import pandas as pd
import flowio
from pathlib import Path


def extrair_metadado(caminho_arquivo: Path) -> dict[str, any]:
    """
    Lê arquivo fcs, extrai metadados principais e normaliza canais.
    Retorna um dicionário consolidado
    """

    try:
        # Lê apenas a seção de metadados
        fcs = flowio.FlowData(str(caminho_arquivo), only_text=True)
        meta = fcs.text

        lista_canais: list[dict[str, str]] = []
        lista_fluoroforos: list[dict[str, str]] = []

        exclusao: list[str] = ['FSC', 'SSC', 'TIME', 'WIDTH']
        for numero, info in fcs.channels.items():

            canal: str = info.get('pnn', '').upper()
            fluoroforo: str = info.get('pns', '').upper()

            concatena: str = f"{canal}{fluoroforo}"

            if not any(termo in concatena for termo in exclusao):

                lista_canais.append({
                    "Canal": info.get('pnn')
                })
                lista_fluoroforos.append({
                    "Fluoróforo": info.get('pns')
                })
                pass 

        dicionario: dict[str, any] = {
            "Data": meta.get('date', 'N/A'),
            "Citômetro": meta.get('cyt', 'N/A'),
            "Amostra": meta.get('tbnm'),
            "Eventos registrados": int(meta.get('tot',0)),
            "Canais": lista_canais,
            "Fluoróforos": lista_fluoroforos
        }
        return dicionario

    except Exception as e:
        return {"Status": "Erro de Leitura", "Error": str(e)}
    

def formata_df(dados_brutos: dict[str,any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Recebe dicionário de metadados fcs extraído e tranforma em três Dataframes 
    """
    # Dataframe de dados gerais
    dados_gerais: dict[str, list[any]] = {
        "Métrica": ["Data", "Citômetro", "Amostra", "Eventos registrados"],
        "Valor": [
           dados_brutos.get('Data',"N/A"),
           dados_brutos.get('Citômetro', "N/A"),
           dados_brutos.get('Amostra', 'N/A'),
           dados_brutos.get("Eventos registrados", "0")
        ]
    }
    df_geral: pd.DataFrame = pd.DataFrame(dados_gerais)


    # Dataframe de canais e fluoróforos
    df_canais: pd.DataFrame = pd.DataFrame(dados_brutos.get("Canais", []))
    df_fluoroforos: pd.DataFrame = pd.DataFrame(dados_brutos.get("Fluoróforos", []))

    return df_geral, df_canais, df_fluoroforos

def processa_compara(lista_caminhos_fcs:list):
    lista_dados_gerais_planos = []

    for caminho in lista_caminhos_fcs:
        dados_brutos = extrair_metadado(caminho)

        df_geral = formata_df(dados_brutos)

        df_geral_transposto = df_geral.set_index('Métrica').T
        df_geral_transposto['Arquivo'] = Path(caminho).name

        lista_dados_gerais_planos.append(df_geral_transposto)

    df_comparado_geral = pd.concat(lista_dados_gerais_planos)
    
    df_eventos = df_comparado_geral[['Eventos registrados']].astype(int)

    
    return df_comparado_geral.drop(columns=['Eventos registrados']).describe(), df_eventos.describe()


#    path_dir = Path(r"C:\Users\b1-66\Desktop\Projetos\fiocruz\LIMC\projeto_banco\data\raw\grupo_a\agonistas")


    #  / do pathlib une o diretório e o nome do arquivo.
    # O método iterdir() retorna objetos Path diretamente.
#    if path_dir.exists():
        # Filtrar apenas os arquivos .fcs para maior robustez
#        list_caminhos = [caminho for caminho in path_dir.iterdir() if caminho.suffix.lower() == '.fcs']
#    else:
#        print(f"Erro: O diretório não foi encontrado: {path_dir}")
#        list_caminhos = []

#    if list_caminhos:
#        teste = processa_compara(list_caminhos)
#        print(teste)
#    else:
#        print("Nenhum arquivo FCS encontrado ou o diretório está vazio/inexistente.")



### Teste pra extrair só um dos dataframes que retornam da função de formatar df

a = r"C:\Users\b1-66\Desktop\Projetos\fiocruz\LIMC\projeto_banco\data\raw\grupo_a\agonistas\AGO BCG 11.fcs"

teste = extrair_metadado(a)
print(teste)


# aaa = formata_df(teste)[1].value_counts()
#print(aaa)

