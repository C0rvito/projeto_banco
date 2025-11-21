from pathlib import Path

def pega_arquivos(letra: str, dir_base):

    ensaios = ["agonistas", "cryptococcus", "fagocitose", "imunofenotipagem"]
    arquivos_resultados = {}
    dir_base = Path(__file__).resolve().parent.parent.parent

    for ensaio in ensaios:
        dir_grupo = dir_base  / "data" / "raw" / f"grupo_{letra}" / f"{ensaio}"
       
        arquivos_totais = list(dir_grupo.glob("**/*.fcs"))
        contagem_arquivos = len(arquivos_totais)

        print(f"{ensaio}: {contagem_arquivos} arquivos encontrados")

        dados_ensaio = {
            'contagem': contagem_arquivos,
            'lista_arquivos': arquivos_totais
        }

        arquivos_resultados[ensaio] = dados_ensaio

    #return arquivos_resultados
 