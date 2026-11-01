# Roteiro de Apresentação - A3
## EduGrade — Sistema de Gestão e Desempenho Acadêmico com IA

### 1. Capa
* **Projeto:** EduGrade
* **Função DevOps/Documentação:** Gabriel Ferreira — RA 325140970
* **Integrantes do Grupo:** [Adicione o nome e RA dos outros integrantes aqui]

### 2. Problema
* Dificuldade na gestão de desempenho acadêmico, aplicação e correção de provas em larga escala de forma ágil e justa.

### 3. Objetivo
* Desenvolver uma plataforma integrada que automatize processos de avaliação e forneça análise preditiva de desempenho de alunos utilizando Inteligência Artificial.

### 4. ODS 4 - Educação de Qualidade
* Como o EduGrade se alinha: Garantir o acesso à educação inclusiva, promovendo ferramentas tecnológicas que otimizam o tempo do docente e geram feedbacks personalizados para a evolução do aluno.

### 5. Público-alvo
* Instituições de ensino de grande porte, professores, coordenadores pedagógicos e estudantes de graduação/pós-graduação.

### 6. Arquitetura
* **Backend:** Python / FastAPIs
* **Frontend:** HTML, CSS, JavaScript
* **Integração:** Scripts de automação e processamento de dados.

### 7. Banco de Dados
* [Descrever brevemente se utilizam SQLite, PostgreSQL ou similar para guardar notas e cadastros]

### 8. Funcionalidades do Aluno
* Visualização de dashboard acadêmico.
* Consulta de notas e relatórios de desempenho gerados pela IA.

### 9. Funcionalidades do Professor
* Cadastro de turmas, criação de avaliações e visualização de métricas consolidadas da turma.

### 10. Criação e Impressão das Provas
* Módulo de geração de exames em formato padronizado com suporte a exportação.

### 11. Correção Assistida por IA
* Utilização de OCR (Optical Character Recognition) e modelos de linguagem para leitura, interpretação e atribuição preliminar de notas a questões discursivas e objetivas.

### 12. Segurança
* Proteção de rotas, chaves de ambiente criptografadas (`.env`) e controle de acesso baseado em funções.

### 13. Testes
* Testes unitários cobrindo as principais regras de negócio localizados na pasta `tests/unit`.

### 14. Cobertura
* Monitoramento de cobertura de código para garantir confiabilidade nas alterações.

### 15. CI/CD
* Pipeline automatizado utilizando GitHub Actions para validação e execução de testes a cada Pull Request enviado.

### 16. Resultados
* Otimização no tempo de correção de avaliações e relatórios precisos sobre os pontos de dificuldade da turma.

### 17. Conclusão
* O EduGrade moderniza a gestão educacional unindo automação DevOps e IA para focar no que mais importa: o aprendizado real do estudante.
