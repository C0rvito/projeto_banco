import streamlit as st
import sys
from pathlib import Path

#st.write(st.session_state) # <-- NOVA LINHA DE DEBUG

# Pega o caminho absoluto deste arquivo
arquivo_atual = Path(__file__).resolve()

# Calcula a raiz 'src' (subindo 3 níveis: pages -> app -> src)
PASTA_SRC = arquivo_atual.parent.parent.parent

# Adiciona ao sys.path se ainda não estiver lá
if str(PASTA_SRC) not in sys.path:
    sys.path.append(str(PASTA_SRC))

# Import da finção de leitura
try:
    from funcoes.db_tools import leitura
except ImportError as e:
    st.error("🛑 ERRO CRÍTICO DE IMPORTAÇÃO")
    st.write(f"O Python falhou ao importar 'funcoes': `{e}`")
    st.stop()
try:
    from funcoes.metadados import extrair_metadado, formata_df, processa_compara
except ImportError as e:
    st.error(f'Erro ao importar metadados: {e}')
    st.stop()

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Repositório de Experimentos" ,layout="wide", page_icon="📂")
st.title("📂 Repositório de Experimentos")

# --- 3. MAPAS DE DADOS ---
MAPA_TABELAS_DETALHE = {
    'agonistas': 'detalhes_agonistas',
    'cryptococcus': 'detalhes_cryptococcus',
    'fagocitose': 'detalhes_fagocitose',
    'imunofenotipagem': 'detalhes_imunofenotipagem'
}

MAPA_PKS_DETALHE = {
    'agonistas': 'id_agonista',
    'cryptococcus': 'id_cryptococcus',
    'fagocitose': 'id_fagocitose',
    'imunofenotipagem': 'id_imunofenotipagem'
}

# --- 4. FUNÇÕES CACHEADAS (Consultas ao Banco) ---
@st.cache_data
def buscar_mapa_de_grupos():
    resultados_tuplas = leitura("SELECT id_grupo, nome_grupo FROM grupos ORDER BY nome_grupo")
    lista_nomes = [item[1] for item in resultados_tuplas]
    mapa_ids = {nome: id for id, nome in resultados_tuplas}
    return lista_nomes, mapa_ids

@st.cache_data
def buscar_ensaios_por_grupo(id_grupo):
    query = "SELECT DISTINCT tipo_ensaio FROM experimentos_master WHERE id_grupo = ? ORDER BY tipo_ensaio"
    resultados = leitura(query, (id_grupo,))
    return [item[0] for item in resultados]

@st.cache_data
def buscar_resultados_finais(id_grupo, tipo_ensaio):
    tabela = MAPA_TABELAS_DETALHE[tipo_ensaio]
    pk = MAPA_PKS_DETALHE[tipo_ensaio]
    
    query = f"""
        SELECT d.id_animal, d.arquivo_de_resultado, d.condicao
        FROM {tabela} AS d
        JOIN experimentos_master AS m ON d.{pk} = m.id_detalhe_ensaio
        WHERE m.id_grupo = ? AND m.tipo_ensaio = ?
        ORDER BY d.id_animal
    """
    return leitura(query, (id_grupo, tipo_ensaio))

# --- 5. LÓGICA DA BARRA LATERAL (Filtros) ---
st.sidebar.header("Filtros")
try:
    st.sidebar.image("assets/logo.png", use_column_width=True)
except:
    pass

lista_grupos, mapa_grupos = buscar_mapa_de_grupos()
grupo_sel = st.sidebar.selectbox('1. Grupo:', lista_grupos)

if grupo_sel:
    id_grupo = mapa_grupos[grupo_sel]
    lista_ensaios = buscar_ensaios_por_grupo(id_grupo)
    ensaio_sel = st.sidebar.selectbox('2. Ensaio:', lista_ensaios)

    # --- 6. EXIBIÇÃO DOS RESULTADOS ---
    if ensaio_sel:
        st.divider()
        st.subheader(f"Resultados: {grupo_sel} - {ensaio_sel}")
        
        resultados = buscar_resultados_finais(id_grupo, ensaio_sel)
        
        if resultados:
            # Cabeçalho da Lista
            c1, c2, c3, c4 = st.columns([1, 2, 4, 2])
            c1.markdown("**ID Animal**")
            c2.markdown("**Condição**")
            c3.markdown("**Nome do Arquivo**")
            c4.markdown("**Ação**")
            st.markdown("---")

            # Loop para desenhar cada linha
            for linha in resultados:
                id_animal, caminho_relativo_str, condicao = linha
                
                # Constrói o caminho absoluto para leitura do arquivo
                # PASTA_SRC é .../src
                # O pai dela é a raiz do projeto (.../projeto_banco)
                dir_raiz_projeto = PASTA_SRC.parent
                caminho_absoluto = dir_raiz_projeto / caminho_relativo_str
                nome_arquivo = Path(caminho_relativo_str).name

                # Colunas da Linha
                c1, c2, c3, c4 = st.columns([1, 2, 4, 2])
                
                with c1: 
                    st.write(f"#{id_animal}")
                
                with c2: 
                    if condicao:
                        st.write(condicao)
                    else:
                        st.caption("N/A")
                
                with c3: 
                    st.caption(nome_arquivo)
                
                with c4:
                    if caminho_absoluto.exists():
                            print(f"\n[DEBUG_START] Tentando abrir: {caminho_absoluto}") # <-- LOG 1: O caminho 
                            
                            try:
                                # Tenta ler o arquivo
                                with open(caminho_absoluto, "rb") as f:
                                    bytes_do_arquivo = f.read()
                                
                                print(f"[DEBUG_SUCCESS] Bytes lidos com sucesso. Tamanho: {len(bytes_do_arquivo)} bytes.") # LOG 2
                                
                                # --- SE SUCESSO, MOSTRA O BOTÃO ---
                                st.download_button(
                                    label="⬇️ Baixar FCS",
                                    data=bytes_do_arquivo,
                                    file_name=nome_arquivo,
                                    mime="application/octet-stream",
                                    key=f"dl_{id_animal}_{nome_arquivo}"
                                )

                            except Exception as e:
                                # LOG 3: Captura o erro técnico exato (permissão, arquivo corrompido, etc.)
                                print(f"[DEBUG_FAIL] Erro I/O FATAL: {e}") 
                                st.error("Erro ao ler: (Detalhes no Terminal)")
               
                    else:
                        # Esta linha não deve estar dando erro, mas é bom mantê-la.
                        st.error("Arquivo não encontrado (Caminho inválido)")
                        st.warning(f"DEBUG: Procurado em: {caminho_absoluto}")
                    
                with st.expander(f'Ver Detalhes e Metadados'):
                    if caminho_absoluto.exists():
                        dados_brutos = extrair_metadado(caminho_absoluto)

                        df_geral, df_canais, df_fluoroforos = formata_df(dados_brutos)

                        if "Erro de Leitura" in df_geral.columns:
                            st.error(f"ERRO: Não foi possível ler o arquivo. {df_geral['Erro de Leitura'].iloc[0]}")
                        else:
                            st.markdown("##### Informações Gerais:")
                            # Transpõe o DF Geral (de 3 linhas para 3 colunas)
                            st.dataframe(df_geral.set_index('Métrica').T, hide_index=True)

                            col_canais, col_fluoros = st.columns(2)
                            with col_canais:
                                st.markdown("##### Canais Adquiridos:")
                                st.dataframe(df_canais, hide_index=True, use_container_width=True)
                        with col_fluoros:
                            st.markdown("##### Fluoróforos/Marcadores:")
                            st.dataframe(df_fluoroforos, hide_index=True, use_container_width=True)
                    
                    else:
                        st.warning("Caminho do arquivo não é válido")
                st.markdown("---")
        else:
            st.warning("Nenhum resultado encontrado no banco para este filtro.")
else:
    st.info("Selecione um Grupo para começar.")


    
    