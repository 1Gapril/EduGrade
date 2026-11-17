# AUDITORIA COMPLETA, TESTES FUNCIONAIS E CORREÇÃO AUTOMÁTICA — EDUGRADE

## 1. PAPEL DO AGENTE

Você será o engenheiro de software sênior responsável pela auditoria técnica, funcional e estrutural do sistema EduGrade.

Sua missão não é apenas analisar o código ou apresentar uma lista de problemas.

Você deverá:

1. Examinar todo o projeto.
2. Identificar tudo que foi implementado.
3. Verificar se cada funcionalidade realmente funciona.
4. Identificar funcionalidades incompletas ou inexistentes.
5. Testar a comunicação entre frontend, backend, API, banco de dados e serviços.
6. Corrigir os problemas encontrados.
7. Criar e executar testes automatizados.
8. Reexecutar os testes após cada correção.
9. Repetir o processo até atingir os critérios de aprovação.
10. Gerar um relatório final com evidências reais.

**REGRA PRINCIPAL: NÃO CONSIDERE UMA FUNCIONALIDADE CONCLUÍDA APENAS PORQUE EXISTE UMA TELA, BOTÃO, ROTA OU FUNÇÃO NO CÓDIGO. ELA PRECISA FUNCIONAR DE PONTA A PONTA.**

---

## 2. DIAGNÓSTICO COMPLETO DO PROJETO

Antes de realizar alterações:

- Analise toda a estrutura de pastas.
- Leia a documentação existente.
- Identifique a linguagem e os frameworks utilizados.
- Identifique frontend e backend.
- Identifique todas as APIs.
- Identifique os serviços.
- Identifique o banco de dados.
- Analise modelos, entidades e relacionamentos.
- Analise autenticação e autorização.
- Identifique todas as funcionalidades implementadas.
- Identifique funcionalidades parcialmente implementadas.
- Identifique funções sem utilização.
- Identifique botões sem ação.
- Identifique endpoints sem integração.
- Identifique erros de comunicação.
- Identifique problemas de persistência.
- Identifique duplicações e inconsistências.
- Verifique os testes existentes e a cobertura atual.

Não substitua a arquitetura existente sem necessidade.

Não apague funcionalidades que já funcionam.

Não crie implementações duplicadas.

Preserve os dados e as configurações existentes.

Antes de mudanças estruturais ou migrações com risco de perda de dados, apresente o plano e solicite autorização.

---

## 3. AUDITORIA DE TODAS AS FUNCIONALIDADES

Faça um levantamento de todas as funcionalidades encontradas no sistema.

Para cada funcionalidade, verifique:

1. Se existe no frontend.
2. Se possui comunicação com o backend.
3. Se possui endpoint ou serviço correspondente.
4. Se valida os dados corretamente.
5. Se utiliza o banco de dados corretamente.
6. Se salva os dados.
7. Se recupera os dados salvos.
8. Se apresenta mensagens de sucesso e erro.
9. Se respeita as permissões do usuário.
10. Se possui testes automatizados.
11. Se funciona no fluxo completo.

Classifique cada funcionalidade como:

- APROVADA: funciona e foi testada.
- PARCIAL: funciona apenas em parte.
- REPROVADA: existe, mas apresenta falhas.
- AUSENTE: não foi implementada.
- BLOQUEADA: depende de configuração ou serviço externo indisponível.

Não marque nenhuma funcionalidade como aprovada sem evidência de execução.

---

## 4. AUDITORIA DE COMUNICAÇÃO ENTRE TODAS AS CAMADAS

Revise todos os pontos de comunicação do sistema.

### Frontend
- Eventos dos botões.
- Formulários.
- Validações.
- Estados de carregamento.
- Tratamento de erros.
- Atualização das telas.
- Consumo das APIs.
- Autenticação.
- Controle de sessão.

### Backend
- Rotas.
- Controllers.
- Services.
- Repositories.
- Models.
- Schemas.
- Validações.
- Tratamento de exceções.
- Regras de negócio.

### Banco de dados
- Conexões.
- Consultas.
- Inserções.
- Atualizações.
- Exclusões.
- Relacionamentos.
- Chaves estrangeiras.
- Integridade referencial.
- Migrações.
- Persistência real.

### Integrações
- Serviços externos.
- Serviço de IA.
- OCR.
- Upload de documentos.
- Geração de PDF.
- Armazenamento de arquivos.

Verifique se todas as camadas estão realmente conectadas.

Identifique chamadas incorretas, endpoints incompatíveis, nomes de campos diferentes, erros de serialização, problemas de autenticação e falhas de sincronização.

---

## 5. AUDITORIA ESPECÍFICA DO PROFESSOR

Faça uma revisão aprofundada do painel do professor.

### Associação de disciplinas

Verifique obrigatoriamente:

- Se existe opção de adicionar disciplina ao professor.
- Se existe opção de remover disciplina.
- Se o administrador consegue associar disciplinas.
- Se o professor consegue visualizar suas disciplinas.
- Se as disciplinas associadas ficam salvas no banco.
- Se a associação permanece após sair e entrar novamente.
- Se o professor consegue visualizar somente as disciplinas autorizadas.
- Se as turmas correspondentes aparecem corretamente.
- Se a associação respeita o período acadêmico.

Se não existir funcionalidade para adicionar disciplinas ao professor, implemente-a respeitando a arquitetura e as permissões existentes.

### Outras funcionalidades

Teste:

- Visualização de disciplinas.
- Visualização de turmas.
- Consulta de alunos.
- Criação de avaliações.
- Criação de provas.
- Edição de provas.
- Exclusão de provas, respeitando as regras de negócio.
- Cadastro de questões.
- Cadastro de gabaritos.
- Distribuição de pontuação.
- Impressão de provas.
- Geração de PDF.
- Upload de provas respondidas.
- Correção assistida por IA.
- Revisão manual.
- Aprovação da correção.
- Publicação de notas.

---

## 6. AUDITORIA DO FLUXO DE PROVAS

Execute o fluxo completo:

1. Professor realiza login.
2. Professor acessa uma disciplina autorizada.
3. Professor seleciona uma turma.
4. Professor cria uma avaliação.
5. Professor cadastra questões.
6. Professor define pontuações.
7. Professor cadastra o gabarito.
8. Sistema valida a soma dos pontos.
9. Professor salva a prova.
10. Sistema persiste os dados.
11. Professor consulta novamente a prova.
12. Professor gera o PDF.
13. Professor imprime ou visualiza o documento.
14. Prova respondida é enviada ao sistema.
15. Sistema processa o documento.
16. IA sugere a correção.
17. Sistema apresenta justificativas e nível de confiança.
18. Professor revisa a correção.
19. Professor aprova ou altera a pontuação.
20. Professor publica as notas.
21. Aluno autorizado consegue consultar sua nota.

Verifique se os dados permanecem consistentes durante todo o processo.

A IA não poderá publicar notas automaticamente.

A aprovação final deverá ser realizada pelo professor.

---

## 7. AUDITORIA DO PAINEL DO ALUNO

Verifique:

- Login.
- Consulta de notas.
- Consulta de disciplinas.
- Consulta de avaliações.
- Histórico acadêmico.
- Frequência.
- Atualização das informações.
- Permissões.
- Proteção dos dados de outros alunos.

Tente acessar dados de outro aluno utilizando uma conta comum.

O sistema deverá impedir esse acesso no backend, não apenas esconder informações no frontend.

---

## 8. AUDITORIA DO PAINEL ADMINISTRATIVO

Verifique:

- Cadastro de alunos.
- Cadastro de professores.
- Cadastro de administradores.
- Edição de usuários.
- Desativação de usuários.
- Cadastro de disciplinas.
- Cadastro de turmas.
- Associação de professores às disciplinas.
- Associação de disciplinas às turmas.
- Gerenciamento de períodos acadêmicos.
- Gerenciamento de permissões.
- Consulta de registros de auditoria.

Teste todas as operações e sua persistência.

---

## 9. TESTES UNITÁRIOS

Crie ou amplie os testes unitários de acordo com a arquitetura existente.

Teste:

- Autenticação.
- Autorização.
- Validações.
- Regras acadêmicas.
- Serviços.
- Repositórios.
- Relacionamentos.
- Associação de disciplinas.
- Cadastro de professores.
- Cadastro de alunos.
- Criação de avaliações.
- Criação de questões.
- Cálculo de pontuação.
- Geração de notas.
- Publicação de resultados.
- Processamento de provas.
- Correção assistida por IA.
- Auditoria.

Utilize mocks para serviços externos, como IA, OCR e provedores de terceiros, quando apropriado.

Os testes devem verificar comportamentos reais do código, e não apenas executar funções sem validar seus resultados.

### META OBRIGATÓRIA

**Atingir pelo menos 80% de cobertura de código.**

Configure a ferramenta de cobertura adequada à stack existente.

Se o projeto utilizar Python e pytest, utilize pytest-cov quando compatível.

Configure cobertura para:

- Statements.
- Branches.
- Functions, quando suportado.
- Linhas relevantes do código.

Evite excluir módulos apenas para aumentar artificialmente a cobertura.

Não utilize mocks excessivos que escondam defeitos da implementação.

---

## 10. TESTES DE INTEGRAÇÃO

Crie testes que validem a comunicação real entre os componentes.

Teste:

- Frontend e API.
- API e serviços.
- Serviços e banco de dados.
- Autenticação e permissões.
- Cadastro e persistência.
- Associação de disciplinas.
- Criação e consulta de provas.
- Upload e processamento de documentos.
- Correção e revisão.
- Publicação de notas.

Utilize banco de dados de teste isolado.

Não utilize dados reais de produção.

---

## 11. TESTES FUNCIONAIS E DE INTERFACE

Verifique todos os botões e ações disponíveis.

Para cada botão:

- Identifique sua finalidade.
- Verifique se possui evento.
- Verifique se chama a função correta.
- Verifique se realiza a operação esperada.
- Verifique se apresenta retorno ao usuário.
- Verifique se trata erros.
- Verifique se atualiza a interface.

Procure especialmente:

- Botões sem ação.
- Links quebrados.
- Formulários que não salvam.
- Modais que não abrem.
- Menus que não funcionam.
- Dados que desaparecem após atualização.
- Telas que apresentam informações incorretas.
- Erros no console.
- Erros de requisição.

Quando houver infraestrutura adequada, utilize testes E2E com Playwright ou ferramenta equivalente.

---

## 12. PÁGINA DE CONSULTA DE TESTES E COBERTURA

Crie uma página administrativa de qualidade do sistema, caso ainda não exista.

Nome sugerido:

**Painel de Qualidade e Cobertura de Testes**

Essa página deverá apresentar:

- Total de testes.
- Testes aprovados.
- Testes reprovados.
- Testes ignorados.
- Percentual de cobertura.
- Cobertura de linhas.
- Cobertura de branches.
- Data da última execução.
- Histórico das execuções.
- Módulos testados.
- Módulos sem testes.
- Falhas identificadas.
- Erros encontrados.
- Status geral da qualidade.

Inclua acesso ao relatório HTML detalhado de cobertura.

O relatório deverá ser gerado automaticamente após a execução dos testes.

Não apresente números fictícios ou resultados simulados como se fossem reais.

Se não houver uma execução válida, mostre que os dados estão indisponíveis.

Restrinja essa página aos usuários administrativos autorizados.

---

## 13. CORREÇÃO AUTOMÁTICA DOS PROBLEMAS

Depois do diagnóstico:

1. Organize os problemas por gravidade.
2. Corrija primeiro os erros críticos.
3. Corrija os problemas de comunicação.
4. Corrija as funcionalidades incompletas.
5. Implemente as funcionalidades ausentes necessárias aos requisitos.
6. Corrija problemas de persistência.
7. Corrija problemas de autenticação e autorização.
8. Corrija os erros de interface.
9. Amplie os testes.
10. Execute novamente todos os testes afetados.

Não se limite a sugerir correções.

Implemente as correções no código sempre que forem seguras e estiverem dentro do escopo autorizado.

Se encontrar uma operação destrutiva, migração arriscada, necessidade de credenciais ou dependência externa indisponível, registre o bloqueio e solicite autorização ou configuração.

Não desative testes para obter aprovação.

Não remova funcionalidades para eliminar erros.

Não altere regras de negócio sem justificativa.

---

## 14. CICLO OBRIGATÓRIO DE VALIDAÇÃO

Utilize o seguinte ciclo:

DIAGNÓSTICO → TESTE → IDENTIFICAÇÃO → CORREÇÃO → NOVO TESTE → VALIDAÇÃO.

Repita esse ciclo até:

- Não existirem falhas críticas conhecidas.
- Todas as funcionalidades obrigatórias estarem implementadas.
- Todas as funcionalidades aprovadas terem evidências de execução.
- Os testes unitários e de integração passarem.
- A cobertura mínima de 80% ser atingida.
- O relatório HTML ser gerado.
- A comunicação entre as camadas estar validada.
- O sistema estar executável.

Se uma correção provocar uma nova falha, corrija-a antes de concluir.

Não pare após encontrar o primeiro problema.

Não encerre o trabalho apenas porque apresentou um relatório.

---

## 15. AUTOMAÇÃO E CI/CD

Verifique o pipeline existente.

Configure ou corrija o GitHub Actions para:

1. Instalar dependências.
2. Preparar o ambiente de testes.
3. Executar testes unitários.
4. Executar testes de integração.
5. Calcular cobertura.
6. Exigir pelo menos 80% de cobertura.
7. Gerar relatório HTML.
8. Armazenar relatórios como artefatos.
9. Falhar automaticamente se os critérios obrigatórios não forem atendidos.

Não exponha senhas, tokens ou arquivos de ambiente.

---

## 16. RELATÓRIOS OBRIGATÓRIOS

Crie a pasta:

docs/auditoria/

Gere os seguintes documentos:

### RELATORIO_DIAGNOSTICO.md
Estado inicial do projeto e problemas encontrados.

### RELATORIO_FUNCIONALIDADES.md
Lista de funcionalidades e respectivos resultados dos testes.

### RELATORIO_COMUNICACAO.md
Validação das integrações entre frontend, backend, API, serviços e banco.

### RELATORIO_CORRECOES.md
Problemas identificados, alterações realizadas e resultados.

### RELATORIO_TESTES.md
Quantidade de testes, aprovados, reprovados e ignorados.

### RELATORIO_COBERTURA.md
Percentuais reais de cobertura e módulos analisados.

### RELATORIO_FINAL.md
Resultado consolidado da auditoria.

Todos os relatórios deverão refletir a execução real do projeto.

---

## 17. CRITÉRIOS FINAIS DE APROVAÇÃO

O EduGrade somente poderá ser considerado aprovado quando:

- [ ] Backend funcional.
- [ ] Frontend funcional.
- [ ] Banco de dados persistente.
- [ ] Login dos três perfis funcionando.
- [ ] Permissões validadas.
- [ ] Associação de disciplinas aos professores funcionando.
- [ ] Consulta de disciplinas funcionando.
- [ ] Consulta de turmas funcionando.
- [ ] Criação de avaliações funcionando.
- [ ] Publicação de provas funcionando.
- [ ] Cadastro de gabaritos funcionando.
- [ ] Geração de PDF funcionando.
- [ ] Upload de provas funcionando.
- [ ] Correção assistida por IA funcionando ou integração externa devidamente identificada como bloqueada.
- [ ] Revisão humana obrigatória funcionando.
- [ ] Publicação de notas funcionando.
- [ ] Auditoria das operações funcionando.
- [ ] Botões e formulários testados.
- [ ] Comunicação entre todas as camadas validada.
- [ ] Testes unitários aprovados.
- [ ] Testes de integração aprovados.
- [ ] Testes funcionais aprovados.
- [ ] Cobertura mínima de 80%.
- [ ] Relatório HTML gerado.
- [ ] Painel de qualidade atualizado.
- [ ] GitHub Actions validado.
- [ ] Nenhuma falha crítica conhecida.

---

## 18. INSTRUÇÃO FINAL — NÃO ENCERRAR ANTES DA CONCLUSÃO

Execute a auditoria no projeto real.

Não invente resultados.

Não simule testes.

Não marque funcionalidades como concluídas sem executá-las.

Não considere a existência de um botão como comprovação de funcionamento.

Não interrompa o processo após gerar os relatórios iniciais.

Corrija os problemas identificados e execute novamente os testes.

**Continue trabalhando até concluir todas as correções seguras possíveis e atingir os critérios de aprovação.**

Se houver bloqueios externos que não possam ser resolvidos sem credenciais, autorização ou intervenção humana, documente exatamente o que falta e prossiga com todas as outras tarefas.

Ao terminar, apresente:

1. Estado inicial do projeto.
2. Quantidade de problemas encontrados.
3. Quantidade de problemas corrigidos.
4. Funcionalidades implementadas.
5. Funcionalidades testadas e aprovadas.
6. Funcionalidades ainda bloqueadas.
7. Quantidade de testes executados.
8. Quantidade de testes aprovados e reprovados.
9. Percentual real de cobertura.
10. Localização do relatório HTML.
11. Situação do CI/CD.
12. Pendências que dependem de intervenção humana.
13. Conclusão final sobre a qualidade do EduGrade.

**OBJETIVO: ENTREGAR O EDUGRADE FUNCIONAL, INTEGRADO, TESTADO, CORRIGIDO E COM PELO MENOS 80% DE COBERTURA DE TESTES, COM EVIDÊNCIAS REAIS DE VALIDAÇÃO.**