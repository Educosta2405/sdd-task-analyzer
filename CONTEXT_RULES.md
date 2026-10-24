# CONTEXT_RULES — governança de IA do TaskAnalyzer

> Regras persistentes fornecidas ao assistente de IA antes de qualquer geração de código. Reconstruídas a partir do **enunciado** da Fase 1 (pp. 3 e 8), pois a Fase 1 não foi entregue; não reproduzem uma entrega anterior.

## Fonte da verdade
`specs/task_analyzer_spec.md` é o contrato. Se código e contrato divergirem, o contrato prevalece; se o contrato for ambíguo, a decisão é registrada na especificação antes de ser implementada.

## Diretrizes arquiteturais (obrigatórias)
- Python 3.11+ como versão mínima.
- Type hints em todas as funções, métodos e parâmetros.
- PEP 8 e princípio da responsabilidade única (SRP); funções pequenas, coesas e com um único propósito.
- Docstrings no padrão Google style (`Args`, `Returns`, `Raises`) para módulos, classes e funções.
- Exceções específicas (`TaskValidationError`) com mensagens claras; prevenir divisão por zero.
- Logs estruturados com o módulo padrão `logging`, sem registrar dados sensíveis.
- Código legível e manutenível, com nomes descritivos.

## Proibições
- Não utilizar bibliotecas externas não autorizadas (autorizado: `pytest`, apenas nos testes).
- Não alterar, remover ou adaptar os cenários de teste para facilitar a aprovação.
- Não modificar a estrutura de pastas definida; arquivos de suporte (ex.: `pytest.ini`) só com justificativa no PR.
- Não persistir dados em arquivos ou bancos de dados.
- Não alterar a assinatura (nome e parâmetros) de funções públicas sem autorização.
- Não gerar código sem testes correspondentes.
- Não inserir código duplicado, desnecessário ou comentado em excesso.
- Não assumir comportamentos não especificados no contrato de negócio.
- Não retornar valores diferentes do contrato definido.

## Regras de interação com a IA
- Fornecer sempre o contexto completo (este arquivo e a especificação) antes da solicitação.
- Validar se a IA compreendeu o contrato antes de aceitar o código gerado.
- Solicitar explicações quando houver dúvida sobre a solução.
- Revisar criticamente todo código gerado e rejeitar respostas que violem o contrato ou estas regras.
- Não inventar commits, capturas de tela, resultados de testes ou outras evidências.
- Registrar a participação da IA nos commits (`Co-Authored-By`) e nos Pull Requests.

## Integração contínua, contêiner e dependências
- Toda alteração entra na `main` por Pull Request com o workflow de CI aprovado (jobs `test` e `docker`).
- Não desativar, pular ou enfraquecer etapas do CI (ex.: `continue-on-error`, testes ignorados) para obter build verde.
- Dependências com versão fixada em `requirements.txt`; actions do GitHub fixadas por SHA de commit.
- A imagem Docker usa `python:3.11-slim`, contém apenas o necessário para os testes e executa sem root.
- Não incluir segredos, credenciais ou dados pessoais no código, no workflow ou na imagem.

## Homologação humana
Todo código gerado por IA passa por revisão humana antes de entrar na `main`:
1. Executar todos os testes automatizados (`pytest`) e conferir o CI verde.
2. Revisar a conformidade com o contrato e com estas regras.
3. Analisar qualidade, legibilidade e tratamento de erros.
4. Realizar testes manuais complementares em casos de borda.
5. Somente após a aprovação, fazer o merge do Pull Request.
