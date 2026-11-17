# Instalar e configurar o OCR no Windows

Este guia instala o Tesseract OCR e o modelo de português necessários para
processar digitalizações de provas no EduGrade. Ter somente o executável não
basta: o idioma `por` também precisa estar instalado.

> Execute os comandos a partir da pasta raiz do projeto
> (`E:\Projetos GitHub\EduGrade` neste computador).

## 1. Instale o Tesseract OCR

1. Abra a página oficial dos instaladores para Windows:
   [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
2. Baixe o instalador de 64 bits recomendado pela página e execute-o.
3. Use a pasta padrão, se possível:
   `C:\Program Files\Tesseract-OCR`
4. Durante a instalação, escolha os dados adicionais de idioma e marque
   **Portuguese** (português). O arquivo instalado deve se chamar
   `por.traineddata`.
5. Termine a instalação. Se o Tesseract já estiver instalado, confira se a
   pasta `tessdata` contém `por.traineddata`; se não contiver, instale o pacote
   de idioma português antes de continuar.

## 2. Configure o EduGrade

Na raiz do projeto, abra o arquivo `.env`. Se ele ainda não existir, crie uma
cópia do modelo:

```powershell
Copy-Item .env.example .env
```

Edite a linha `TESSERACT_PATH` para apontar para o executável instalado:

```env
OCR_ENGINE=tesseract
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Se instalou o Tesseract em outra pasta, informe o caminho completo correto.
Não adicione aspas ao valor no `.env`.

O idioma `por` já é o padrão do processador de provas. Normalmente não é
necessário configurar `TESSDATA_PREFIX` quando o idioma foi instalado na pasta
padrão do Tesseract. Para uma instalação personalizada, defina essa variável
no Windows apontando para a pasta que contém os dados de idioma, reinicie o
terminal e o EduGrade e siga as instruções específicas do instalador.

## 3. Confira a instalação

Abra um **novo** PowerShell e execute:

```powershell
& 'C:\Program Files\Tesseract-OCR\tesseract.exe' --version
& 'C:\Program Files\Tesseract-OCR\tesseract.exe' --list-langs
```

O primeiro comando deve mostrar a versão do Tesseract. No resultado do segundo,
confirme que aparece:

```text
por
```

Se `por` não aparecer, o modelo de português não foi instalado ou não está na
pasta `tessdata` reconhecida pelo Tesseract. Volte à etapa 1 e instale os dados
de idioma. O comando de configuração do idioma não é substituído apenas por
adicionar a pasta do executável ao `PATH`.

Também é possível validar a configuração carregada pelo Python do projeto:

```powershell
.\venv\Scripts\python.exe -c "from backend.app.core.config import settings; import pytesseract; pytesseract.pytesseract.tesseract_cmd=settings.tesseract_path; print('Executável:', pytesseract.pytesseract.tesseract_cmd); print('Idiomas:', pytesseract.get_languages(config=''))"
```

Na lista impressa pelo Python também deve constar `por`. Se o ambiente virtual
ainda não existir, crie-o e instale as dependências antes:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Reinicie o EduGrade

Pare qualquer servidor já aberto com `Ctrl+C`. Na raiz do projeto, inicie-o
novamente para que carregue o caminho atualizado do `.env`:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Abra `http://localhost:8000/docs` para conferir se a API está disponível.
Processos iniciados antes da alteração do `.env` precisam ser reiniciados.

## 5. Teste o processamento de uma prova

1. Entre no EduGrade com um usuário autorizado a enviar provas.
2. Use uma prova de teste e envie o arquivo digitalizado pelo fluxo de
   submissão.
3. Solicite o processamento OCR da submissão. Na API, a rota é
   `POST /api/v1/exams/submissions/{submission_id}/process-ocr`; envie o token
   de acesso e substitua `{submission_id}` pelo identificador retornado no
   envio.
4. Uma resposta de sucesso confirma que o OCR conseguiu processar as páginas.
   Isso não garante, por si só, que as respostas manuscritas foram extraídas ou
   corrigidas corretamente: confira os resultados antes de publicar notas.

## Solução de problemas

### “Tesseract não encontrado”

- Confira se `TESSERACT_PATH` aponta para o arquivo `tesseract.exe`, não apenas
  para a pasta.
- Execute o teste da etapa 3 e reinicie o servidor depois de editar o `.env`.

### “Modelo de idioma 'por' do Tesseract não encontrado”

- Execute `--list-langs` no executável configurado e confirme que `por` aparece.
- Instale o modelo de português; confira também a localização de `tessdata`.
- Se os dados estiverem em uma pasta personalizada, configure
  `TESSDATA_PREFIX` no Windows e reinicie o terminal e o servidor.

### O endpoint retorna erro 502

Consulte a mensagem detalhada na resposta da API e verifique primeiro o
executável e os idiomas com os comandos da etapa 3. O PDF precisa conter páginas
legíveis; digitalizações desfocadas ou muito inclinadas podem reduzir a
qualidade do reconhecimento.
