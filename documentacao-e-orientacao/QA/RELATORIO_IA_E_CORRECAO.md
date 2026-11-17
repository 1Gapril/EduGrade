# Relatório de IA e correção

**Status:** fluxo de ponta a ponta NÃO EXECUTADO.

## Evidência do código e ambiente

Há rotas e serviços para correção, resultados e revisão. A configuração da
Central de IA permite cadastrar provedores e testa o catálogo por HTTP; os
testes unitários usam respostas simuladas e não demonstram uma conexão externa.
Foi corrigido o fallback para `MockProvider` quando OpenAI/Anthropic estão
selecionados sem provider correspondente: agora ocorre falha explícita, coberta
por teste unitário. Isso não configura nem valida conexão externa.

No ambiente local, `AI_PROVIDER` está em modo `mock`, `DEBUG` está habilitado
e `ENVIRONMENT` está em desenvolvimento. Não há chaves OpenAI/Anthropic nem
`CREDENTIAL_ENCRYPTION_KEY` configuradas. Nenhum valor de segredo foi exibido
ou alterado. Portanto, nenhuma chamada de correção real foi feita e nenhum
resultado mock deve ser apresentado como nota real.

## Requisitos ainda sem evidência

- OCR e identificação pelo RA/matrícula sem correspondência aproximada.
- Separação de páginas/alunos e tratamento de conflito/duplicidade.
- Pontuação dentro dos limites da rubrica.
- Estado pendente de revisão humana.
- Bloqueio de publicação automática.
- Auditoria da alteração do professor e persistência após reload.

Nenhuma nota foi alterada ou publicada. A suíte completa teve 15 testes
aprovados, mas a cobertura global de 55,50% não alcançou o gate de 80%.
