import csv
import os
from datetime import datetime


def detectar_tipo_valores(valores):
    tipos = set()

    for valor in valores:
        valor = valor.strip()

        if valor == "":
            continue

        try:
            int(valor)
            tipos.add("BIGINT")
            continue
        except ValueError:
            pass

        try:
            float(valor)
            tipos.add("NUMERIC")
            continue
        except ValueError:
            pass

        try:
            datetime.fromisoformat(valor)
            tipos.add("TIMESTAMP")
            continue
        except ValueError:
            pass

        tipos.add("TEXT")

    if not tipos:
        return "TEXT"

    if tipos == {"BIGINT"}:
        return "BIGINT"

    if tipos <= {"BIGINT", "NUMERIC"}:
        return "NUMERIC"

    if tipos == {"TIMESTAMP"}:
        return "TIMESTAMP"

    return "TEXT"


def gerar_schema(pasta):
    arquivos_csv = sorted(
        arquivo
        for arquivo in os.listdir(pasta)
        if arquivo.lower().endswith(".csv")
    )

    comandos = []

    for arquivo in arquivos_csv:
        caminho = os.path.join(pasta, arquivo)

        with open(caminho, "r", encoding="utf-8") as f:
            leitor = csv.DictReader(f)

            valores_por_coluna = {
                coluna: []
                for coluna in leitor.fieldnames
            }

            for linha in leitor:
                for coluna, valor in linha.items():
                    valores_por_coluna[coluna].append(valor)

        nome_tabela = os.path.splitext(arquivo)[0]

        colunas_sql = []

        for coluna, valores in valores_por_coluna.items():
            tipo = detectar_tipo_valores(valores)
            colunas_sql.append(f'    "{coluna}" {tipo}')

        comando = (
            f'CREATE TABLE "{nome_tabela}" (\n'
            + ",\n".join(colunas_sql)
            + "\n);"
        )

        comandos.append(comando)

    caminho_saida = os.path.join(pasta, "schema2.sql")

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("\n\n".join(comandos))

    print(f"Schema gerado com sucesso: {caminho_saida}")
    print(f"Tabelas encontradas: {len(arquivos_csv)}")


pasta = "."

gerar_schema(pasta)