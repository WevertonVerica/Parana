import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import pandas as pd
from unidecode import unidecode

# Título da aplicação
st.title("Jogo de Adivinhação de Cidades do Paraná")

# Carregar os dados
#@st.cache  # Ou @st.cache se estiver usando uma versão antiga
pr = gpd.read_file('PR_Municipios_2022.shp')
pr['cor'] = 0
# Função para tratar texto
def tratar_texto(col):
    if col.dtype == 'object':  # Verifica se a coluna contém texto
        col_tratada = col.apply(lambda x: unidecode(str(x).lower()))
        return col_tratada
    return col

# Aplicar tratamento de texto
pr = pr.apply(tratar_texto)

# Inicializar o estado da sessão
if 'x' not in st.session_state:
    st.session_state.x = pr['NM_MUN'].sample().iloc[0]  # Município alvo
    st.session_state.pr = pr.copy()  # Cópia do DataFrame para manipulação
    st.session_state.tentativas = []  # Lista de municípios já tentados

# Encontrar vizinhos e marcar cores
teste = st.session_state.pr[st.session_state.pr['NM_MUN'] == st.session_state.x].geometry.iloc[0]
st.session_state.pr.loc[st.session_state.pr['NM_MUN'] == st.session_state.x, 'cor'] = 1

# Encontrar vizinhos diretos
vizinho1 = st.session_state.pr[st.session_state.pr.geometry.intersects(teste)]
for i in vizinho1['NM_MUN']:
    st.session_state.pr.loc[st.session_state.pr['NM_MUN'] == i, 'cor'] += 1

# Encontrar vizinhos de vizinhos
lista_sequencia = [f'vizinho{i+1}' for i in range(1, 10)]
lista_sequencia = [vizinho1] + lista_sequencia
anterior = lista_sequencia[0]

for seq in lista_sequencia[1:]:
    vizinhot = []
    for i in anterior['NM_MUN']:
        viz = st.session_state.pr[st.session_state.pr.geometry.intersects(
            st.session_state.pr[st.session_state.pr['NM_MUN'] == i].geometry.iloc[0]
        )]
        vizinhot.append(viz)
    seq = vizinhot[0]
    for i in range(1, len(vizinhot)):
        seq = pd.concat([seq, pd.DataFrame(vizinhot[i])], ignore_index=True)
    seq = seq.drop_duplicates(subset=['CD_MUN'], keep='first')
    for i in seq['NM_MUN']:
        st.session_state.pr.loc[st.session_state.pr['NM_MUN'] == i, 'cor'] += 1
    anterior = seq

# Exibir o município correto e o mapa completo para depuração
#st.write("**Depuração:** Município correto:", st.session_state.x)
#fig, ax = plt.subplots(figsize=(15, 9))
#st.session_state.pr.plot(ax=ax, column='cor', cmap='jet', edgecolor='black', legend=True)
#st.pyplot(fig)

# Função para tratar entrada do usuário
def tratar_entrada(texto):
    texto_tratado = unidecode(texto.lower())
    return texto_tratado

# Interface do Streamlit
st.write("Tente adivinhar a cidade do Paraná!")

chute = st.text_input("Digite uma cidade:")

if chute:
    chute = tratar_entrada(chute)
    if chute == st.session_state.x:
        st.success("Você acertou!")
        st.session_state.tentativas.append(chute)  # Adiciona o chute à lista de tentativas
    else:
        st.error("Tente novamente!")
        st.session_state.tentativas.append(chute)  # Adiciona o chute à lista de tentativas

# Atualizar o mapa com as tentativas
if st.session_state.tentativas:
    novo = st.session_state.pr.copy()
    for tentativa in st.session_state.tentativas:
        novo = novo.drop(st.session_state.pr[st.session_state.pr['NM_MUN'] == tentativa].index)

    fig, ax = plt.subplots(figsize=(15, 9))
    st.session_state.pr.plot(ax=ax, column='cor', cmap='jet', edgecolor='black', legend=True)
    novo.plot(ax=ax, color='white')
    st.pyplot(fig)
