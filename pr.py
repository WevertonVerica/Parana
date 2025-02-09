import streamlit as st
import pandas as pd
import geopandas as gpd
from unidecode import unidecode
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

cores_personalizadas = ['#FFFFFF','#00008B', '#ADD8E6', '#008000', '#FFFF00', '#FFA500', '#FF0000']
valores_cor = [0, 1, 2, 3, 4, 5, 6,7]  # Os valores correspondentes às cores

# Crie o colormap personalizado
cmap_personalizado = ListedColormap(cores_personalizadas)


# Carregar e processar os dados apenas uma vez
pr = gpd.read_file('PR_Municipios_2022.shp')
pr['cor'] = 0

def tratar_texto(col):
    if col.dtype == 'object':
        col_tratada = col.apply(lambda x: unidecode(str(x).lower()))
        return col_tratada
    return col

pr = pr.apply(tratar_texto)

# Inicializar o valor aleatório uma vez
if 'x_value' not in st.session_state:
    st.session_state.x_value = pr['NM_MUN'].sample().iloc[0]

# Inicializar a lista de chutes uma vez
if 'lista_chutes' not in st.session_state:
    st.session_state.lista_chutes = []

# Preparar os dados uma vez
x = st.session_state.x_value
teste = pr[pr['NM_MUN'] == x].geometry.iloc[0]
pr.loc[pr['NM_MUN'] == x, 'cor'] = 1
vizinho1 = pr[pr.geometry.intersects(teste)]
for i in vizinho1['NM_MUN']:
    pr.loc[pr['NM_MUN'] == i, 'cor'] += 1
lista_sequencia = [vizinho1] + [f'vizinho{i+1}' for i in range(1,6)]

anterior = lista_sequencia[0]
for seq in lista_sequencia[1:]:
    vizinhot = []
    for i in anterior['NM_MUN']:
        viz = pr[pr.geometry.intersects(pr[pr['NM_MUN'] == i].geometry.iloc[0])]
        vizinhot.append(viz)
    seq = vizinhot[0]
    for i in range(1,len(vizinhot)):
        seq = seq.append(vizinhot[i])
    seq = seq.drop_duplicates(subset=['CD_MUN'], keep='first')
    for i in seq['NM_MUN']:
        pr.loc[pr['NM_MUN'] == i, 'cor'] += 1
    anterior = seq

novo = pr

# Configurações iniciais do Streamlit
st.title('Acerte o município')
pr['cor'] = pr['cor'].map({0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6:6, 7:7})
# Criar a figura do mapa original se ainda não foi criada
if 'map_fig_original' not in st.session_state:
    map_fig_original, map_ax_original = plt.subplots(figsize=(15, 9))
    pr.plot(ax=map_ax_original, column='cor', cmap=cmap_personalizado, edgecolor='black')
    novo.plot(column='cor', cmap=cmap_personalizado, edgecolor='black')
    st.session_state.map_fig_original = map_fig_original
st.pyplot(st.session_state.map_fig_original)
# Interface para o usuário
chute = st.text_input('Digite uma cidade:')
resultado = ""
st.session_state.lista_chutes.append(chute)
if st.button('Verificar'):
    if chute == st.session_state.x_value:
        resultado = "Você acertou!"
    else:
        resultado = 'Tente novamente'
        lista = [elemento for elemento in novo['NM_MUN'] if elemento not in st.session_state.lista_chutes]
        # Resetar a cor do município do chute para 0
        for i in lista:
            novo.loc[novo['NM_MUN'] == i, 'cor'] = 0
        map_fig_chute, map_ax_chute = plt.subplots(figsize=(15, 9))
        novo.plot(ax=map_ax_chute, column='cor', cmap=cmap_personalizado, edgecolor='black')
        st.session_state.map_fig_chute = map_fig_chute
        st.pyplot(st.session_state.map_fig_chute)


st.write(st.session_state.x_value)



# Mostrar as figuras dos mapas
#st.pyplot(st.session_state.map_fig_original)
