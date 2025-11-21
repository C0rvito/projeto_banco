import pandas as pd
from pathlib import Path
import sqlite3
from funcoes.db_tools import conectaDB, escrita, leitura

script_dir = Path(__file__).resolve().parent

mapa_csv = script_dir / "mapeamento.csv"

def popularDB():
    """
    Função principal do ETL.
    Lê o CSV de mapeamento e popula o banco de dados.
    """
    print("Iniciando o script de ETL para popular o banco...")
    
    # 1. Ler o mapa de arquivos
    print(f"Lendo o mapa de arquivos em: {mapa_csv}")
    try:
        df_mapa = pd.read_csv(mapa_csv)
        # Lida com IDs de animais vazios (que o Pandas lê como NaN)
        # Substitui NaN por None, que o SQLite entende como NULL.
        df_mapa['id_animal'] = df_mapa['id_animal'].astype('Int64').where(df_mapa['id_animal'].notna(), None)
        
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{mapa_csv.name}' não encontrado em {script_dir}.")
        print("Verifique o nome e a localização do arquivo.")
        return
    except KeyError:
        print("ERRO: O 'mapeamento.csv' não contém as colunas esperadas.")
        print("Verifique se ele tem 'nome_grupo', 'tipo_ensaio', 'id_animal', 'caminho_arquivo'.")
        return

    print(f"Encontradas {len(df_mapa)} linhas no mapa.")

    query_grupos = "SELECT id_grupo, nome_grupo FROM grupos"

    try:
        resultados_grupos = leitura(query_grupos)
    except Exception as e:
        print(f"Falha ao ler a tabela 'grupos'. Erro: {e}")
        return

    # Transforma a lista de tuplas em um dicionário rápido
    # Isso é uma "compreensão de dicionário" (dictionary comprehension)
    # Para cada (id, nome) na lista, ele cria um par 'nome': id
    mapa_grupos = {nome: id for id, nome in resultados_grupos}

    print(f"Mapa de tradução criado: {mapa_grupos}")
    if not mapa_grupos:
        print("AVISO: A tabela 'grupos' está vazia. Você precisa inserir os grupos primeiro.")
        # (O ideal seria ter um script para popular 'grupos' ou fazê-lo aqui)
        # Vamos inserir os grupos se não existirem (forma robusta)
        print("Populando tabela 'grupos' (se necessário)...")
        # 'INSERT OR IGNORE' não fará nada se o grupo já existir
        escrita("INSERT OR IGNORE INTO grupos (nome_grupo) VALUES (?)", ("Grupo A",))
        escrita("INSERT OR IGNORE INTO grupos (nome_grupo) VALUES (?)", ("Grupo B",))
        escrita("INSERT OR IGNORE INTO grupos (nome_grupo) VALUES (?)", ("Grupo C",))
        # Recria o mapa
        resultados_grupos = leitura(query_grupos)
        mapa_grupos = {nome: id for id, nome in resultados_grupos}
        print(f"Mapa de tradução recriado: {mapa_grupos}")

    # --- LOOP PRINCIPAL DO ETL (O "CHAPÉU SELETOR") ---
    print("\nIniciando a inserção no banco de dados...")

    # Dicionário de "mapas de query" para evitar um 'if/elif' gigante
    # Mapeia o 'tipo_ensaio' do CSV para o nome da tabela de detalhes
    mapa_tabelas_detalhe = {
        'agonistas': 'detalhes_agonistas',
        'cryptococcus': 'detalhes_cryptococcus',
        'fagocitose': 'detalhes_fagocitose',
        'imunofenotipagem': 'detalhes_imunofenotipagem'
        # Adicione novos ensaios aqui no futuro
    }

    contador_sucesso = 0
    contador_falha = 0

    # Itera sobre cada linha do DataFrame do CSV
    for index, linha in df_mapa.iterrows():
        try:
            # 3.1. Pega os dados da linha
            nome_grupo = linha['nome_grupo']
            tipo_ensaio = linha['tipo_ensaio']
            id_animal = linha['id_animal']
            caminho_arquivo = linha['caminho_arquivo']
            
            # 3.2. TRADUZIR o nome para ID usando o mapa
            id_grupo = mapa_grupos.get(nome_grupo)
            if id_grupo is None:
                print(f"  [FALHA] Grupo '{nome_grupo}' não encontrado no banco de dados. Pulando linha {index}.")
                contador_falha += 1
                continue # Pula para a próxima linha do CSV

            # 3.3. ACHAR a tabela de detalhe correta
            nome_tabela_detalhe = mapa_tabelas_detalhe.get(tipo_ensaio)
            if nome_tabela_detalhe is None:
                print(f"  [FALHA] Tipo de ensaio '{tipo_ensaio}' desconhecido. Pulando linha {index}.")
                contador_falha += 1
                continue

            # --- A LÓGICA MESTRA-DETALHES ---

            sql_detalhe = f"""
                INSERT INTO {nome_tabela_detalhe} (id_animal, arquivo_de_resultado, condicao)
                VALUES (?, ?, ?)
            """
            params_detalhe = (id_animal, caminho_arquivo, None)
            
            # Usa a função 'escrita' e CAPTURA o ID retornado
            id_detalhe_criado = escrita(sql_detalhe, params_detalhe)
            
            if id_detalhe_criado is None:
                print(f"  [FALHA] Erro ao inserir em '{nome_tabela_detalhe}'. Pulando linha {index}.")
                contador_falha += 1
                continue

            sql_mestre = """
                INSERT INTO experimentos_master (id_grupo, data_experimento, tipo_ensaio, id_detalhe_ensaio)
                VALUES (?, ?, ?, ?)
            """
            params_mestre = (
                id_grupo,
                None, # data_experimento é NULL
                tipo_ensaio,
                id_detalhe_criado # O ID que acabamos de capturar!
            )
            
            # Desta vez não precisamos do ID de retorno, apenas executamos
            escrita(sql_mestre, params_mestre)
            
            contador_sucesso += 1

        except Exception as e:
            print(f"  [FALHA GERAL] Erro inesperado na linha {index}: {e}")
            contador_falha += 1

    print("-" * 50)
    print("Script ETL concluído.")
    print(f"Linhas processadas com sucesso: {contador_sucesso}")
    print(f"Linhas com falha: {contador_falha}") 

if __name__ == "__main__":
     popularDB()         