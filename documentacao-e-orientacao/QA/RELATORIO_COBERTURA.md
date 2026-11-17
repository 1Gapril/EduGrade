# Relatório de cobertura

**Baseline existente:** 9 testes em 3 arquivos.

Após as alterações, a suíte completa encontrou **15 testes aprovados** em 5
arquivos. A execução padrão terminou com código 1 porque a cobertura agregada
foi **55,50%**, abaixo do limite de 80% configurado em `pyproject.toml`.

| Medição | Resultado |
|---|---:|
| Cobertura anterior | 54,31% |
| Cobertura pós-alterações | 55,50% |
| Meta configurada | 80% |
| Testes aprovados | 15 |
| Arquivos de teste | 5 |
| Resultado do comando | Código 1: gate de cobertura não atingido |

Não houve alteração artificial de relatório ou limite. A cobertura mínima não
foi atingida; o projeto não está aprovado por esse critério. A suíte também
emitiu avisos de configuração do `pytest-asyncio`; eles não falharam os testes.

O README descreve um pipeline GitHub Actions, mas não há arquivos de workflow
rastreados em `.github/workflows` neste checkout. A execução de CI não foi
verificada.
