# Contrato SDD — TaskAnalyzer

**Situação:** a Fase 1 não foi entregue. Este contrato foi reconstruído a partir dos enunciados da Fase 1 (pp. 2, 3 e 8) e da Fase 2 (seções 3.2 e 3.3); não é cópia de uma especificação produzida anteriormente.

## Objetivo
Analisar uma lista de tarefas em memória e calcular indicadores de produtividade — totais, tempo médio de conclusão e taxa de atraso —, gerais e por prioridade. Entradas que violem o contrato geram `TaskValidationError`. Nenhum dado é persistido.

## Interface
Módulo `src/task_analyzer.py`:

```python
def analyze_tasks(tasks: list[dict[str, Any]]) -> TaskMetrics: ...

class TaskValidationError(ValueError): ...
```

### Entrada (cada tarefa)
| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `id_tarefa` | int | Sim | Inteiro positivo e único no conjunto |
| `data_criacao` | datetime | Sim | UTC |
| `data_inicio` | datetime ou None | Não | UTC quando existente |
| `data_conclusao` | datetime ou None | Não | UTC quando existente |
| `prazo` | datetime | Sim | UTC |
| `prioridade` | str | Sim | `baixa`, `média` ou `alta` |
| `status` | str | Sim | `concluída`, `pendente` ou `cancelada` |

Campos extras (ex.: `titulo`) são ignorados.

### Saída (`TaskMetrics`)
| Campo | Tipo | Descrição | Origem |
|---|---|---|---|
| `total_tarefas` | int | Tarefas analisadas | Fase 2 |
| `quantidade_tarefas` | int | Mesmo valor de `total_tarefas` | Fase 1 |
| `total_concluidas` | int | Tarefas `concluída` | Fase 2 |
| `total_pendentes` | int | Tarefas `pendente` | Fase 2 |
| `total_canceladas` | int | Tarefas `cancelada` | Decisão: fecha a soma dos totais |
| `tempo_medio_conclusao_min` | float | Média de `data_conclusao - data_inicio`, em minutos | Fase 1 |
| `tempo_medio_conclusao_horas` | float | A mesma média, em horas | Fase 2 |
| `taxa_atraso_percentual` | float | % de concluídas com `data_conclusao > prazo` | Fases 1 e 2 |
| `indicadores_por_prioridade` | dict | Chaves `baixa`, `média` e `alta`, sempre presentes, cada uma com os oito campos acima | Fase 1 |

## Regras de negócio
1. Apenas tarefas concluídas entram na média e na taxa de atraso (numerador e denominador). Pendentes e canceladas entram só nas contagens.
2. Duração = `data_conclusao - data_inicio`, expressa em minutos e em horas.
3. Atrasada = tarefa concluída com `data_conclusao > prazo`; conclusão igual ao prazo não é atraso.
4. Média = soma das durações / número de concluídas; atraso = atrasadas / concluídas × 100.
5. Sem tarefas concluídas, médias e taxa de atraso valem `0.0`, sem exceção (prevenção de divisão por zero).
6. Tempos e percentuais são arredondados para duas casas decimais.
7. Cronologia impossível gera `TaskValidationError`: `data_inicio < data_criacao`, `data_conclusao < data_criacao` ou `data_conclusao < data_inicio`.
8. Todas as datas devem ser `datetime` com fuso UTC; datas sem fuso ou em outro fuso são rejeitadas.
9. Status `concluída` exige `data_inicio` e `data_conclusao`; status não concluído não pode ter `data_conclusao`.
10. Campo obrigatório ausente, `id_tarefa` inválido ou repetido e prioridade ou status fora da lista geram `TaskValidationError`.
11. Mensagens de erro identificam a tarefa e o motivo, no formato `Tarefa <id>: <motivo>`.
12. Uma tarefa inválida rejeita o lote inteiro; não há resultado parcial.

## Divergências entre os enunciados e decisões registradas
| Tema | Fase 1 | Fase 2 | Decisão |
|---|---|---|---|
| Unidade do tempo médio | `tempo_medio_conclusao_min` | `tempo_medio_conclusao_horas` | Retornar ambos |
| Nome do total | `quantidade_tarefas` | `total_tarefas` | Retornar ambos, com o mesmo valor |
| Datas inconsistentes | Regras (p. 8): ignorar a tarefa; Cenário 2: lançar exceção | Lançar `TaskValidationError` | Lançar exceção e rejeitar o lote (regras 7 e 12) |
| Sem tarefas concluídas | Cenário 2 cita divisão por zero entre os casos de exceção | Retornar `0.0` sem exceção | Retornar `0.0` (regra 5) |
| Cronologia testada | Conclusão antes do início | Conclusão antes da criação | Validar e testar as três comparações (regra 7) |

Em todos os conflitos prevalece a Fase 2, que é a entrega avaliada.

**Decisões inferidas** (não explícitas nos enunciados): exigir início e conclusão em tarefas concluídas, rejeitar conclusão em tarefas pendentes ou canceladas, rejeitar IDs repetidos, rejeitar datas sem fuso e incluir `total_canceladas`. Devem ser revistas se o docente indicar outro entendimento.

## Cenários de aceite (Dado / Quando / Então)
**Cenário 1 — sucesso.** Dado o conjunto abaixo (criação 01/10 00:00 UTC, início 08:00 UTC), quando `analyze_tasks` é executado, então retorna:

| id | Prioridade | Status | Duração | Atrasada |
|---|---|---|---|---|
| 1 | alta | concluída | 120 min | Sim |
| 2 | alta | concluída | 60 min | Não |
| 3 | média | concluída | 30 min | Não |
| 4 | baixa | pendente | — | — |
| 5 | média | cancelada | — | — |

| Grupo | Total | Concl. | Pend. | Canc. | Média (min) | Média (h) | Atraso (%) |
|---|---|---|---|---|---|---|---|
| Geral | 5 | 3 | 1 | 1 | 70.0 | 1.17 | 33.33 |
| alta | 2 | 2 | 0 | 0 | 90.0 | 1.5 | 50.0 |
| média | 2 | 1 | 0 | 1 | 30.0 | 0.5 | 0.0 |
| baixa | 1 | 0 | 1 | 0 | 0.0 | 0.0 | 0.0 |

**Cenário 2 — erro.** Dada uma tarefa com `data_conclusao` anterior à `data_criacao` (ou ao início), quando `analyze_tasks` é executado, então lança `TaskValidationError` com mensagem que identifica a tarefa e a inconsistência.

**Casos de borda.** Dada uma lista vazia ou apenas com tarefas pendentes, quando `analyze_tasks` é executado, então médias e taxa de atraso são `0.0`, no geral e em cada prioridade, sem divisão por zero.

## Rastreabilidade (regra → teste em `tests/test_harness.py`)
| Regra / cenário | Testes |
|---|---|
| Cenário 1; regras 1–4 e 6 | `test_cenario_1_metricas_gerais_e_prioridades` |
| Regra 3 (no prazo) | `test_atraso_no_prazo_nao_conta` |
| Cenário 2; regras 7 e 11 | `test_cenario_2_conclusao_antes_da_criacao`, `test_cenario_2_conclusao_antes_do_inicio`, `test_cenario_2_inicio_antes_da_criacao` |
| Regra 12 | `test_cenario_2_lote_com_tarefa_invalida_e_rejeitado` |
| Bordas; regra 5 | `test_lista_vazia`, `test_apenas_pendentes` |
| Regra 8 | `test_timezone_obrigatorio_utc` |
| Regra 9 | `test_concluida_sem_datas`, `test_pendente_com_data_conclusao` |
| Regra 10 | `test_campos_invalidos`, `test_campo_obrigatorio_ausente`, `test_identificador_duplicado` |
| Interface | `test_tipo_entrada_errado`, `test_tarefa_nao_dicionario` |

## Planejamento de validação
Executar `pytest -v` com Python 3.11+ na raiz do repositório. Evidências do terminal e do GitHub devem ser capturadas no ambiente real do estudante.
