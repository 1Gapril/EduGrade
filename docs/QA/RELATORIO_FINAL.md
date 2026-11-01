# Relatório final — auditoria EduGrade

**Status: NÃO APROVADO para produção; auditoria estática e E2E parcial concluídos.**

O status não significa que todas as telas/fluxos estejam certificados. Foram
corrigidos problemas prioritários de autorização, arquivos, fallback de IA e
dashboards; os fluxos de provas, notas, uploads e OCR continuam parcialmente
sem teste.

## Evidências atuais

- Repositório em `develop`; árvore de trabalho preservada durante a auditoria.
- Banco SQLite local não vazio, não consultado individualmente e não alterado.
- `.env` local ignorado pelo Git e não alterado. Foram verificados apenas
  indicadores não secretos: ambiente de desenvolvimento, `DEBUG` habilitado,
  `AI_PROVIDER=mock`, sem chaves OpenAI/Anthropic ou chave mestra; nenhum segredo
  foi mostrado.
- E2E usou banco e storage temporários marcados
  `DADO_DE_TESTE_EDUGRADE`; nenhum fluxo tocou no SQLite local.
- Login admin/professor/aluno e login inválido foram exercitados. O dashboard
  do professor carregou materiais/revisões sem erro; sem disciplina atribuída,
  o upload permaneceu desabilitado. Dados sem fonte confiável aparecem como
  indisponíveis.
- FCC status e catálogo responderam HTTP 200, com 38 modelos. A central do
  EduGrade aceitou a URL com `/admin`, normalizou para a origem local e
  confirmou a comunicação; nenhuma credencial foi sincronizada.
- A suíte final teve 15 testes aprovados, mas cobertura de 55,50%, abaixo do
  gate de 80%; o comando terminou com código 1 por cobertura.
- `git diff --check` e `node --check` passaram.
- Screenshots estão em `docs/QA/evidencias/`.
- O PDF de teste e os executáveis Tesseract/Poppler não foram encontrados.
- PDF de teste e executáveis Tesseract/Poppler não encontrados nos locais
  pesquisados.

## Bloqueios para aprovação

1. Aumentar a cobertura com testes significativos até o gate real de 80%.
2. Concluir E2E de CRUD, provas, correção, notas, matrícula e autorização por
   objeto/perfil.
3. Implementar e testar o upload batch, atualmente `501 Not Implemented`.
4. Disponibilizar o PDF e as dependências OCR para validar a prova solicitada.
5. Configurar `CREDENTIAL_ENCRYPTION_KEY` e uma chave NVIDIA autorizada para
   validar a chamada real; não sincronizar a chave ao FCC sem autorização.
6. Tratar revogação de tokens no logout, validação de conteúdo/MIME dos uploads
   e falhas de inicialização/migrações.
7. Desabilitar `DEBUG` e rever a chave de desenvolvimento antes de publicar.

As alterações permanecem locais e sem commit/push. Consulte a matriz e os
relatórios por perfil para evidências e limites. A integração NVIDIA direta
está implementada na central, mas não foi autenticada neste ambiente: faltam a
chave de API e a chave mestra do cofre. O status NVIDIA que o FCC reporta não
substitui esse teste.
