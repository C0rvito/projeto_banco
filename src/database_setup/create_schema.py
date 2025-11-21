import sqlite3
import os
from pathlib import Path

def create_database_schema():
    """
    Cria o arquivo do banco de dados e todas as tabelas necessárias com base na arquitetura Mestra-Detalhes
    """

db_path = Path(__file__).resolve().parent.parent.parent / "database" / "experimentos.db"

# Garante que o diretório 'database' exista
db_path.parent.mkdir(parents=True, exist_ok=True)

print(f"Iniciando a criação do banco de dados em: {db_path}")

sql_create_tables = """
PRAGMA foreign_keys = ON; -- Habilita a checagem de chaves estrangeiras

CREATE TABLE IF NOT EXISTS grupos (
    id_grupo INTEGER PRIMARY KEY,
    nome_grupo TEXT NOT NULL UNIQUE    
);

CREATE TABLE IF NOT EXISTS experimentos_master (
    id_experimento INTEGER PRIMARY KEY,
    id_grupo INTEGER NOT NULL,
    data_experimento TEXT,
    tipo_ensaio TEXT NOT NULL,
    id_detalhe_ensaio INTEGER NOT NULL,
    FOREIGN KEY (id_grupo) REFERENCES grupos (id_grupo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS detalhes_agonistas (
    id_agonista INTEGER PRIMARY KEY,
    id_animal INTEGER,
    condicao TEXT,
    arquivo_de_resultado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS detalhes_cryptococcus (
    id_cryptococcus INTEGER PRIMARY KEY,
    id_animal INTEGER,
    condicao TEXT,
    arquivo_de_resultado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS detalhes_fagocitose (
    id_fagocitose INTEGER PRIMARY KEY,
    id_animal INTEGER,
    condicao TEXT,
    arquivo_de_resultado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS detalhes_imunofenotipagem (
    id_imunofenotipagem INTEGER PRIMARY KEY,
    id_animal INTEGER,
    condicao TEXT,
    arquivo_de_resultado TEXT NOT NULL
);

"""

conn = None
try:
    # conecta com o banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 'executescript permite rodar múltiplos comandos SQL de uma vez
    cursor.executescript(sql_create_tables)

    # confirma as mudanças no banco de dados
    conn.commit()
    print("Esquema do banco de dados criado com sucesso!")

except sqlite3.Error as e:
    print(f"Erro ao criar o bando de dados: {e}")
    if conn:
        conn.rollback() # Desfaz qualquer mudança em caso de erro

finally:
    if conn:
        conn.close() # Sempre fecha a conexão
        print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    create_database_schema()