import pandas as pd
from pathlib import Path
from funcoes.pega_arquivos import pega_arquivos
import re 

dir_base = Path(__file__).resolve().parent.parent.parent

mapa_dos_grupos = {
    "a": "Grupo A",
    "b": "Grupo B",
    "c": "Grupo C"
}

mapa_id_animal = {
    "Grupo A": (11, 20),
    "Grupo B": (21, 30),
    "Grupo C": (31, 40)
}

# 1 - Cria lista vazia para guardar as linhas planas
lista_para_csv = []

# 2 - Itera sobre o dicionário principal
for letra_do_grupo, nome_do_grupo in mapa_dos_grupos.items():
    
    print(f"Processando: {nome_do_grupo}")

    range_valido = mapa_id_animal[nome_do_grupo]

    dados_do_grupo = pega_arquivos(letra_do_grupo, dir_base)

    for tipo_ensaio, detalhes in dados_do_grupo.items():
        # 3 - Itera sobre lista_arquivos
        for arquivo_path in detalhes['lista_arquivos']:

            arquivo = arquivo_path.name

            id_animal = None

            sei_la = re.findall(r"\d+",arquivo)
            numeros = [int(s) for s in sei_la]

            for num in numeros:
                # Verifica se no range
                if range_valido[0] <= num <= range_valido[1]:
                    id_animal = int(num)
                    break

            caminho_relativo = arquivo_path.relative_to(dir_base)
            nova_linha = [nome_do_grupo, tipo_ensaio, id_animal, str(caminho_relativo)]

            lista_para_csv.append(nova_linha)

        df = pd.DataFrame(lista_para_csv, columns=["nome_grupo", "tipo_ensaio", "id_animal", "caminho_arquivo"])

        # df está salvando o ID animal como float
        df['id_animal'] = df['id_animal'].astype('Int64')

        df.to_csv(dir_base / "mapeamento.csv", index=False)
