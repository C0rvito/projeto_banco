import sqlite3
from pathlib import Path

dir_base = Path(__file__).resolve().parent.parent.parent

db_path = dir_base / "database" / "experimentos.db"

teste = db_path.parent

def conectaDB():
    """
    Cria e retorna uma conexão com o banco de dados. 
    """

    try:
        # Garante que pasta do banco exista
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados em {db_path}: {e}")
        return None

def escrita(sql_query: str, params: tuple) -> int:
    """
    Executa uma query de escrita (INSERT, UPDATE, DELETE) no banco de dados
    e retorna o ID da última linha inserida (lastrowid).
    
    Argumentos:
        sql_query (str): A string SQL (ex: "INSERT INTO ... (?, ?)")
        params (tuple): Uma tupla de valores para a query.
        
    Retorna:
        int: O ID da última linha inserida, ou None em caso de falha.
    """
    conn = None
    last_id = None
    try:
        # Usa a sua função para pegar a conexão
        conn = conectaDB() 
        if conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            conn.commit() # Salva (confirma) as mudanças
            last_id = cursor.lastrowid # Pega o ID da linha recém-criada
            
    except sqlite3.Error as e:
        print(f"Erro na query de escrita: {e}")
        if conn:
            conn.rollback() # Desfaz a mudança em caso de erro
    finally:
        if conn:
            conn.close() # Sempre fecha a conexão
            
    return last_id



def leitura(sql_query: str, params: tuple = ()) -> list[tuple[any, ...]]:
    """
    Executa uma query de leitura (SELECT) e retorna todos os resultados.
    
    Argumentos:
        sql_query (str): A string SQL (ex: "SELECT * FROM ... WHERE id = ?")
        params (tuple): Uma tupla de valores (opcional).
        
    Retorna:
        list: Uma lista de tuplas, onde cada tupla é uma linha do resultado.
              Retorna uma lista vazia em caso de falha ou se não houver resultados.
    """
    conn = None
    resultados = []
    try:
        # Usa a sua função para pegar a conexão
        conn = conectaDB() 
        if conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            resultados = cursor.fetchall() # Pega todos os resultados da consulta
            
    except sqlite3.Error as e:
        print(f"Erro na query de leitura: {e}")
    finally:
        if conn:
            conn.close()
            
    return resultados