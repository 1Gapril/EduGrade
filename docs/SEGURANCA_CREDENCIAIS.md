# Segurança do cofre de credenciais

## Inicialização única

As chaves de API são criptografadas com Fernet antes de serem persistidas em
`ai_provider_configs.encrypted_api_key`. A chave mestra não é armazenada no
banco e não pode ser consultada ou alterada pela interface.

Gere uma chave aleatória com o Python do projeto:

```powershell
.\venv\Scripts\python.exe -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copie o valor gerado e configure-o no ambiente seguro do processo EduGrade como
`CREDENTIAL_ENCRYPTION_KEY`. Para desenvolvimento local, a opção é colocá-lo no
`.env` ignorado pelo Git:

```env
CREDENTIAL_ENCRYPTION_KEY=COLE_A_CHAVE_GERADA_AQUI
```

Não use uma string escolhida manualmente nem publique, registre ou envie a
chave. Reinicie o backend após configurar o segredo. Em produção, use o gerenciador
de segredos do ambiente de execução, não um `.env` versionado.

Sem essa chave, o painel ainda permite consultar estado e configurar provedores
sem segredo, mas recusa persistir credenciais com HTTP 503. Uma chave mestra
incorreta ou perdida torna as credenciais criptografadas ilegíveis.

## Operações

- A API nunca retorna o texto completo de uma chave; a interface exibe somente
  estado configurado e uma máscara curta.
- Uma chave vazia ao editar preserva a credencial existente. Uma chave nova a
  substitui.
- Remover a configuração apaga a credencial criptografada associada.
- Eventos de auditoria registram o provedor, estado e metadados; não incluem
  chave, ciphertext ou corpo de requisição.
- Erros de APIs externas são sanitizados e não incluem resposta bruta.
- Endpoints conhecidos aceitam apenas seus domínios HTTPS oficiais. Ollama e
  FCC são restritos a loopback; endpoints personalizados são HTTPS e rejeitam
  DNS/IP privado.
- Credenciais de banco, SMTP e segredos pessoais não são coletados pela tela de
  provedores.

## Backup e rotação

Faça backup protegido do banco e da chave mestra como itens separados. Quem
obtiver os dois consegue recuperar as chaves de API.

Rotação automática da chave mestra não está implementada no painel. Não troque
`CREDENTIAL_ENCRYPTION_KEY` enquanto houver credenciais criptografadas sem um
procedimento de migração: primeiro exporte/recadastre as chaves pelo fluxo
administrativo ou implemente uma rotação controlada com backup e teste de
restauração. Nunca registre plaintext durante uma migração.
