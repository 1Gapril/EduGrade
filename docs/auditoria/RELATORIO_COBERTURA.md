# Relatório de cobertura — EduGrade

**Data:** 05/11/2026  
**Ferramenta:** pytest-cov / coverage.py  
**Meta configurada:** 80%

## Resultado real

- Testes aprovados na execução final: **83**.
- Statements contabilizados: **7.208**.
- Statements não cobertos: **2.859**.
- Statements cobertos: **4.349**.
- Cobertura global: **60,34%**.
- Critério de 80%: **não atingido**.
- Relatório HTML: [`reports/coverage/index.html`](../../reports/coverage/index.html).
- Relatório XML: [`reports/coverage.xml`](../../reports/coverage.xml).

Não foi aplicado nenhum `omit` adicional para aumentar artificialmente o percentual. Cobertura de branches não está configurada como requisito separado no `pyproject.toml`.

## Áreas prioritárias para ampliar cobertura

O baseline mostra serviços e repositórios com cobertura baixa, incluindo autenticação, usuário, material, correção por IA, correção em lote e módulos acadêmicos/provas. A ampliação deve testar regras e resultados, não apenas executar linhas ou usar mocks sem assertivas.
