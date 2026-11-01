# NVIDIA NIM

## Criar uma chave

1. Acesse [NVIDIA API Keys](https://build.nvidia.com/settings/api-keys).
2. Crie uma chave para a conta/serviço que será usado.
3. Não envie a chave por chamados, prints, commits ou mensagens.

## Cadastrar e testar

1. Faça o bootstrap do cofre conforme
   [Segurança de credenciais](SEGURANCA_CREDENCIAIS.md).
2. Abra **Configurações → Provedores de IA** e selecione **NVIDIA NIM**.
3. Mantenha `https://integrate.api.nvidia.com/v1` como Base URL, informe um
   identificador único, nome e chave. O painel não fixa um modelo.
4. Salve e clique **Testar**. O EduGrade faz uma chamada real autenticada ao
   endpoint de modelos da NVIDIA NIM. O resultado HTTP e os identificadores
   listados são devolvidos sem incluir o corpo de erro ou a chave.
5. Escolha um modelo disponível, habilite a integração e defina-a como
   principal somente após o teste ter sido bem-sucedido.

Uma indisponibilidade, chave recusada ou timeout permanece registrada como
falha/teste pendente; não é apresentada como conexão bem-sucedida.

## Sincronizar com FCC

Na seção NVIDIA NIM, escolha um identificador confirmado e use a sincronização
explícita. O EduGrade chama a API administrativa local documentada do FCC,
preserva credenciais FCC já referenciadas, atualiza o catálogo e seleciona o
modelo apenas se ele aparecer no resultado. Leia
[Integração FCC](INTEGRACAO_FCC.md) antes de autorizar o envio da chave ao FCC.

## Estado deste ambiente

Não foi fornecida uma chave NVIDIA ao EduGrade nesta tarefa. Portanto, o teste
autenticado da chave e a sincronização desta chave com o FCC não foram
executados. Um FCC que já informa NVIDIA NIM como disponível não comprova que
a chave cadastrada no EduGrade é a mesma nem que uma chamada do `fcc-claude`
foi bem-sucedida.
