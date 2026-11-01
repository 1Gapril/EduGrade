# Bugs e pendências encontrados

**Estado:** levantamento estático e validação parcial; não representa auditoria aprovada.

| ID | Prioridade | Problema observado | Evidência / estado |
|---|---|---|---|
| BUG-01 | Crítica | Exposição potencial de gabaritos a aluno autenticado | Corrigido; coberto por teste unitário |
| BUG-02 | Crítica | Acesso a submissões sem isolamento consistente por aluno | Corrigido; coberto por testes unitários |
| BUG-03 | Alta | Arquivos privados servidos por montagem estática pública | Corrigido; download exige rota autenticada; teste unitário |
| BUG-04 | Alta | Upload de arquivo no processamento em lote retorna `501` | Não implementado |
| BUG-05 | Alta | Dashboards exibiam números/listas estáticos como se fossem reais | Removidos; indisponibilidades são explicitadas; E2E parcial |
| BUG-06 | Alta | Fallback para provider mock podia ocultar falta de integração real | Corrigido para OpenAI/Anthropic; teste unitário; provider real não configurado |
| BUG-07 | Média | Logout não revoga token no backend | Aberto |
| BUG-08 | Média | Validação de upload não verifica conteúdo/MIME | Aberto |
| BUG-09 | Média | Checagem de sessão na tela de login referencia estado antes de inicializá-lo | Corrigido; login E2E passou para os três perfis |
| BUG-10 | Média | Workspace não aplica verificação global de perfil; algumas rotas ficam incompletas | Checagem de perfil adicionada para UX; autorização do servidor segue necessária |
| BUG-11 | Média | Migração inicial não contém todas as tabelas dos models atuais | Aberto; startup usa `create_all()` |
| BUG-12 | Média | Startup captura exceção de inicialização e ainda pode manter servidor ativo | Aberto |
| BUG-13 | Baixa | Links/documentação tinham nomes de arquivo inexistentes e instruções para apagar banco | Documentação corrigida nesta auditoria |
| BUG-14 | Bloqueio | Tesseract executável/Poppler e PDF indicado ausentes | Impede teste OCR real até fornecer dependências/arquivo |
| BUG-15 | Bloqueio | Sem `CREDENTIAL_ENCRYPTION_KEY` e chave externa da NVIDIA | Impede conexão autenticada e sincronização FCC |
| BUG-16 | Média | README descreve CI/CD sem workflow GitHub Actions rastreado | `git ls-files .github` não retorna workflow |
| BUG-17 | Média | Dashboard do professor exibia erro e materiais presos em “Carregando...” | Corrigido; login E2E sem toast, endpoints carregaram e placeholders foram resolvidos |
| BUG-18 | Média | Configuração FCC aceitava URL base com `/admin`, duplicando o caminho dos endpoints administrativos | Corrigido; `/admin` final é normalizado para a origem e comunicação foi confirmada em E2E |

Prioridades são qualitativas e não substituem triagem institucional. Não foram
alterados dados reais nem publicadas notas.
