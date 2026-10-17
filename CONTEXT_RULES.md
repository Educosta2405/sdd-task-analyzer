# CONTEXT_RULES — governança reconstruída da Fase 1

> Reconstrução do **enunciado** da Fase 1, não de uma entrega prévia do estudante. Contradições entre os enunciados são documentadas na especificação.

## Diretivas obrigatórias
- Python 3.11+ e type hints em todas as funções e parâmetros.
- Estilo PEP 8, funções pequenas e com responsabilidade única (SRP).
- Documentar módulos, classes e funções com docstrings.
- Usar exceções específicas e mensagens claras; proteger divisões por zero.
- Empregar `logging` da biblioteca padrão, sem registrar dados sensíveis.
- Manter código legível, nomes descritivos e responsabilidades separadas.

## Proibições
- Não incluir bibliotecas externas além das autorizadas (`pytest`, somente nos testes).
- Não alterar ou remover cenários de teste fornecidos para facilitar sua aprovação.
- Não modificar estrutura definida do repositório sem justificar.
- Não persistir dados em arquivos ou bancos de dados.
- Não alterar assinatura de funções públicas sem aprovação.
- Não gerar código sem testes correspondentes; não inserir duplicações desnecessárias.
- Não presumir requisitos que não constem do contrato sem registrar decisão explícita.

## Fluxo com IA e validação humana
Antes de programar, consultar `specs/task_analyzer_spec.md`. Quando uma ambiguidade surgir, explicar alternativa, registrar a decisão e preservar a rastreabilidade dos testes. O estudante deve conferir o código, executar pytest, revisar alterações e aprovar PR. Não inventar commits, capturas, testes ou outras evidências.
