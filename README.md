# TaskAnalyzer — Bootcamp III

[![CI](https://github.com/Educosta2405/sdd-task-analyzer/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Educosta2405/sdd-task-analyzer/actions/workflows/ci.yml)

Projeto acadêmico de análise de tarefas e produtividade em Python 3.11+, desenvolvido com Spec-Driven Development (SDD): o código de `src/` foi gerado com assistente de IA a partir da especificação e das regras de contexto, validado por testes pytest, executado em integração contínua e em contêiner Docker, e homologado por revisão humana via Pull Request.

## Status do build
- **Integração contínua:** o badge acima mostra o resultado do workflow [`ci.yml`](.github/workflows/ci.yml) na `main`. Cada push ou Pull Request em `main` e `develop` executa o Test Harness em Python 3.11 (`ubuntu-latest`) e dentro da imagem Docker `python:3.11-slim`.
- **Histórico de execuções:** [aba Actions](https://github.com/Educosta2405/sdd-task-analyzer/actions/workflows/ci.yml).

## Estrutura
```
sdd-task-analyzer/
├── .github/
│   └── workflows/
│       └── ci.yml                    # Pipeline de CI (GitHub Actions)
├── Dockerfile                        # Imagem python:3.11-slim do Test Harness
├── docker-compose.yml                # Serviço test-harness
├── .dockerignore                     # Exclusões do contexto de build
├── CONTEXT_RULES.md                  # Regras de governança fornecidas à IA
├── specs/
│   ├── task_analyzer_spec.md         # Contrato SDD (fonte da verdade)
│   ├── requirements.yaml             # Requisitos estruturados e rastreáveis
│   └── system_design_document.pdf    # Documento de projeto do sistema
├── tests/
│   └── test_harness.py               # Test Harness (cenários 1 e 2 e bordas)
├── src/
│   ├── __init__.py
│   └── task_analyzer.py              # analyze_tasks e TaskValidationError
├── pytest.ini                        # Configuração para rodar `pytest` na raiz
├── requirements.txt                  # Dependência autorizada (pytest==9.1.1)
├── .gitignore
└── README.md
```

## Como executar

### Com Docker (ambiente isolado)
Requer Docker com o plugin Compose.
```bash
docker compose run --rm test-harness
```
Equivalente sem Compose:
```bash
docker build -t sdd-task-analyzer .
docker run --rm sdd-task-analyzer
```

### Localmente (Python 3.11+)
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
python -m pip install -r requirements.txt
pytest tests/test_harness.py -v
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
- `main`: versão homologada; após a documentação inicial, recebe alterações apenas por Pull Request com CI verde e homologação humana.
- `develop`: integração das funcionalidades antes da `main` (a partir da Fase 3).
- `feature/*`: desenvolvimento de cada funcionalidade, integrado por Pull Request.
- Commits pequenos, no padrão `tipo: descrição` (`feat`, `test`, `docs`, `chore`, `refactor`, `ci`, `build`).

**Observação:** a Fase 1 não foi entregue; a especificação deste repositório foi reconstruída com base nos enunciados, não reproduz uma entrega anterior.
