"""TaskAnalyzer: métricas de tarefas em memória, baseadas no SDD reconstruído."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, TypedDict

logger = logging.getLogger(__name__)
PRIORIDADES = ("baixa", "média", "alta")
STATUS = ("concluída", "pendente", "cancelada")


class TaskValidationError(ValueError):
    """Indica violação do contrato de entrada TaskAnalyzer."""


class TaskMetrics(TypedDict):
    quantidade_tarefas: int
    total_tarefas: int
    total_concluidas: int
    total_pendentes: int
    total_canceladas: int
    tempo_medio_conclusao_min: float
    tempo_medio_conclusao_horas: float
    taxa_atraso_percentual: float
    indicadores_por_prioridade: dict[str, dict[str, int | float]]


def _require_utc(value: Any, field: str) -> datetime:
    """Aceita datetime com timezone UTC, rejeitando datas ingênuas."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TaskValidationError(f"{field}: esperado datetime com fuso UTC")
    if value.utcoffset().total_seconds() != 0:
        raise TaskValidationError(f"{field}: fuso deve ser UTC")
    return value.astimezone(timezone.utc)


def _validated(task: Any, seen: set[int]) -> dict[str, Any]:
    """Valida o contrato de campos, enumerações, unicidade e cronologia."""
    if not isinstance(task, dict):
        raise TaskValidationError("Cada tarefa deve ser um dicionário")
    mandatory = ("id_tarefa", "data_criacao", "prazo", "prioridade", "status")
    for key in mandatory:
        if key not in task:
            raise TaskValidationError(f"Campo obrigatório ausente: {key}")
    task_id = task["id_tarefa"]
    if type(task_id) is not int or task_id <= 0 or task_id in seen:
        raise TaskValidationError("id_tarefa deve ser inteiro positivo e único")
    seen.add(task_id)
    if task["prioridade"] not in PRIORIDADES:
        raise TaskValidationError("prioridade inválida")
    if task["status"] not in STATUS:
        raise TaskValidationError("status inválido")
    dates: dict[str, datetime | None] = {}
    for field in ("data_criacao", "data_inicio", "data_conclusao", "prazo"):
        value = task.get(field)
        dates[field] = None if value is None and field in ("data_inicio", "data_conclusao") else _require_utc(value, field)
    if dates["data_inicio"] is not None and dates["data_inicio"] < dates["data_criacao"]:
        raise TaskValidationError("data_inicio anterior à data_criacao")
    if dates["data_conclusao"] is not None:
        if dates["data_conclusao"] < dates["data_criacao"]:
            raise TaskValidationError("data_conclusao anterior à data_criacao")
        if dates["data_inicio"] is not None and dates["data_conclusao"] < dates["data_inicio"]:
            raise TaskValidationError("data_conclusao anterior à data_inicio")
    if task["status"] == "concluída" and (dates["data_inicio"] is None or dates["data_conclusao"] is None):
        raise TaskValidationError("Tarefa concluída requer data_inicio e data_conclusao")
    if task["status"] != "concluída" and dates["data_conclusao"] is not None:
        raise TaskValidationError("Tarefa não concluída não pode ter data_conclusao")
    return {**task, **dates}


def _metric(tasks: list[dict[str, Any]]) -> dict[str, int | float]:
    """Produz métricas agregadas com denominadores seguros."""
    completed = [t for t in tasks if t["status"] == "concluída"]
    overdue = sum(t["data_conclusao"] > t["prazo"] for t in completed)
    minutes = sum((t["data_conclusao"] - t["data_inicio"]).total_seconds() / 60 for t in completed)
    mean_min = minutes / len(completed) if completed else 0.0
    return {
        "quantidade_tarefas": len(tasks),
        "total_tarefas": len(tasks),
        "total_concluidas": len(completed),
        "total_pendentes": sum(t["status"] == "pendente" for t in tasks),
        "total_canceladas": sum(t["status"] == "cancelada" for t in tasks),
        "tempo_medio_conclusao_min": round(mean_min, 2),
        "tempo_medio_conclusao_horas": round(mean_min / 60, 2),
        "taxa_atraso_percentual": round(100 * overdue / len(completed), 2) if completed else 0.0,
    }


def analyze_tasks(tasks: list[dict[str, Any]]) -> TaskMetrics:
    """Analisa tarefas e retorna indicadores gerais e por prioridade.

    Contrato reconstruído: recebe lista de dicionários com datetimes UTC.
    Atraso considera apenas tarefas concluídas; médias usam início -> conclusão.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas")
    seen: set[int] = set()
    validated = [_validated(task, seen) for task in tasks]
    overall = _metric(validated)
    by_priority = {
        priority: _metric([task for task in validated if task["prioridade"] == priority])
        for priority in PRIORIDADES
    }
    logger.info("TaskAnalyzer: %s tarefas analisadas", len(tasks))
    return {**overall, "indicadores_por_prioridade": by_priority}  # type: ignore[return-value]
