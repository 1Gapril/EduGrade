# NVIDIA NIM — passo a passo

Este guia configura a conexão direta **EduGrade → API NVIDIA NIM**. Ela não
depende do FCC. A sincronização com **FCC / Claude Code** é uma etapa opcional
que envia uma cópia da credencial para o serviço local.

## 1. Se uma chave foi compartilhada

Se uma chave NVIDIA foi colada em chat, chamado, print ou commit, considere-a
comprometida:

1. Acesse [NVIDIA API Keys](https://build.nvidia.com/settings/api-keys).
2. Revogue a chave exposta.
3. Crie uma chave nova e guarde-a em um gerenciador de segredos.
4. Não reutilize nem cole a chave nova em conversas, documentação, prints ou
   comandos registrados no histórico.

Não é necessário informar a chave ao assistente para configurar a integração.

## 2. Inicialize o cofre de credenciais

O EduGrade criptografa a chave NVIDIA antes de salvá-la no banco. A
`CREDENTIAL_ENCRYPTION_KEY` é a chave mestra do cofre; **não é** a chave NVIDIA
e não pode ser recuperada pelo painel.

Na raiz do projeto, gere uma chave Fernet usando o Python do projeto:

```powershell
.\venv\Scripts\python.exe -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Configure o valor gerado como `CREDENTIAL_ENCRYPTION_KEY` no `.env` local
ignorado pelo Git, ou no gerenciador de segredos do ambiente de execução:

```env
CREDENTIAL_ENCRYPTION_KEY=COLE_A_CHAVE_FERNET_GERADA_AQUI
```

Regras importantes:

- Não use a chave NVIDIA como `CREDENTIAL_ENCRYPTION_KEY`.
- Não publique nem compartilhe a chave mestra.
- Reinicie o backend para carregar a configuração.
- Faça backup protegido do banco e da chave mestra separadamente. Perder ou
  trocar a chave mestra sem migrar as credenciais impede descriptografá-las.

Mais detalhes: [Segurança de credenciais](SEGURANCA_CREDENCIAIS.md).

## 3. Cadastre NVIDIA NIM no painel

1. Entre no EduGrade com perfil administrador.
2. Abra **Configurações → Provedores de IA**.
3. Em **Adicionar provedor**, selecione **NVIDIA NIM**.
4. Preencha:
   - **Identificador:** `nvidia_nim` (ou outro ID único permitido).
   - **Nome:** por exemplo, `NVIDIA NIM`.
   - **Base URL:** `https://integrate.api.nvidia.com/v1`.
   - **API Key:** cole a chave nova diretamente no campo do painel.
   - **Modelo:** pode ser escolhido após consultar o catálogo.
5. Salve o provedor. A resposta do EduGrade não revela a chave; ao editar, o
   campo vazio mantém a credencial atual e uma chave nova a substitui.

O cadastro direto da API usa o formulário de provedores. A seção **NVIDIA NIM**
da central também lista os modelos recebidos e apresenta controles para uma
eventual sincronização com FCC.

## 4. Teste a conexão direta com a NVIDIA

1. Clique **Testar** no provedor recém-cadastrado.
2. O EduGrade consulta, com autenticação, o endpoint de modelos da NVIDIA.
3. Confirme que o estado ficou **Conectado** e que o catálogo retornou modelos.
4. Selecione um modelo retornado, habilite o provedor e defina-o como principal
   se desejar usá-lo nas correções.

O teste confirma autenticação e acesso ao catálogo, não uma correção acadêmica
completa. Para provar geração, use um teste controlado, sem dados pessoais, e
confirme modelo, limites e eventuais custos da conta NVIDIA.

### Se o teste falhar

- **Cofre não inicializado / HTTP 503:** configure `CREDENTIAL_ENCRYPTION_KEY`
  no processo do backend e reinicie-o.
- **Autenticação recusada / HTTP 401 ou 403:** confirme que a chave nova está
  ativa na NVIDIA e substitua-a no provedor.
- **Timeout ou indisponibilidade:** verifique internet, acesso ao endpoint e
  disponibilidade do serviço NVIDIA.
- **Catálogo sem modelos:** confirme se o endpoint/modelo está disponível para
  a conta; não marque a integração como validada sem resposta bem-sucedida.

Não coloque chaves em logs ou mensagens de erro. A API do EduGrade deve retornar
estado e mensagem sanitizados, nunca a chave ou o corpo bruto da resposta.

## 5. FCC é opcional

Para usar NVIDIA diretamente na aplicação EduGrade, **não é necessário
sincronizar com FCC**. Só faça isso se também quiser configurar o FCC para usar
a credencial/modelo:

1. Teste NVIDIA no EduGrade e selecione um modelo confirmado.
2. Na seção **NVIDIA NIM**, escolha o modelo oferecido para sincronização.
3. Leia [Integração FCC](INTEGRACAO_FCC.md) e confirme conscientemente a
   operação. Ela envia uma cópia da chave ao cofre administrado pelo FCC.

A URL do FCC deve conter somente a origem local, por exemplo
`http://127.0.0.1:8082`, sem `/admin`. Status e catálogo do FCC não provam que a
chave salva no EduGrade foi validada pela NVIDIA nem que houve geração real.

## Estado da validação neste ambiente

O status e o catálogo do FCC foram consultados com sucesso; isso foi apenas uma
verificação da integração administrativa local. A chave exposta deve ser
revogada. Não foi realizado teste autenticado NVIDIA com essa chave, nem
sincronização dela com o FCC. Para validar a integração, gere uma chave nova e
siga este guia sem compartilhá-la.
