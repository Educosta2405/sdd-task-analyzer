"""Test Harness: cenários de aceite e testes de fronteira da Fase 2."""
from datetime import datetime, timedelta, timezone
import pytest
from src.task_analyzer import TaskValidationError, analyze_tasks


def dt(day: int, hour: int = 0) -> datetime:
    return datetime(2026, 10, day, hour, tzinfo=timezone.utc)


def task(task_id: int, priority: str, status: str, minutes: int | None, late: bool = False) -> dict:
    start = dt(1, 8)
    conclusion = start + timedelta(minutes=minutes) if minutes is not None else None
    return {
        "id_tarefa": task_id, "data_criacao": dt(1), "data_inicio": start if minutes is not None else None,
        "data_conclusao": conclusion, "prazo": (conclusion - timedelta(minutes=1) if late else dt(3)),
        "prioridade": priority, "status": status,
    }


def test_cenario_1_metricas_gerais_e_prioridades() -> None:
    data = [task(1,"alta","concluída",120,True),task(2,"alta","concluída",60),
            task(3,"média","concluída",30),task(4,"baixa","pendente",None),
            task(5,"média","cancelada",None)]
    result = analyze_tasks(data)
    assert (result["total_tarefas"],result["total_concluidas"],result["total_pendentes"],result["total_canceladas"]) == (5,3,1,1)
    assert result["quantidade_tarefas"] == 5
    assert result["tempo_medio_conclusao_min"] == 70.0
    assert result["tempo_medio_conclusao_horas"] == 1.17
    assert result["taxa_atraso_percentual"] == 33.33
    assert result["indicadores_por_prioridade"]["alta"]["tempo_medio_conclusao_min"] == 90.0
    assert result["indicadores_por_prioridade"]["alta"]["tempo_medio_conclusao_horas"] == 1.5
    assert result["indicadores_por_prioridade"]["alta"]["taxa_atraso_percentual"] == 50.0
    assert result["indicadores_por_prioridade"]["baixa"]["quantidade_tarefas"] == 1


def test_cenario_2_conclusao_antes_da_criacao() -> None:
    invalid = task(1,"alta","concluída",60)
    invalid["data_conclusao"] = dt(1) - timedelta(minutes=1)
    with pytest.raises(TaskValidationError, match="data_conclusao"):
        analyze_tasks([invalid])


def test_cenario_2_conclusao_antes_do_inicio() -> None:
    invalid = task(1,"alta","concluída",60)
    invalid["data_conclusao"] = dt(1,7)
    with pytest.raises(TaskValidationError):
        analyze_tasks([invalid])


def test_lista_vazia() -> None:
    result = analyze_tasks([])
    assert result["tempo_medio_conclusao_min"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0
    assert all(value["tempo_medio_conclusao_horas"] == 0.0 for value in result["indicadores_por_prioridade"].values())


def test_apenas_pendentes() -> None:
    result = analyze_tasks([task(1,"alta","pendente",None),task(2,"baixa","pendente",None)])
    assert result["total_pendentes"] == 2
    assert result["tempo_medio_conclusao_horas"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0


@pytest.mark.parametrize("key,value",[("id_tarefa",0),("prioridade","urgente"),("status","em andamento"),("prazo",None)])
def test_campos_invalidos(key: str, value: object) -> None:
    invalid = task(1,"alta","concluída",60)
    invalid[key] = value
    with pytest.raises(TaskValidationError):
        analyze_tasks([invalid])


def test_identificador_duplicado() -> None:
    with pytest.raises(TaskValidationError):
        analyze_tasks([task(1,"alta","pendente",None),task(1,"alta","pendente",None)])


def test_timezone_obrigatorio_utc() -> None:
    invalid = task(1,"alta","concluída",60)
    invalid["data_criacao"] = datetime(2026,10,1)
    with pytest.raises(TaskValidationError):
        analyze_tasks([invalid])


def test_concluida_sem_datas() -> None:
    with pytest.raises(TaskValidationError):
        analyze_tasks([task(1,"alta","concluída",None)])


def test_atraso_no_prazo_nao_conta() -> None:
    item = task(1,"baixa","concluída",60)
    item["prazo"] = item["data_conclusao"]
    assert analyze_tasks([item])["taxa_atraso_percentual"] == 0.0


def test_tipo_entrada_errado() -> None:
    with pytest.raises(TaskValidationError):
        analyze_tasks(None)  # type: ignore[arg-type]
