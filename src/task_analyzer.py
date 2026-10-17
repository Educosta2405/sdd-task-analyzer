"""TaskAnalyzer: métricas de produtividade de tarefas em memória.

Implementa o contrato de ``specs/task_analyzer_spec.md``: valida a lista de
tarefas e calcula totais, tempo médio de conclusão e taxa de atraso, gerais
e por prioridade. Nenhum dado é persistido.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

logger = logging.getLogger(__name__)

PRIORIDADES = ("baixa", "média", "alta")
STATUS = ("concluída", "pendente", "cancelada")
CONCLUIDA = "concluída"
CAMPOS_OBRIGATORIOS = (
    "id_tarefa", "data_criacao", "prazo", "prioridade", "status",
)


class TaskValidationError(ValueError):
    """Indica que a entrada viola o contrato do TaskAnalyzer."""


class GroupMetrics(TypedDict):
    """Indicadores de um grupo de tarefas (geral ou de uma prioridade).

    Attributes:
        quantidade_tarefas: Total de tarefas do grupo (nome da Fase 1).
        total_tarefas: Total de tarefas do grupo (nome da Fase 2).
        total_concluidas: Tarefas com status ``concluída``.
        total_pendentes: Tarefas com status ``pendente``.
        total_canceladas: Tarefas com status ``cancelada``.
        tempo_medio_conclusao_min: Média de conclusão, em minutos.
        tempo_medio_conclusao_horas: Média de conclusão, em horas.
        taxa_atraso_percentual: Percentual de concluídas após o prazo.
    """

    quantidade_tarefas: int
    total_tarefas: int
    total_concluidas: int
    total_pendentes: int
    total_canceladas: int
    tempo_medio_conclusao_min: float
    tempo_medio_conclusao_horas: float
    taxa_atraso_percentual: float


class TaskMetrics(GroupMetrics):
    """Saída de ``analyze_tasks``: indicadores gerais e por prioridade.

    Attributes:
        indicadores_por_prioridade: Indicadores de cada prioridade
            (``baixa``, ``média`` e ``alta``), sempre presentes.
    """

    indicadores_por_prioridade: dict[str, GroupMetrics]


def analyze_tasks(tasks: list[dict[str, Any]]) -> TaskMetrics:
    """Valida as tarefas e calcula os indicadores gerais e por prioridade.

    Args:
        tasks: Tarefas no formato do contrato, com datas em UTC.

    Returns:
        Totais, tempo médio de conclusão (minutos e horas) e taxa de atraso,
        gerais e de cada prioridade. Grupos sem tarefas concluídas retornam
        ``0.0`` nas médias e na taxa de atraso.

    Raises:
        TaskValidationError: Se a entrada não for uma lista ou se alguma
            tarefa violar o contrato; o lote inteiro é rejeitado.
    """
    try:
        validated = _validate_tasks(tasks)
    except TaskValidationError as error:
        logger.warning("TaskAnalyzer: entrada rejeitada: %s", error)
        raise
    by_priority = {
        priority: _group_metrics(
            [task for task in validated if task["prioridade"] == priority]
        )
        for priority in PRIORIDADES
    }
    logger.info("TaskAnalyzer: %d tarefas analisadas", len(validated))
    return {
        **_group_metrics(validated),
        "indicadores_por_prioridade": by_priority,
    }


def _validate_tasks(tasks: object) -> list[dict[str, Any]]:
    """Valida a lista de tarefas e a unicidade dos identificadores.

    Args:
        tasks: Entrada recebida por ``analyze_tasks``.

    Returns:
        Tarefas validadas, com as datas normalizadas para UTC.

    Raises:
        TaskValidationError: Se a entrada não for lista ou houver tarefa
            inválida.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas")
    seen_ids: set[int] = set()
    return [
        _validate_task(task, position, seen_ids)
        for position, task in enumerate(tasks, start=1)
    ]


def _validate_task(
    task: object, position: int, seen_ids: set[int]
) -> dict[str, Any]:
    """Valida uma tarefa e devolve uma cópia com as datas em UTC.

    Args:
        task: Tarefa recebida na entrada.
        position: Posição da tarefa na lista (base 1), usada nas mensagens.
        seen_ids: Identificadores já validados; recebe o desta tarefa.

    Returns:
        Cópia da tarefa com ``data_criacao``, ``data_inicio``,
        ``data_conclusao`` e ``prazo`` normalizados.

    Raises:
        TaskValidationError: Se a tarefa violar o contrato.
    """
    if not isinstance(task, dict):
        raise TaskValidationError(
            f"Tarefa na posição {position}: deve ser um dicionário"
        )
    label = (
        f"Tarefa {task['id_tarefa']}" if "id_tarefa" in task
        else f"Tarefa na posição {position}"
    )
    _check_fields(task, label, seen_ids)
    created = _require_utc(task["data_criacao"], "data_criacao", label)
    deadline = _require_utc(task["prazo"], "prazo", label)
    started = _optional_utc(task.get("data_inicio"), "data_inicio", label)
    finished = _optional_utc(
        task.get("data_conclusao"), "data_conclusao", label
    )
    _check_chronology(created, started, finished, label)
    _check_status_dates(task["status"], started, finished, label)
    return {
        **task,
        "data_criacao": created,
        "data_inicio": started,
        "data_conclusao": finished,
        "prazo": deadline,
    }


def _check_fields(
    task: dict[str, Any], label: str, seen_ids: set[int]
) -> None:
    """Valida campos obrigatórios, identificador e enumerações.

    Args:
        task: Tarefa recebida na entrada.
        label: Identificação da tarefa nas mensagens de erro.
        seen_ids: Identificadores já validados; recebe o desta tarefa.

    Raises:
        TaskValidationError: Se faltar campo obrigatório, o identificador
            for inválido ou repetido, ou a prioridade/status for inválido.
    """
    missing = [field for field in CAMPOS_OBRIGATORIOS if field not in task]
    if missing:
        raise TaskValidationError(
            f"{label}: campos obrigatórios ausentes: {', '.join(missing)}"
        )
    task_id = task["id_tarefa"]
    if type(task_id) is not int or task_id <= 0:
        raise TaskValidationError(
            f"{label}: id_tarefa deve ser inteiro positivo"
        )
    if task_id in seen_ids:
        raise TaskValidationError(f"{label}: id_tarefa repetido")
    seen_ids.add(task_id)
    if task["prioridade"] not in PRIORIDADES:
        raise TaskValidationError(
            f"{label}: prioridade inválida {task['prioridade']!r}; "
            f"use {', '.join(PRIORIDADES)}"
        )
    if task["status"] not in STATUS:
        raise TaskValidationError(
            f"{label}: status inválido {task['status']!r}; "
            f"use {', '.join(STATUS)}"
        )


def _require_utc(value: object, field: str, label: str) -> datetime:
    """Valida uma data obrigatória em UTC.

    Args:
        value: Valor recebido no campo.
        field: Nome do campo, usado na mensagem de erro.
        label: Identificação da tarefa nas mensagens de erro.

    Returns:
        A data convertida para ``timezone.utc``.

    Raises:
        TaskValidationError: Se o valor não for ``datetime`` com fuso ou se
            o fuso não for UTC.
    """
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise TaskValidationError(
            f"{label}: {field} deve ser datetime com fuso UTC"
        )
    if value.utcoffset() != timedelta(0):
        raise TaskValidationError(f"{label}: {field} deve estar em UTC")
    return value.astimezone(timezone.utc)


def _optional_utc(value: object, field: str, label: str) -> datetime | None:
    """Valida uma data opcional; ``None`` indica ausência.

    Args:
        value: Valor recebido no campo, ou ``None``.
        field: Nome do campo, usado na mensagem de erro.
        label: Identificação da tarefa nas mensagens de erro.

    Returns:
        ``None`` ou a data convertida para ``timezone.utc``.

    Raises:
        TaskValidationError: Se o valor existir e não estiver em UTC.
    """
    return None if value is None else _require_utc(value, field, label)


def _check_chronology(
    created: datetime,
    started: datetime | None,
    finished: datetime | None,
    label: str,
) -> None:
    """Rejeita sequências de datas impossíveis.

    Args:
        created: ``data_criacao`` da tarefa.
        started: ``data_inicio`` da tarefa, se houver.
        finished: ``data_conclusao`` da tarefa, se houver.
        label: Identificação da tarefa nas mensagens de erro.

    Raises:
        TaskValidationError: Se o início ou a conclusão forem anteriores à
            criação, ou se a conclusão for anterior ao início.
    """
    if started is not None and started < created:
        raise TaskValidationError(
            f"{label}: data_inicio anterior à data_criacao"
        )
    if finished is not None and finished < created:
        raise TaskValidationError(
            f"{label}: data_conclusao anterior à data_criacao"
        )
    if started is not None and finished is not None and finished < started:
        raise TaskValidationError(
            f"{label}: data_conclusao anterior à data_inicio"
        )


def _check_status_dates(
    status: str,
    started: datetime | None,
    finished: datetime | None,
    label: str,
) -> None:
    """Valida a coerência entre o status e as datas de execução.

    Args:
        status: Status da tarefa, já validado.
        started: ``data_inicio`` da tarefa, se houver.
        finished: ``data_conclusao`` da tarefa, se houver.
        label: Identificação da tarefa nas mensagens de erro.

    Raises:
        TaskValidationError: Se uma tarefa concluída não tiver início e
            conclusão, ou se uma tarefa não concluída tiver conclusão.
    """
    if status == CONCLUIDA and (started is None or finished is None):
        raise TaskValidationError(
            f"{label}: tarefa concluída requer data_inicio e data_conclusao"
        )
    if status != CONCLUIDA and finished is not None:
        raise TaskValidationError(
            f"{label}: tarefa {status} não pode ter data_conclusao"
        )


def _group_metrics(tasks: list[dict[str, Any]]) -> GroupMetrics:
    """Calcula os indicadores de um grupo de tarefas já validadas.

    Apenas tarefas concluídas entram na média e na taxa de atraso; uma
    tarefa concluída exatamente no prazo não está atrasada.

    Args:
        tasks: Tarefas validadas do grupo; pode ser vazia.

    Returns:
        Indicadores do grupo, com tempos e percentuais em duas casas.
    """
    completed = [task for task in tasks if task["status"] == CONCLUIDA]
    total_minutes = sum(
        (task["data_conclusao"] - task["data_inicio"]).total_seconds() / 60
        for task in completed
    )
    late = sum(task["data_conclusao"] > task["prazo"] for task in completed)
    mean_minutes = _safe_ratio(total_minutes, len(completed))
    return {
        "quantidade_tarefas": len(tasks),
        "total_tarefas": len(tasks),
        "total_concluidas": len(completed),
        "total_pendentes": sum(task["status"] == "pendente" for task in tasks),
        "total_canceladas": sum(
            task["status"] == "cancelada" for task in tasks
        ),
        "tempo_medio_conclusao_min": round(mean_minutes, 2),
        "tempo_medio_conclusao_horas": round(mean_minutes / 60, 2),
        "taxa_atraso_percentual": round(
            100 * _safe_ratio(late, len(completed)), 2
        ),
    }


def _safe_ratio(numerator: float, denominator: int) -> float:
    """Divide sem risco de divisão por zero.

    Args:
        numerator: Dividendo.
        denominator: Divisor; quando zero, o resultado é ``0.0``.

    Returns:
        ``numerator / denominator``, ou ``0.0`` se ``denominator`` for zero.
    """
    if denominator == 0:
        return 0.0
    return numerator / denominator
