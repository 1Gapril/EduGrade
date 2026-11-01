# QA da Central de Configurações

## Testes locais

Execute os testes focados sem a meta global de cobertura:

```powershell
.\venv\Scripts\python.exe -m pytest tests\unit\test_admin_settings.py -q --no-cov -o addopts=''
```

Os testes cobrem:

- criação, edição e remoção de provedor;
- chave criptografada no banco e mascarada nas respostas;
- auditoria sem plaintext;
- bloqueio de endpoints administrativos para professor;
- teste de conexão/modelos com cliente HTTP simulado;
- recusa de salvar segredo sem chave mestra;
- bloqueio de endpoint personalizado em IP privado.

O teste HTTP usa mock e não comprova conectividade com qualquer provedor externo.

## Evidência do FCC local

Na análise deste ambiente, a instância FCC local respondeu `200` aos endpoints
administrativos de status, configuração e catálogo; o catálogo retornou modelos.
O status reportou o provedor NVIDIA NIM como pronto. Isso comprova apenas que o
FCC local já estava ativo e retornou esses dados naquele momento; não comprova
que a chave salva no EduGrade foi validada nem que `fcc-claude` gerou uma
resposta com ela.

O painel faz novas chamadas ao FCC quando é aberto ou quando se pede um teste.
Se o FCC estiver parado, a API retorna estado indisponível e erro sanitizado.

## Testes reais pendentes

Para evidência real adicional, configure uma chave NVIDIA no cofre e execute:

1. Teste NVIDIA NIM; verifique HTTP 200, modelo(s) retornado(s) e estado
   conectado no painel.
2. Confirme sincronização FCC; verifique a mensagem de aplicação, atualização
   do catálogo e modelo NVIDIA no provedor principal FCC.
3. Execute uma chamada real de geração via `fcc-claude` com o modelo escolhido
   e inspecione o resultado no cliente.
4. Reinicie o EduGrade e verifique que configuração/modelo permanecem e que a
   chave segue mascarada. Uma chave mestra ausente/incorreta deve impedir
   descriptografia, nunca acionar fallback para credenciais em texto.
5. Valide o acesso às rotas como administrador, professor e aluno.

Não marque a conexão `fcc-claude` como concluída antes da chamada real. Esta
tarefa não incluiu uma chave NVIDIA, portanto os passos 1–3 não foram
executados.
