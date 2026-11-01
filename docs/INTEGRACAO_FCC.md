# Integração com Free Claude Code (FCC)

O FCC é um serviço separado do EduGrade. Ele não é uma API oficial da
Anthropic, e esta integração não pede nem armazena credenciais pessoais de
Claude Code.

## Descoberta e segurança

O FCC instalado neste ambiente foi identificado pelo processo local e expõe
uma API administrativa loopback. O EduGrade usa apenas interfaces verificadas
no FCC:

- `GET /admin/api/status`
- `GET /admin/api/models`
- `GET /admin/api/config`
- `POST /admin/api/config/apply`
- `POST /admin/api/models/refresh`

O FCC protege a própria interface administrativa para chamadas locais. O
EduGrade também restringe a URL configurada a loopback, não segue redireções e
não usa proxy de ambiente para essa comunicação. Não configure um endereço
remoto para essa API.

O endereço é configurado em **Configurações → FCC / Free Claude Code**. O valor
inicial `http://127.0.0.1:8082` é apenas a configuração local observada e pode
ser alterado se o serviço mudar de porta.

O status apresenta somente campos não secretos: processo, provedor/modelo
principais, estados de provedores, estado do serviço Code e modelos do catálogo.
A API de status consultada não informa versão instalada nem clientes conectados.

## Sincronização explícita NVIDIA NIM

1. Cadastre NVIDIA NIM no EduGrade, usando o endpoint oficial e a chave do
   cofre local.
2. Teste o provedor no EduGrade. O teste consulta o catálogo real da NVIDIA NIM.
3. Na seção NVIDIA NIM, selecione um modelo retornado pelo provedor ou pelo
   catálogo FCC.
4. Confirme **Sincronizar provedor e modelo com FCC**.
5. O EduGrade consulta a configuração FCC, preserva referências às chaves já
   cadastradas, envia a chave pela API `config/apply`, solicita uma atualização
   do catálogo e só seleciona o modelo se ele estiver presente no resultado
   atualizado.

A chave trafega entre processos pela rede local e fica armazenada também no
cofre gerenciado do FCC. Essa cópia adicional é apresentada antes da operação
por confirmação explícita. Erros informam se a credencial pode já ter sido
salva antes de uma falha posterior na atualização do catálogo.

A confirmação de configuração aplicada não prova que o cliente `fcc-claude`
consegue gerar uma resposta. A prova de ponta a ponta exige uma chamada real de
cliente e um modelo autorizado na conta NVIDIA; não declare essa integração
completa apenas com status ou catálogo.

## Limitações

- Não há execução de comandos, alteração direta de arquivos internos do FCC ou
  credenciais pessoais do cliente.
- Modelos alternativos e configurações de clientes locais permanecem
  administrados pela interface FCC, não são sincronizados pelo EduGrade.
- Para verificar a instalação do FCC, abra o endereço configurado e consulte
  `/admin`. Use a API de status para disponibilidade; não presuma a versão
  quando o serviço não a expuser.
