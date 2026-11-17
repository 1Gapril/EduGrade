# Relatório de testes — EduGrade

**Data:** 05/11/2026

## Execuções

| Execução | Resultado |
|---|---|
| Baseline, `python -m pytest -q` | 53 aprovados, 4 avisos; cobertura 58,19%; gate de 80% falhou. |
| Comando do CI antes do ajuste | 0 testes coletados ao executar dentro de `backend/`; cobertura 0%; falhou. |
| Testes focados após as correções | 12 aprovados: vínculo/período, transação e autorização acadêmica. |
| Suíte final, `python -m pytest --cov-report=xml:reports/coverage.xml -q` | 61 aprovados, 4 avisos; cobertura 58,44%; gate de 80% falhou. |
| Suíte após as correções, `python -m pytest --cov-report=xml:reports/coverage.xml --junitxml=reports/junit.xml -q` | 80 aprovados, 4 avisos; cobertura 59,74%; gate de 80% falhou. |
| Execução final após publicação de notas e correção OCR | 83 aprovados, 4 avisos; cobertura 60,34%; gate de 80% falhou. |
| `python -c "import backend.app.main"` | Aprovado. |
| `node --check` em `frontend/js/**/*.js` | Aprovado. |
| `python -m ruff check backend/app tests --statistics` | Reprovado: 1.165 violações no checkout. |

## Avisos

Foram observados avisos de configuração do `pytest-asyncio`, de configuração antiga no Pydantic e de campo `copy` sombreando atributo no schema de submissão.

## Limitações

Não foram executados E2E de navegador, teste de integração com banco persistente, CI remoto nem chamadas reais de IA/OCR. A suíte final teve 83 testes aprovados, mas a qualidade global não passa o gate de cobertura nem o lint.
