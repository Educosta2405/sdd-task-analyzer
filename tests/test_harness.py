"""Test Harness do TaskAnalyzer (Fase 2).

Traduz os cenários de aceite de ``specs/task_analyzer_spec.md`` em testes
pytest: Cenário 1 (sucesso), Cenário 2 (datas inconsistentes), casos de
borda e validações do contrato de entrada.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from src.task_analyzer import (
    GroupMetrics,
    TaskValidationError,
    analyze_tasks,
)

CRIACAO = datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc)
INICIO = datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)
PRAZO = datetime(2026, 10, 3, 0, 0, tzinfo=timezone.utc)


def make_task(
    task_id: int,
    prioridade: str,
    status: str,
    duracao_min: int | None = None,
    atrasada: bool = False,
) -> dict[str, Any]:
    """Cria uma tarefa válida no formato do contrato.

    Args:
        task_id: Valor de ``id_tarefa``.
        prioridade: ``baixa``, ``média`` ou ``alta``.
        status: ``concluída``, ``pendente`` ou ``cancelada``.
        duracao_min: Minutos entre início e conclusão; ``None`` cria a
            tarefa sem início nem conclusão.
        atrasada: Se ``True``, o prazo vence 1 minuto antes da conclusão.

    Returns:
        Dicionário com os campos de entrada do contrato.
    """
    conclusao = (
        None if duracao_min is None
        else INICIO + timedelta(minutes=duracao_min)
    )
    prazo = (
        conclusao - timedelta(minutes=1)
        if atrasada and conclusao is not None
        else PRAZO
    )
    return {
        "id_tarefa": task_id,
        "data_criacao": CRIACAO,
        "data_inicio": None if conclusao is None else INICIO,
        "data_conclusao": conclusao,
        "prazo": prazo,
        "prioridade": prioridade,
        "status": status,
    }


def assert_sem_concluidas(grupo: GroupMetrics) -> None:
    """Confere que médias e taxa de atraso valem 0.0 (float).

    Args:
        grupo: Indicadores gerais ou de uma prioridade.
    """
    valores = (
        grupo["tempo_medio_conclusao_min"],
        grupo["tempo_medio_conclusao_horas"],
        grupo["taxa_atraso_percentual"],
    )
    assert valores == (0.0, 0.0, 0.0)
    assert all(isinstance(valor, float) for valor in valores)


# Cenário 1 — sucesso


def test_cenario_1_metricas_gerais_e_prioridades() -> None:
    """Cenário 1: totais, médias e atraso corretos, gerais e por prioridade."""
    # Dado: 3 concluídas (120, 60 e 30 min; a de 120 min atrasada),
    # 1 pendente e 1 cancelada.
    tarefas = [
        make_task(1, "alta", "concluída", duracao_min=120, atrasada=True),
        make_task(2, "alta", "concluída", duracao_min=60),
        make_task(3, "média", "concluída", duracao_min=30),
        make_task(4, "baixa", "pendente"),
        make_task(5, "média", "cancelada"),
    ]

    # Quando
    resultado = analyze_tasks(tarefas)

    # Então: média geral (120 + 60 + 30) / 3 = 70 min = 1.17 h;
    # atraso: 1 de 3 concluídas = 33.33%.
    assert resultado == {
        "quantidade_tarefas": 5,
        "total_tarefas": 5,
        "total_concluidas": 3,
        "total_pendentes": 1,
        "total_canceladas": 1,
        "tempo_medio_conclusao_min": 70.0,
        "tempo_medio_conclusao_horas": 1.17,
        "taxa_atraso_percentual": 33.33,
        "indicadores_por_prioridade": {
            # Sem concluídas: 0.0, sem divisão por zero.
            "baixa": {
                "quantidade_tarefas": 1,
                "total_tarefas": 1,
                "total_concluidas": 0,
                "total_pendentes": 1,
                "total_canceladas": 0,
                "tempo_medio_conclusao_min": 0.0,
                "tempo_medio_conclusao_horas": 0.0,
                "taxa_atraso_percentual": 0.0,
            },
            # 30 min = 0.5 h; a cancelada conta no total, não na média.
            "média": {
                "quantidade_tarefas": 2,
                "total_tarefas": 2,
                "total_concluidas": 1,
                "total_pendentes": 0,
                "total_canceladas": 1,
                "tempo_medio_conclusao_min": 30.0,
                "tempo_medio_conclusao_horas": 0.5,
                "taxa_atraso_percentual": 0.0,
            },
            # (120 + 60) / 2 = 90 min = 1.5 h; 1 de 2 atrasada = 50%.
            "alta": {
                "quantidade_tarefas": 2,
                "total_tarefas": 2,
                "total_concluidas": 2,
                "total_pendentes": 0,
                "total_canceladas": 0,
                "tempo_medio_conclusao_min": 90.0,
                "tempo_medio_conclusao_horas": 1.5,
                "taxa_atraso_percentual": 50.0,
            },
        },
    }


def test_atraso_no_prazo_nao_conta() -> None:
    """Regra 3: conclusão exatamente no prazo não é atraso."""
    tarefa = make_task(1, "baixa", "concluída", duracao_min=60)
    tarefa["prazo"] = tarefa["data_conclusao"]

    assert analyze_tasks([tarefa])["taxa_atraso_percentual"] == 0.0


# Cenário 2 — datas inconsistentes


def test_cenario_2_conclusao_antes_da_criacao() -> None:
    """Cenário 2: data_conclusao < data_criacao gera TaskValidationError."""
    tarefa = make_task(1, "alta", "concluída", duracao_min=60)
    tarefa["data_conclusao"] = CRIACAO - timedelta(minutes=1)

    with pytest.raises(
        TaskValidationError,
        match="Tarefa 1: data_conclusao anterior à data_criacao",
    ):
        analyze_tasks([tarefa])


def test_cenario_2_conclusao_antes_do_inicio() -> None:
    """Cenário 2: data_conclusao < data_inicio gera TaskValidationError."""
    tarefa = make_task(1, "alta", "concluída", duracao_min=60)
    tarefa["data_conclusao"] = INICIO - timedelta(minutes=1)

    with pytest.raises(
        TaskValidationError,
        match="Tarefa 1: data_conclusao anterior à data_inicio",
    ):
        analyze_tasks([tarefa])


def test_cenario_2_inicio_antes_da_criacao() -> None:
    """Regra 7: data_inicio < data_criacao gera TaskValidationError."""
    tarefa = make_task(1, "alta", "pendente")
    tarefa["data_inicio"] = CRIACAO - timedelta(minutes=1)

    with pytest.raises(
        TaskValidationError,
        match="Tarefa 1: data_inicio anterior à data_criacao",
    ):
        analyze_tasks([tarefa])


def test_cenario_2_lote_com_tarefa_invalida_e_rejeitado() -> None:
    """Regra 12: uma tarefa inconsistente rejeita o lote inteiro."""
    valida = make_task(1, "alta", "concluída", duracao_min=60)
    invalida = make_task(2, "baixa", "concluída", duracao_min=60)
    invalida["data_conclusao"] = CRIACAO - timedelta(days=1)

    with pytest.raises(TaskValidationError, match="Tarefa 2:"):
        analyze_tasks([valida, invalida])


# Casos de borda — sem tarefas concluídas


def test_lista_vazia() -> None:
    """Borda: lista vazia retorna zeros, sem divisão por zero."""
    resultado = analyze_tasks([])

    assert resultado["total_tarefas"] == 0
    assert set(resultado["indicadores_por_prioridade"]) == {
        "baixa", "média", "alta",
    }
    assert_sem_concluidas(resultado)
    for grupo in resultado["indicadores_por_prioridade"].values():
        assert grupo["total_tarefas"] == 0
        assert_sem_concluidas(grupo)


def test_apenas_pendentes() -> None:
    """Borda: apenas pendentes retorna 0.0 nas médias e na taxa."""
    resultado = analyze_tasks([
        make_task(1, "alta", "pendente"),
        make_task(2, "baixa", "pendente"),
    ])

    assert resultado["total_tarefas"] == 2
    assert resultado["total_pendentes"] == 2
    assert resultado["total_concluidas"] == 0
    assert_sem_concluidas(resultado)
    for grupo in resultado["indicadores_por_prioridade"].values():
        assert_sem_concluidas(grupo)


# Validações do contrato de entrada


@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("id_tarefa", 0, "id_tarefa deve ser inteiro positivo"),
        ("id_tarefa", "1", "id_tarefa deve ser inteiro positivo"),
        ("prioridade", "urgente", "prioridade inválida"),
        ("status", "em andamento", "status inválido"),
        ("prazo", None, "prazo deve ser datetime com fuso UTC"),
    ],
    ids=[
        "id-zero", "id-texto", "prioridade-invalida", "status-invalido",
        "prazo-nulo",
    ],
)
def test_campos_invalidos(campo: str, valor: object, mensagem: str) -> None:
    """Regra 10: valores fora do contrato geram TaskValidationError."""
    tarefa = make_task(1, "alta", "concluída", duracao_min=60)
    tarefa[campo] = valor

    with pytest.raises(TaskValidationError, match=mensagem):
        analyze_tasks([tarefa])


def test_campo_obrigatorio_ausente() -> None:
    """Regra 10: campo obrigatório ausente gera TaskValidationError."""
    tarefa = make_task(1, "alta", "pendente")
    del tarefa["prazo"]

    with pytest.raises(
        TaskValidationError,
        match="Tarefa 1: campos obrigatórios ausentes: prazo",
    ):
        analyze_tasks([tarefa])


def test_identificador_duplicado() -> None:
    """Regra 10: id_tarefa repetido gera TaskValidationError."""
    tarefas = [make_task(1, "alta", "pendente"),
               make_task(1, "baixa", "pendente")]

    with pytest.raises(
        TaskValidationError, match="Tarefa 1: id_tarefa repetido"
    ):
        analyze_tasks(tarefas)


@pytest.mark.parametrize(
    ("data", "mensagem"),
    [
        (datetime(2026, 10, 1), "deve ser datetime com fuso UTC"),
        (
            datetime(2026, 10, 1, tzinfo=timezone(timedelta(hours=-3))),
            "deve estar em UTC",
        ),
    ],
    ids=["sem-fuso", "fuso-brasilia"],
)
def test_timezone_obrigatorio_utc(data: datetime, mensagem: str) -> None:
    """Regra 8: datas sem fuso ou fora de UTC geram TaskValidationError."""
    tarefa = make_task(1, "alta", "concluída", duracao_min=60)
    tarefa["data_criacao"] = data

    with pytest.raises(TaskValidationError, match=f"data_criacao {mensagem}"):
        analyze_tasks([tarefa])


def test_concluida_sem_datas() -> None:
    """Regra 9: tarefa concluída exige data_inicio e data_conclusao."""
    with pytest.raises(
        TaskValidationError,
        match="concluída requer data_inicio e data_conclusao",
    ):
        analyze_tasks([make_task(1, "alta", "concluída")])


def test_pendente_com_data_conclusao() -> None:
    """Regra 9: tarefa não concluída não pode ter data_conclusao."""
    tarefa = make_task(1, "alta", "concluída", duracao_min=60)
    tarefa["status"] = "pendente"

    with pytest.raises(
        TaskValidationError,
        match="tarefa pendente não pode ter data_conclusao",
    ):
        analyze_tasks([tarefa])


def test_tipo_entrada_errado() -> None:
    """Interface: entrada que não é lista gera TaskValidationError."""
    with pytest.raises(TaskValidationError, match="lista de tarefas"):
        analyze_tasks(None)  # type: ignore[arg-type]


def test_tarefa_nao_dicionario() -> None:
    """Interface: item que não é dicionário gera TaskValidationError."""
    with pytest.raises(
        TaskValidationError, match="posição 1: deve ser um dicionário"
    ):
        analyze_tasks(["tarefa"])  # type: ignore[list-item]
