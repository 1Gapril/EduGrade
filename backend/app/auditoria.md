# PROMPT MASTER — AUDITORIA COMPLETA, CORREÇÃO DO SISTEMA, TESTES AUTOMATIZADOS E PAINEL DE COBERTURA

## OBJETIVO PRINCIPAL

Quero que você faça uma auditoria técnica completa em todo o meu sistema, analisando todas as telas, funcionalidades, botões, rotas, serviços, integrações e comunicações entre frontend, backend e banco de dados.

Não quero apenas uma análise ou relatório. Quero que você investigue, corrija os problemas encontrados, implemente as funcionalidades ausentes e execute os testes para comprovar que tudo está funcionando.

O objetivo é entregar um sistema funcional, estável, seguro e testado, com pelo menos 80% de cobertura de código e uma página administrativa para acompanhar os resultados.

---

# 1. CORRIGIR O CADASTRO E GERENCIAMENTO DE PROFESSORES

Identifique e corrija a ausência da opção de adicionar disciplinas aos professores.

Verifique:

- Opção de adicionar disciplina ao professor.
- Listagem de disciplinas disponíveis.
- Associação entre professor e disciplina.
- Edição das disciplinas vinculadas.
- Remoção de disciplinas vinculadas.
- Persistência dos dados no banco.
- Atualização automática das informações na interface.
- Validação para impedir associações duplicadas.
- Permissões de acesso para administradores e usuários autorizados.

A associação deve funcionar corretamente tanto na interface quanto no backend.

Verifique também se o professor consegue visualizar somente as disciplinas às quais está vinculado, respeitando as regras de acesso do sistema.

# 2. AUDITAR TODAS AS TELAS E FUNCIONALIDADES

Faça uma varredura completa em todas as telas do sistema.

Verifique:

- Botões e seus eventos.
- Formulários e validações.
- Menus e opções.
- Rotas de navegação.
- Modais e janelas de confirmação.
- Listagens e filtros.
- Cadastro, edição e exclusão.
- Comunicação entre frontend e backend.
- Requisições às APIs.
- Serviços e funções internas.
- Banco de dados e persistência.
- Controle de acesso e permissões.
- Mensagens de sucesso e erro.
- Carregamentos e estados vazios.

Identifique:

- Botões sem ação.
- Funções incompletas.
- Links quebrados.
- Rotas inexistentes.
- Erros silenciosos.
- Requisições que falham.
- Dados que não são salvos.
- Informações desatualizadas.
- Funcionalidades que apresentam sucesso na tela, mas não concluem a operação no servidor.

Crie um inventário das funcionalidades encontradas e seu respectivo status.

# 3. TESTAR O MÓDULO DE PROVAS

Realize testes completos nas funcionalidades do módulo de provas.

### 3.1. Publicar prova

- Criar uma prova.
- Adicionar questões.
- Editar questões.
- Associar a disciplina.
- Definir professor responsável.
- Definir data e prazo, quando disponíveis.
- Publicar a prova.
- Verificar se ela fica disponível para os alunos autorizados.
- Conferir se os dados são persistidos.
- Verificar se a prova aparece corretamente nas listagens.

### 3.2. Visualizar disciplinas

- Consultar disciplinas cadastradas.
- Verificar disciplinas vinculadas aos professores.
- Conferir permissões de visualização.
- Testar filtros.
- Verificar atualização dos dados.
- Validar se professores e alunos visualizam apenas as informações permitidas.

### 3.3. Corrigir provas

- Abrir provas respondidas.
- Corrigir questões objetivas.
- Corrigir questões discursivas, quando disponíveis.
- Calcular a nota.
- Salvar a correção.
- Conferir o resultado.
- Verificar se o aluno consegue visualizar a nota conforme as regras do sistema.
- Validar se a nota permanece salva após atualizar a página.

# 4. AUDITAR TODOS OS BOTÕES

Faça um levantamento de todos os botões existentes no projeto.

Para cada botão:

1. Identifique sua finalidade.
2. Localize sua função ou evento.
3. Execute o fluxo correspondente.
4. Verifique se a ação é concluída.
5. Confirme se os dados são atualizados.
6. Verifique mensagens de sucesso e erro.
7. Corrija botões que não executam suas funções.

Inclua:

- Botões de salvar.
- Botões de editar.
- Botões de excluir.
- Botões de cancelar.
- Botões de publicar.
- Botões de consultar.
- Botões de corrigir.
- Botões de adicionar.
- Botões de exportar.
- Botões de navegação.
- Botões de confirmação.

Não considere um botão funcional apenas porque responde ao clique. Verifique se a operação realmente foi concluída.

# 5. REVISAR A COMUNICAÇÃO ENTRE FRONTEND, BACKEND E SERVIÇOS

Analise todos os fluxos de comunicação.

Verifique:

- Chamadas HTTP.
- Endpoints e métodos.
- Controllers.
- Services.
- Repositories.
- Models.
- Middlewares.
- Autenticação.
- Autorização.
- Tratamento de exceções.
- Respostas das APIs.
- Integridade dos dados.
- Relacionamentos do banco de dados.
- Transações.
- Validações no servidor.

Corrija inconsistências entre os dados enviados pelo frontend e os esperados pelo backend.

Verifique se as operações de cadastro, edição, exclusão e consulta estão funcionando corretamente.

# 6. CRIAR TESTES UNITÁRIOS COM COBERTURA MÍNIMA DE 80%

Crie uma estrutura completa de testes de cobertura para todo o sistema.

Analise a tecnologia e utilize a ferramenta de testes já adotada pelo projeto.

Configure os seguintes limites mínimos:

- Statements: 80%.
- Branches: 80%.
- Functions: 80%.
- Lines: 80%.

Crie testes para:

### Professores
- Cadastro.
- Edição.
- Exclusão.
- Consulta.
- Adição de disciplinas.
- Remoção de disciplinas.
- Associação entre professor e disciplina.
- Validação de permissões.

### Disciplinas
- Cadastro.
- Consulta.
- Edição.
- Exclusão.
- Vínculo com professores.
- Validação de dados.
- Permissões.

### Provas
- Criação.
- Edição.
- Publicação.
- Cancelamento de publicação, quando permitido.
- Consulta.
- Associação à disciplina.
- Associação ao professor.
- Validação de questões e respostas.

### Correção de provas
- Correção de questões objetivas.
- Correção de questões discursivas.
- Cálculo de notas.
- Salvamento das correções.
- Consulta dos resultados.
- Permissões dos alunos.

### Demais funcionalidades
- Services.
- Controllers.
- Repositories.
- Validações.
- Regras de negócio.
- Autenticação.
- Autorização.
- Tratamento de erros.
- Comunicação com APIs.

Não exclua arquivos importantes para aumentar artificialmente a cobertura.

# 7. CRIAR TESTES DE INTEGRAÇÃO

Valide a comunicação real entre frontend, backend e banco de dados.

Teste:

- Cadastro de professores.
- Atualização de professores.
- Associação de disciplinas.
- Persistência de dados.
- Comunicação com APIs.
- Publicação de provas.
- Correção de provas.
- Atualização de notas.
- Controle de permissões.
- Consulta de informações.

Utilize banco de testes ou ambiente isolado.

Não altere dados de produção.

# 8. CRIAR TESTES PONTA A PONTA (E2E)

Crie cenários automatizados para validar os principais fluxos do sistema.

### Fluxo 1 — Professor e disciplinas

1. Administrador cadastra um professor.
2. Administrador adiciona disciplinas ao professor.
3. Sistema salva a associação.
4. Professor acessa suas disciplinas.
5. Professor visualiza as disciplinas vinculadas.

### Fluxo 2 — Publicação de provas

1. Professor cria uma prova.
2. Professor adiciona questões.
3. Professor seleciona a disciplina.
4. Professor publica a prova.
5. Aluno visualiza a prova.
6. Aluno responde à prova.

### Fluxo 3 — Correção de provas

1. Professor acessa provas respondidas.
2. Professor corrige a prova.
3. Sistema calcula a nota.
4. Sistema salva o resultado.
5. Aluno consulta a nota.

Confirme se todos os dados permanecem salvos após atualizar a página e realizar novas consultas.

# 9. CRIAR TESTES NEGATIVOS E DE SEGURANÇA

Teste situações de erro:

- Campos obrigatórios vazios.
- Dados inválidos.
- Professor sem disciplina.
- Disciplina inexistente.
- Associação duplicada.
- Usuário sem permissão.
- Prova sem questões.
- Publicação de prova inválida.
- Correção de prova inexistente.
- Erros de comunicação com o servidor.
- Falhas no banco de dados.
- Acesso indevido a resultados de outros alunos.
- Tentativas de acessar rotas restritas.
- Dados enviados em formatos incorretos.

O sistema deve apresentar mensagens apropriadas e não pode perder ou corromper dados.

# 10. CRIAR RELATÓRIO HTML DE COBERTURA E AUDITORIA

Crie um arquivo independente chamado:

`relatorio-testes.html`

O relatório deverá apresentar:

### Resumo da auditoria
- Quantidade de testes executados.
- Testes aprovados.
- Testes reprovados.
- Funcionalidades testadas.
- Funcionalidades corrigidas.
- Funcionalidades pendentes.

### Cobertura de código
- Statements.
- Branches.
- Functions.
- Lines.
- Cobertura geral.
- Cobertura por módulo.
- Cobertura por arquivo.
- Linhas de código não testadas.

### Status visual

- Verde: aprovado.
- Vermelho: reprovado.
- Amarelo: pendente.

Inclua gráficos, indicadores de cobertura e data e horário da última execução.

O relatório deve ser atualizado automaticamente a cada execução dos testes, utilizando os resultados reais da ferramenta de cobertura.

Não invente resultados nem apresente funcionalidades como aprovadas sem testes executados.

# 11. AUTOMATIZAR A EXECUÇÃO DOS TESTES

Configure comandos no projeto, adaptados à tecnologia existente:

- `test`: executar todos os testes.
- `test:unit`: executar testes unitários.
- `test:integration`: executar testes de integração.
- `test:e2e`: executar testes ponta a ponta.
- `test:coverage`: executar testes e calcular cobertura.
- `test:report`: gerar o relatório HTML.

Configure também a execução automática no processo de integração contínua (CI), quando disponível.

Os relatórios devem ser atualizados depois de cada execução.

# 12. IMPLEMENTAR BLOQUEIO DE QUALIDADE

Configure limites mínimos para impedir que novas alterações reduzam a cobertura abaixo de 80%.

Quando os testes falharem:

1. Identifique a origem do problema.
2. Analise o código responsável.
3. Corrija a falha.
4. Execute novamente os testes.
5. Atualize o relatório.
6. Confirme os resultados.

Não utilize mocks excessivos, testes artificiais ou exclusões indevidas.

# 13. CRIAR PÁGINA DE CONSULTA DE TESTES E COBERTURA DENTRO DO SISTEMA

Além do arquivo HTML independente, quero uma página própria integrada ao sistema, chamada:

**Painel de Testes e Cobertura**

Essa página deverá estar disponível no menu administrativo.

### 13.1. Acesso à página

- Adicionar opção "Testes e Cobertura" no menu administrativo.
- Criar rota própria.
- Restringir o acesso a administradores e usuários autorizados.
- Garantir navegação correta entre a página e as demais telas.
- Seguir o padrão visual do sistema.

### 13.2. Dashboard de cobertura

Exibir indicadores:

- Cobertura de Statements.
- Cobertura de Branches.
- Cobertura de Functions.
- Cobertura de Lines.
- Total de testes executados.
- Testes aprovados.
- Testes reprovados.
- Testes pendentes.
- Última execução.

Apresentar gráficos de progresso para cada métrica.

Destacar visualmente quando alguma métrica estiver abaixo de 80%.

### 13.3. Consulta detalhada dos testes

Criar uma tabela com:

| Funcionalidade | Tipo de teste | Resultado | Status |
|---|---|---|---|
| Cadastro de professor | Unitário | Resultado real | Status real |
| Adicionar disciplina | Integração | Resultado real | Status real |
| Publicar prova | E2E | Resultado real | Status real |
| Visualizar disciplinas | Unitário | Resultado real | Status real |
| Corrigir prova | E2E | Resultado real | Status real |

Permitir:

- Pesquisar testes.
- Filtrar por módulo.
- Filtrar por tipo de teste.
- Filtrar por status.
- Consultar detalhes de cada execução.
- Visualizar erros encontrados.
- Identificar arquivos sem cobertura.
- Consultar linhas não testadas.

### 13.4. Atualização automática

A página deverá consumir os resultados reais gerados pela ferramenta de cobertura.

Implementar:

- Integração com o relatório de cobertura.
- Atualização após cada execução.
- Histórico de execuções.
- Data e horário da última atualização.
- Indicadores de testes aprovados e reprovados.
- Atualização dos gráficos.

Não utilizar dados fictícios ou números fixos.

### 13.5. Botão para executar testes

Criar um botão chamado:

**Executar testes**

Ao clicar:

1. Acionar o processo de testes pelo backend.
2. Executar a suíte configurada.
3. Exibir o andamento da execução.
4. Apresentar testes aprovados e reprovados.
5. Atualizar os indicadores de cobertura.
6. Atualizar o histórico.
7. Disponibilizar o relatório detalhado.

A execução deverá ser protegida, autorizada e realizada em ambiente seguro.

Não permitir que usuários comuns executem comandos arbitrários no servidor.

Evite execuções simultâneas conflitantes e implemente tratamento de erros e timeout.

### 13.6. Relatórios

Disponibilizar opções para:

- Consultar cobertura geral.
- Consultar cobertura por módulo.
- Consultar cobertura por arquivo.
- Visualizar linhas não testadas.
- Consultar histórico.
- Abrir o relatório HTML detalhado.
- Exportar resultados.

### 13.7. Critérios de aprovação

A página estará concluída quando:

- Estiver integrada ao menu administrativo.
- A rota estiver funcionando.
- Os dados forem reais.
- A cobertura for atualizada automaticamente.
- Os filtros funcionarem.
- O botão de execução funcionar.
- Os resultados forem armazenados e consultáveis.
- O acesso estiver protegido.
- A interface funcionar em computadores e dispositivos móveis.

Preserve a arquitetura e o padrão visual já existentes no projeto.

# 14. CRITÉRIOS OBRIGATÓRIOS DE CONCLUSÃO

Considere o trabalho concluído somente quando:

1. A opção de adicionar disciplinas aos professores estiver funcionando.
2. Todas as telas tiverem sido auditadas.
3. Todos os botões tiverem sido verificados.
4. Publicar provas estiver funcionando.
5. Visualizar disciplinas estiver funcionando.
6. Corrigir provas estiver funcionando.
7. Frontend, backend e banco estiverem comunicando corretamente.
8. Os testes unitários estiverem passando.
9. Os testes de integração estiverem passando.
10. Os principais testes E2E estiverem aprovados.
11. Statements atingirem pelo menos 80%.
12. Branches atingirem pelo menos 80%.
13. Functions atingirem pelo menos 80%.
14. Lines atingirem pelo menos 80%.
15. O relatório HTML estiver sendo gerado automaticamente.
16. O Painel de Testes e Cobertura estiver integrado ao sistema.
17. O botão de executar testes estiver funcionando com segurança.
18. O histórico das execuções estiver disponível.
19. Os resultados apresentados forem comprovadamente reais.

Se algum critério não puder ser atendido, informe claramente o motivo e não declare o projeto totalmente aprovado.

# 15. RELATÓRIO FINAL DA EXECUÇÃO

Ao terminar, apresente:

### Diagnóstico
- Problemas encontrados.
- Funcionalidades incompletas.
- Erros de comunicação.
- Problemas de banco de dados.
- Falhas de segurança identificadas.

### Correções
- Arquivos modificados.
- Funcionalidades corrigidas.
- Funcionalidades implementadas.
- Rotas criadas ou corrigidas.
- Serviços atualizados.

### Testes
- Testes unitários executados.
- Testes de integração executados.
- Testes E2E executados.
- Quantidade de testes aprovados.
- Quantidade de testes reprovados.
- Testes pendentes.

### Cobertura
- Statements.
- Branches.
- Functions.
- Lines.
- Cobertura por módulo.
- Módulos com cobertura insuficiente.

### Entregáveis
- Localização do arquivo `relatorio-testes.html`.
- Localização da página Painel de Testes e Cobertura.
- Comandos para executar os testes.
- Configuração da ferramenta de cobertura.
- Histórico das execuções.
- Pendências que ainda precisam ser resolvidas.

---

# REGRA PRINCIPAL — EXECUÇÃO OBRIGATÓRIA

Trabalhe diretamente no código existente.

Respeite a arquitetura atual e preserve as funcionalidades que já estão funcionando.

Não faça alterações desnecessárias.

Não simule resultados.

Não marque tarefas como concluídas sem comprovação.

Não utilize dados fictícios para preencher os indicadores.

Não aumente artificialmente a cobertura excluindo arquivos importantes.

Execute, valide e comprove cada correção antes de declarar o sistema aprovado.

Se encontrar problemas, corrija-os e execute novamente os testes.

**OBJETIVO FINAL: ENTREGAR UM SISTEMA FUNCIONAL, AUDITADO, COM AS FUNCIONALIDADES CORRIGIDAS, TESTES AUTOMATIZADOS, COBERTURA MÍNIMA DE 80% EM TODAS AS MÉTRICAS E UM PAINEL ADMINISTRATIVO PARA CONSULTAR, EXECUTAR E ACOMPANHAR OS TESTES CONTINUAMENTE.**