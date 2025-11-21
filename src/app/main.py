# Em: src/app/main.py (O NOVO)
import streamlit as st

st.set_page_config(
    page_title="Home - Banco de Dados LIMC",
)


st.title("Bem-vindo ao Banco de Dados LIMC")
st.header("Plataforma de Rastreamento de Experimentos")

st.markdown("""
    Este aplicativo foi desenvolvido para centralizar e rastrear 
    os arquivos de resultados dos experimentos.

    ### Como usar:
    Use o menu na **barra lateral esquerda** para navegar:

    - **Repositório de Experimentos:** Para buscar e fazer o download dos arquivos de resultados existentes.
    - **Adicionar Dados:** Para inserir novos experimentos no banco de dados (em breve).
""")
        
        
        
        
        # Exibe os resultados em uma tabela
        #if resultados:
        #    df_finais = pd.DataFrame(resultados, columns=["ID Animal", "Caminho do Arquivo", "Condição"])
        #    st.dataframe(df_finais)
        #else:
        #    st.warning("Nenhum resultado encontrado para esta combinação de filtros.")

#else:
    #st.info("Selecione um Grupo e um Ensaio na barra lateral para começar.")