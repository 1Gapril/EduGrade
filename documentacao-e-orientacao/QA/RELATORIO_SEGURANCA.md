# Relatório de segurança

**Status:** revisão estática e testes unitários focados concluídos; E2E parcial.
Nenhum teste destrutivo ou de exploração foi executado.

| ID | Achado | Evidência | Situação |
|---|---|---|---|
| SEC-01 | Respostas de questões com gabarito podiam ser consultadas por qualquer usuário autenticado | `backend/app/api/routes/exams.py` | Corrigido; coberto por teste unitário |
| SEC-02 | Leituras de submissões não aplicavam isolamento por aluno de forma consistente | `backend/app/api/routes/exams.py` | Corrigido; projeção e isolamento cobertos por testes unitários |
| SEC-03 | Diretório de arquivos estava montado em rota estática sem autenticação | `backend/app/main.py`; `backend/app/integrations/storage.py` | Mount público removido; download autenticado; testes unitários passaram |
| SEC-04 | Logout limpava o cliente, mas não invalidava tokens no servidor | `backend/app/api/routes/auth.py`; `backend/app/services/auth_service.py` | Não corrigido; exige estratégia de revogação/rotação |
| SEC-05 | Upload verifica extensão/tamanho, mas não valida conteúdo/MIME | `backend/app/integrations/storage.py` | Não corrigido; requer testes de arquivo malformado em ambiente isolado |
| SEC-06 | Startup chama seed demonstrativo e captura erros de inicialização, podendo seguir sem banco pronto | `backend/app/main.py`; `backend/app/core/seed.py` | Não corrigido; não iniciar contra banco real para E2E |
| SEC-07 | Configuração de IA pode retornar implementação mock sem explicitar que a chamada não foi real | `backend/app/services/ai_correction_service.py` | OpenAI/Anthropic sem provider agora falham explicitamente; teste unitário passou |
| SEC-08 | Valores default de desenvolvimento (debug e chave fallback) exigem configuração explícita antes da produção | `backend/app/core/config.py` | Não corrigido; `.env` local está em desenvolvimento com `DEBUG` habilitado; desabilitar em implantação pública |

O `.env` local está ignorado pelo Git e não foi alterado. Foram verificados
somente indicadores não secretos: ambiente local de desenvolvimento, `DEBUG`
habilitado, provedor de IA em modo `mock`, sem chaves OpenAI/Anthropic ou chave
mestra configuradas; nenhum valor de segredo foi exibido. O E2E usou uma
configuração temporária isolada com `DEBUG=false`. O banco SQLite local contém
dados e foi preservado. A suíte completa passou em 15 testes, mas o gate de
cobertura falhou em 55,50%. Não se afirma que a aplicação está segura para
produção; logout/revogação, validação de uploads, startup/migrações e fluxos
completos de autorização ainda precisam de correção ou E2E.
