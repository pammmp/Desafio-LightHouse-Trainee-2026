"""
Projeto: Desafio Lighthouse
Questão 3 - Carregamento de dados brutos no PostgreSQL

Objetivo:
Carregar todos os arquivos CSV de um diretório nas tabelas PostgreSQL
previamente criadas pelo arquivo schema.sql.

Entradas:
- Diretório com arquivos CSV.
- Banco PostgreSQL com schema previamente criado.

Saída:
- Registros carregados nas tabelas correspondentes.

Restrições:
- Nenhum valor é removido, corrigido ou transformado.
- A carga preserva os dados brutos das fontes originais.
"""

import os
import re
import sys
import subprocess
import unicodedata

# ============================================================
# ETAPA 1 - Padronização do nome do arquivo para a tabela destino
# ============================================================

def normalizar_identificador(nome, prefixo="tabela"):
    """
    Aplica a mesma padronização utilizada na geração do schema.
    """
    nome = unicodedata.normalize("NFKD", nome)
    nome = nome.encode("ascii", "ignore").decode("ascii")
    nome = nome.strip().lower()
    nome = re.sub(r"[^a-z0-9_]+", "_", nome)
    nome = re.sub(r"_+", "_", nome).strip("_")

    if not nome:
        nome = prefixo

    if nome[0].isdigit():
        nome = f"{prefixo}_{nome}"

    return nome

# ============================================================
# ETAPA 2 - Localização dos arquivos CSV disponíveis para carga
# ============================================================

def carregar_csvs(diretorio_csv):
    """
    Carrega todos os CSVs nas tabelas PostgreSQL já existentes.
    Nenhum dado é removido ou transformado.
    """
        # Identificação dos CSVs que serão carregados.
    arquivos_csv = sorted(
        arquivo
        for arquivo in os.listdir(diretorio_csv)
        if arquivo.lower().endswith(".csv")
    )

    if not arquivos_csv:
        raise FileNotFoundError("Nenhum arquivo CSV foi encontrado.")
    
        # Associação do nome do arquivo à tabela criada no schema.
    for arquivo_csv in arquivos_csv:
        caminho_csv = os.path.abspath(
            os.path.join(diretorio_csv, arquivo_csv)
        ).replace("\\", "/")

        nome_tabela = os.path.splitext(arquivo_csv)[0]
        nome_tabela = normalizar_identificador(nome_tabela)

        caminho_sql = caminho_csv.replace("'", "''")

        # Execução do \copy para carregamento em lote, sem transformar os dados.

        comando_copy = (
            f"\\copy {nome_tabela} "
            f"FROM '{caminho_sql}' "
            f"WITH (FORMAT CSV, HEADER TRUE)"
        )

        comando_psql = [
            "psql",
            "-v", "ON_ERROR_STOP=1",
            "-c", comando_copy
        ]

        resultado = subprocess.run(
            comando_psql,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        if resultado.returncode != 0:
            print(f"Erro ao carregar {arquivo_csv}:")
            print(resultado.stderr)
            sys.exit(1)

        print(f"Carregado com sucesso: {arquivo_csv}")

    print("Todos os CSVs foram carregados com sucesso.")

    # Confirmação da transação somente após a carga de cada arquivo.
if __name__ == "__main__":
    diretorio = sys.argv[1] if len(sys.argv) > 1 else "."
    carregar_csvs(diretorio)