
from pathlib import Path
import ast
import re

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "backend" / "app" / "models"
SAIDA = RAIZ / "docs" / "DER_EDUGRADE.md"


def obter_atributos(classe):
    for item in classe.body:
        if isinstance(item, ast.Assign):
            nomes = [
                alvo.id for alvo in item.targets
                if isinstance(alvo, ast.Name)
            ]
            valor = item.value
        elif isinstance(item, ast.AnnAssign):
            nomes = (
                [item.target.id]
                if isinstance(item.target, ast.Name)
                else []
            )
            valor = item.value
        else:
            continue

        if nomes and valor is not None:
            yield nomes[0], valor


def obter_tipo(texto):
    tipos = [
        (r"\b(BigInteger|SmallInteger|Integer)\b", "int"),
        (r"\b(Boolean)\b", "boolean"),
        (r"\b(DateTime|TIMESTAMP)\b", "datetime"),
        (r"\b(Date)\b", "date"),
        (r"\b(Float|Numeric|DECIMAL)\b", "decimal"),
        (r"\b(JSONB|JSON)\b", "json"),
        (r"\b(Text)\b", "text"),
        (r"\b(UUID)\b", "uuid"),
    ]

    for padrao, tipo in tipos:
        if re.search(padrao, texto):
            return tipo

    return "string"


def obter_opcao(chamada, nome):
    for argumento in chamada.keywords:
        if argumento.arg == nome:
            if isinstance(argumento.value, ast.Constant):
                return argumento.value.value
    return None


def extrair_modelos():
    tabelas = {}
    relacionamentos = []

    for arquivo in sorted(MODELOS.glob("*.py")):
        if arquivo.name == "__init__.py":
            continue

        arvore = ast.parse(
            arquivo.read_text(encoding="utf-8"),
            filename=str(arquivo),
        )

        for classe in arvore.body:
            if not isinstance(classe, ast.ClassDef):
                continue

            atributos = list(obter_atributos(classe))
            nome_tabela = None

            for nome, valor in atributos:
                if (
                    nome == "__tablename__"
                    and isinstance(valor, ast.Constant)
                    and isinstance(valor.value, str)
                ):
                    nome_tabela = valor.value

            if not nome_tabela:
                continue

            campos = []

            for nome, valor in atributos:
                if not isinstance(valor, ast.Call):
                    continue

                funcao = ast.unparse(valor.func)

                if funcao not in ("mapped_column", "Column"):
                    continue

                texto = ast.unparse(valor)
                pk = obter_opcao(valor, "primary_key") is True
                unique = obter_opcao(valor, "unique") is True
                nullable = obter_opcao(valor, "nullable")

                referencias = re.findall(
                    r"""ForeignKey\(\s*['"]([A-Za-z_]\w*)\.[^'"]+['"]""",
                    texto,
                )

                fk = bool(referencias)
                tipo = obter_tipo(texto)

                # Tipo declarado na anotação Mapped[...] ou similar
                for item in classe.body:
                    if (
                        isinstance(item, ast.AnnAssign)
                        and isinstance(item.target, ast.Name)
                        and item.target.id == nome
                    ):
                        anotacao = ast.unparse(item.annotation)
                        if "int" in anotacao:
                            tipo = "int"
                        elif "datetime" in anotacao:
                            tipo = "datetime"
                        elif "bool" in anotacao:
                            tipo = "boolean"
                        elif "float" in anotacao:
                            tipo = "decimal"
                        elif "UUID" in anotacao:
                            tipo = "uuid"

                marcador = ""
                if pk:
                    marcador = "PK"
                elif fk:
                    marcador = "FK"
                elif unique:
                    marcador = "UK"

                campo_seguro = re.sub(r"\W", "_", nome)

                campos.append(
                    f"        {tipo} {campo_seguro}"
                    + (f" {marcador}" if marcador else "")
                )

                for destino in referencias:
                    relacionamentos.append({
                        "origem": destino,
                        "destino": nome_tabela,
                        "campo": nome,
                        "opcional": nullable is True,
                        "unico": unique or pk,
                    })

            tabelas[nome_tabela] = campos

    return tabelas, relacionamentos


def gerar_der():
    tabelas, relacionamentos = extrair_modelos()

    linhas = [
        "# DER — EduGrade",
        "",
        "Diagrama gerado a partir dos modelos SQLAlchemy.",
        "",
        "```mermaid",
        "erDiagram",
    ]

    for tabela, campos in sorted(tabelas.items()):
        linhas.append(f"    {tabela} {{")
        linhas.extend(campos)
        linhas.append("    }")

    validos = 0

    for rel in relacionamentos:
        origem = rel["origem"]
        destino = rel["destino"]

        if origem not in tabelas or destino not in tabelas:
            continue

        # O lado direito representa os registros que referenciam a FK.
        # nullable=True permite ausência do vínculo.
        if rel["unico"]:
            cardinalidade = "o|"
        else:
            cardinalidade = "o{"

        # nullable na FK influencia a participação do lado pai.
        lado_pai = "o|" if rel["opcional"] else "||"

        linhas.append(
            f'    {origem} {lado_pai}--{cardinalidade} '
            f'{destino} : "{rel["campo"]}"'
        )
        validos += 1

    linhas.extend([
        "```",
        "",
        "> DER gerado automaticamente. As cardinalidades são "
        "aproximações baseadas em FK, nullable e unique. "
        "Restrições compostas e regras de negócio exigem revisão.",
        "",
    ])

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("\n".join(linhas), encoding="utf-8")

    print(f"Tabelas encontradas: {len(tabelas)}")
    print(f"Relacionamentos representados: {validos}")
    print(f"Arquivo gerado: {SAIDA}")


if __name__ == "__main__":
    gerar_der()
