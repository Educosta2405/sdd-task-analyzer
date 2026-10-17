# Contrato SDD — TaskAnalyzer (reconstrução fundamentada)

**Situação:** Fase 1 não entregue; reconstruído a partir dos enunciados da Fase 1 (especialmente p. 8) e Fase 2 (pp. 2–4). Não é cópia de uma especificação produzida anteriormente.

## Objetivo
Analisar tarefas em memória, agrupando indicadores gerais e por prioridade, calculando tempo médio de conclusão e taxa de atraso; emitir erro específico para inconsistência de dados.

## Interface
`analyze_tasks(tasks: list[dict[str, Any]]) -> TaskMetrics`; exceção pública `TaskValidationError`.

### Campos de entrada por tarefa
| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `id_tarefa` | int | Sim | Positivo e único no conjunto |
| `data_criacao` | datetime | Sim | UTC |
| `data_inicio` | datetime / None | Não | UTC quando existente |
| `data_conclusao` | datetime / None | Não | UTC quando existente |
| `prazo` | datetime | Sim | UTC |
| `prioridade` | str | Sim | `baixa`, `média`, `alta` |
| `status` | str | Sim | `concluída`, `pendente`, `cancelada` |

### Saída
Dicionário com `quantidade_tarefas`, `total_tarefas`, `total_concluidas`, `total_pendentes`, `total_canceladas`, `tempo_medio_conclusao_min`, `tempo_medio_conclusao_horas`, `taxa_atraso_percentual`, `indicadores_por_prioridade`. Cada prioridade recebe os mesmos indicadores numéricos (sem subagrupamentos).

## Regras
1. Apenas concluídas entram na média e no numerador/denominador da taxa de atraso. Pendentes e canceladas entram nas contagens.
2. Duração = `data_conclusao - data_inicio`; minutos para o contrato Fase 1; horas adicionais para a Fase 2.
3. Atrasada = tarefa concluída com `data_conclusao > prazo` (igual ao prazo não é atraso).
4. Média = soma das durações / número de concluídas; atraso = atrasadas / concluídas * 100.
5. Se não existem concluídas, médias e taxa de atraso são `0.0`.
6. Valores de tempo e porcentagem arredondados para duas casas decimais.
7. Cronologia impossível (`data_inicio < data_criacao`, `data_conclusao < data_criacao` ou `data_conclusao < data_inicio`) gera `TaskValidationError`.
8. Todos os datetimes devem ter fuso UTC.
9. `status = concluída` requer início e conclusão; status não concluído não pode ter data de conclusão.
10. IDs repetidos, status/prioridades inválidos e campos obrigatórios faltantes geram `TaskValidationError`.

## Duas divergências/documentação de decisões
- **Unidade:** a Fase 1 cita `tempo_medio_conclusao_min`; a Fase 2 exige `tempo_medio_conclusao_horas`. A saída inclui **ambas**, sem substituir a unidade original.
- **Cenário 2:** a Fase 2 menciona `data_conclusao < data_criacao`; a Fase 1 também descreve conclusão anterior ao início. Testamos os dois.
- **Decisões inferidas, NÃO explicitadas:** exigir início/conclusão em status concluída, rejeitar conclusão em status pendente/cancelada e tratar IDs repetidos como erro; interpretações prudentes do contrato. Ajustar se o docente fornecer esclarecimento.

## Cenários de aceite (Dado / Quando / Então)
**Cenário 1 (sucesso).** Dado um conjunto de tarefas válidas de múltiplas prioridades, com concluídas, pendentes e canceladas, quando executado `analyze_tasks`, então totais, médias (geral/por prioridade) e atrasos são calculados corretamente.

**Cenário 2 (erro).** Dada tarefa com conclusão anterior à criação ou início, quando executado `analyze_tasks`, então lança `TaskValidationError` com mensagem clara.

**Bordas.** Dada lista vazia ou apenas pendentes, quando executado `analyze_tasks`, então médias e percentuais são `0.0`, sem divisão por zero.

## Planejamento de validação
`tests/test_harness.py` cobre os cenários, limites, entradas inválidas e arredondamentos. Execução deve ocorrer com Python 3.11+ e `python -m pytest -q`. Evidências do terminal/GitHub devem ser capturadas no ambiente real do estudante.
