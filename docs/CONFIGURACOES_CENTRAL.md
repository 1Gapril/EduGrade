# Central de Configurações e Integrações

## Acesso

Entre como administrador e abra **Administração → Configurações** ou
`/admin/settings.html`. As rotas correspondentes estão em
`/api/v1/admin/settings`. O backend exige a função administrativa em cada
operação; professores e alunos recebem `403`.

## Visão geral e provedores

A visão geral consulta o banco, o espaço do volume de uploads, o estado das
integrações cadastradas e os endpoints reais de status e catálogo do FCC.
Estados de provedores externos somente mudam para **Conectado** depois de uma
consulta real ao endpoint de modelos. O painel não exibe a URL do banco nem
credenciais de conexão.

O catálogo inicial reconhece NVIDIA NIM, OpenAI, Anthropic, Google Gemini,
DeepSeek, Groq, OpenRouter, Ollama e endpoints OpenAI-compatible personalizados.
Os endpoints dos provedores conhecidos ficam restritos aos domínios oficiais.
Ollama é limitado a loopback. Provedores personalizados precisam de HTTPS e
resolução para IPs públicos.

Para cadastrar um provedor:

1. Preencha tipo, identificador, nome, URL e modelo. Para um endpoint que não
   enumera modelos, o identificador do modelo pode ser informado manualmente.
2. Para serviços autenticados, inicialize o cofre conforme
   [Segurança de credenciais](SEGURANCA_CREDENCIAIS.md).
3. Salve a configuração e use **Testar**. A chave não é retornada pela API.
4. Após um teste bem-sucedido, edite o provedor para habilitá-lo e selecioná-lo
   como principal.

Uma chave vazia ao editar mantém a credencial salva. Para substituí-la, digite
uma chave nova. Remover um provedor exige confirmação e é registrado na
auditoria.

## O que pode ser alterado

O painel salva provedores e os limites de upload, timeout/tentativas de IA,
expiração de tokens e caminho do Tesseract no banco de dados. Esses valores são
aplicados no processo atual e reaplicados na inicialização seguinte.

Banco de dados, backups/restauração, diretórios privados, SMTP e outros segredos
de bootstrap são exibidos somente como diagnóstico ou continuam fora do painel.
Não há botão de restauração ou alteração destrutiva do banco. A URL do FCC pode
ser salva, mas é obrigatoriamente local (`localhost`, `127.0.0.1` ou `::1`).

## Rotas administrativas

- `GET /api/v1/admin/settings/overview`
- `GET/POST /api/v1/admin/settings/providers`
- `PUT/DELETE /api/v1/admin/settings/providers/{provider_id}`
- `POST /api/v1/admin/settings/providers/{provider_id}/test`
- `GET/PUT /api/v1/admin/settings/system`
- `GET/PUT /api/v1/admin/settings/fcc`
- `POST /api/v1/admin/settings/fcc/test`
- `POST /api/v1/admin/settings/fcc/sync/nvidia`
- `GET /api/v1/admin/settings/audit`

Consulte `/docs` quando o modo de desenvolvimento estiver habilitado para os
schemas atuais.

## Limites declarados

- O catálogo de APIs é amplo, mas não significa que uma conta ou credencial
  esteja configurada. O teste externo depende do endpoint e do acesso de rede.
- O FCC não fornece, nos endpoints de status usados, sua versão instalada nem
  a quantidade de clientes conectados. O painel informa esses campos como não
  disponíveis em vez de inferi-los.
- Backup/restore, e-mail, logotipo, permissões granulares por ação e capacidades
  por finalidade de modelo não são editáveis nesta versão.
- Para chamadas de correção em tempo de execução, use um provedor testado como
  principal. Modelos de visão devem ser identificados explicitamente; não se
  presume capacidade multimodal a partir do nome do modelo.
- Veja [QA](QA/TESTES_CONFIGURACOES.md) antes de tratar uma integração externa
  como pronta para produção.
