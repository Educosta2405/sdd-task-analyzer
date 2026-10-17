# TaskAnalyzer — Bootcamp III

Projeto acadêmico de análise de tarefas e produtividade em Python 3.11+, desenvolvido com Spec-Driven Development (SDD): o código de `src/` foi gerado com assistente de IA a partir da especificação e das regras de contexto, validado por testes pytest e homologado por revisão humana via Pull Request.

## Status do build
- Testes: **21 passed** em execução local (Python 3.14.5, pytest 9.1.1, 17/10/2026).
- Integração contínua com GitHub Actions: prevista para a Fase 3.

## Estrutura
```
sdd-task-analyzer/
├── README.md                  # Visão geral e instruções de execução
├── CONTEXT_RULES.md           # Regras de governança fornecidas à IA
├── .gitignore                 # Arquivos ignorados pelo Git
├── requirements.txt           # Dependências autorizadas (pytest)
├── pytest.ini                 # Configuração para rodar `pytest` na raiz
├── specs/
│   └── task_analyzer_spec.md  # Contrato SDD e cenários de aceite
├── tests/
│   └── test_harness.py        # Test Harness (cenários 1 e 2 e bordas)
└── src/
    ├── __init__.py
    └── task_analyzer.py       # analyze_tasks e TaskValidationError
```

## Como executar
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
python -m pip install -r requirements.txt
pytest -v
```

## Exemplo de uso
```python
from datetime import datetime, timezone

from src.task_analyzer import analyze_tasks

utc = timezone.utc
tarefas = [
    {
        "id_tarefa": 1,
        "data_criacao": datetime(2026, 10, 1, 9, 0, tzinfo=utc),
        "data_inicio": datetime(2026, 10, 1, 10, 0, tzinfo=utc),
        "data_conclusao": datetime(2026, 10, 1, 11, 30, tzinfo=utc),
        "prazo": datetime(2026, 10, 1, 18, 0, tzinfo=utc),
        "prioridade": "alta",
        "status": "concluída",
    },
]
resultado = analyze_tasks(tarefas)
print(resultado["tempo_medio_conclusao_horas"])  # 1.5
```

Entradas que violam o contrato (datas inconsistentes, campos inválidos, fuso diferente de UTC) lançam `TaskValidationError`. Regras completas em [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md).

## Fluxo de trabalho
- `main`: versão homologada; após a documentação inicial, recebe alterações apenas por Pull Request.
- `feature/*`: desenvolvimento de cada funcionalidade.
- Commits pequenos, no padrão `tipo: descrição` (`feat`, `test`, `docs`, `chore`, `refactor`).

**Observação:** a Fase 1 não foi entregue; a especificação deste repositório foi reconstruída com base nos enunciados, não reproduz uma entrega anterior.
