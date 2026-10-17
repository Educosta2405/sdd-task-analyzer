# Roteiro prático de entrega (Fase 2)

1. Revisar o contrato reconstruído e as decisões inferidas; homologar comportamento.
2. Conferir o repositório público `sdd-task-analyzer`.
3. Inspecionar os commits de documentação na `main` e a branch `feature/task-analyzer-impl`.
4. Revisar implementação e testes; executar `python -m pytest -q` no ambiente local.
5. Revisar o Pull Request da branch para `main`, documentando o resultado da homologação humana; fazer merge após aprovação.
6. Tirar capturas REAIS do pytest no terminal, da árvore do GitHub e do PR.
7. Gravar vídeo **horizontal** de cerca de **5 minutos**, câmera e áudio visíveis, demonstrando árvore, pytest, PR, regras e revisão; publicar no YouTube como Não Listado ou Público.
8. Atualizar o PDF com URLs reais, imagens autênticas e explicação do uso da IA; enviar no Sala Online.

## Prompt sugerido ao Claude Code

Leia `CONTEXT_RULES.md` e `specs/task_analyzer_spec.md` integralmente antes de agir. Faça uma auditoria independente da aderência de `src/task_analyzer.py` e `tests/test_harness.py` aos dois enunciados do Bootcamp III. Identifique divergências reais, proponha correções proporcionais e implemente com autonomia onde não houver risco. Execute os testes e reporte resultados verdadeiros. Em seguida, ajude a revisar o PR documentado no GitHub do estudante, preservando decisões humanas. Não invente evidências nem trate a Fase 1 como já entregue. Reserve para a pessoa responsável as decisões de publicação e a gravação do vídeo.

## Modelo de apresentação (aproximadamente 5 minutos)
- 0:00–0:45 — apresentação e objetivo SDD / IA Harness
- 0:45–1:40 — especificação reconstruída, entradas, métricas e regras
- 1:40–2:40 — implementação e tratamento de inconsistências
- 2:40–3:35 — execução real do pytest e explicação dos cenários
- 3:35–4:25 — histórico, branches e Pull Request
- 4:25–5:00 — revisão humana, restrições da IA e conclusão
