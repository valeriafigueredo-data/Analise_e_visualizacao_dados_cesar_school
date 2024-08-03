import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pgeocode

# Criando Título na sidebar
st.sidebar.markdown('<h1 style="font-size:55px;">Super Store</h1>', unsafe_allow_html=True)
st.sidebar.image('https://www.impulsonegocios.com/wp-content/uploads/2021/04/SUPERMERCADOS-Y-PROVEDORES.jpg', use_column_width=True)

# Carregando os dados
url = "https://raw.githubusercontent.com/valeriafigueredo-data/Analise_e_visualizacao_dados_cesar_school/main/pandas/SampleSuperstore.csv"
df_store = pd.read_csv(url)

# Criando o filtro de categorias
with st.sidebar:
    st.sidebar.title('Categorias')
    categories = df_store['Categoria'].unique().tolist()
    selected_categories = [category for category in categories if st.sidebar.checkbox(category, value=True, key=f"cat_{category}")]

# Criando o filtro de regiões
with st.sidebar:
    st.sidebar.title('Regiões')
    regioes = df_store['Região'].unique().tolist()
    selected_regioes = [regiao for regiao in regioes if st.sidebar.checkbox(regiao, value=True, key=f"reg_{regiao}")]

# Filtrar os estados com base nas regiões selecionadas
if selected_regioes:
    estados = df_store[df_store['Região'].isin(selected_regioes)]['Estado'].unique().tolist()
else:
    estados = []  # Nenhum estado disponível se nenhuma região estiver selecionada

# Adicionar "Selecionar Todos" ao início da lista de estados
if estados:
    estados.insert(0, "Selecionar Todos")

# Criar o widget multiselect para estados
with st.sidebar:
    st.sidebar.title('Estados')
    selected_estados = st.sidebar.multiselect(" ", options=estados, default="Selecionar Todos")

# Garantir que pelo menos um estado esteja selecionado
if not selected_estados:
    st.warning("Por favor, selecione pelo menos um estado.")
    selected_estados = estados[1:]  # Ignora "Selecionar Todos"

# Aplicando os filtros
df_filtered = df_store

# Aplicando o filtro para categorias
if selected_categories:
    df_filtered = df_filtered[df_filtered['Categoria'].isin(selected_categories)]
else:
    df_filtered = df_filtered[0:0]  # DataFrame vazio

# Aplicando o filtro para estados
if "Selecionar Todos" in selected_estados:
    selected_estados = df_store[df_store['Região'].isin(selected_regioes)]['Estado'].unique().tolist()  # Selecionar todos os estados das regiões selecionadas
else:
    selected_estados = [estado for estado in selected_estados if estado != "Selecionar Todos"]

if selected_estados:
    df_filtered = df_filtered[df_filtered['Estado'].isin(selected_estados)]
else:
    df_filtered = df_filtered[0:0]  # DataFrame vazio

# Aplicando o filtro para regiões
if selected_regioes:
    df_filtered = df_filtered[df_filtered['Região'].isin(selected_regioes)]
else:
    df_filtered = df_filtered[0:0]  # DataFrame vazio

# Criando mapa interativo
# Agrupamento e soma das vendas por cidade, estado e código postal
sales_by_city_state = df_filtered.groupby(['Estado', 'Cidade', 'Código Postal', 'Categoria'])['Vendas'].sum().reset_index()

# Uso do pgeocode para obter as coordenadas a partir dos códigos postais
nomi = pgeocode.Nominatim('us')

# Função para obter coordenadas de um código postal
def get_coordinates(postal_code):
    location = nomi.query_postal_code(postal_code)
    if location is not None:
        return pd.Series([location.latitude, location.longitude])
    else:
        return pd.Series([None, None])

# Aplicação da função e adicionando as coordenadas ao DataFrame
sales_by_city_state[['Latitude', 'Longitude']] = sales_by_city_state['Código Postal'].apply(get_coordinates)

# Filtro das linhas com coordenadas válidas
sales_by_city_state = sales_by_city_state.dropna(subset=['Latitude', 'Longitude'])

# Filtrando o dataframe com base nas categorias selecionadas
if selected_categories:
    filtered_sales_by_city_state = sales_by_city_state[sales_by_city_state['Categoria'].isin(selected_categories)]
else:
    filtered_sales_by_city_state = sales_by_city_state[0:0]  # DataFrame vazio


 #Definindo uma escala de cores que vai de vermelho claro para vermelho escuro
red_color_scale = [
    [0.0, 'rgb(255,204,204)'],  # Vermelho muito claro 
    [0.3, 'rgb(255,153,153)'],  # Vermelho claro
    [0.5, 'rgb(255,51,51)'],    # Vermelho médio
    [0.8, 'rgb(204,0,0)'],      # Vermelho escuro
    [1.0, 'rgb(139,0,0)']       # Vermelho muito escuro
]

# Criar o gráfico de mapa

with st.container():
    fig=px.scatter_geo(
        filtered_sales_by_city_state,
        lat='Latitude',
        lon='Longitude',
        color='Vendas',
        hover_name='Cidade',
        hover_data={'Estado': True, 'Vendas': True},
        size='Vendas',
        size_max=40,  # Ajuste o tamanho máximo dos pontos
        color_continuous_scale=red_color_scale,  # Aplicar a escala de cores
        scope='usa',
        projection='albers usa'
)

# Ajustar o tamanho e o estilo do texto do título
fig.update_layout(
    title={
        'text': 'Total de Vendas por Cidade nos EUA',
        'font': {'size': 28, 'family': 'Arial', 'color': 'black'}  # Ajuste o tamanho e a família da fonte
    },
    width=1200,  # Largura do gráfico em pixels
    height=800,  # Altura do gráfico em pixels
    geo=dict(
        showland=True,
        landcolor='lightgray',
        showocean=True,
        oceancolor='#F5F7FA',
        showlakes=True,
        lakecolor='lightblue',
    ),
    margin=dict(l=0, r=0, t=50, b=0),  # Ajuste das margens
    coloraxis_colorbar=dict(title="Vendas")  # Título da barra de cores
)

# Exibindo o gráfico
st.plotly_chart(fig)



# Agrupamento das vendas por estado
sales_by_state = df_filtered.groupby('Estado')['Vendas'].sum().reset_index()

# Ordenamento dos valores de vendas em ordem decrescente
sales_by_state = sales_by_state.sort_values(by='Vendas', ascending=True)

# Gráfico de barras por estado
with st. container():
    fig_barh = px.bar(sales_by_state, x='Vendas', y='Estado', orientation='h')

# Ajustar o tamanho do gráfico e a visibilidade
fig_barh.update_layout(
    title={'text': 'Total de Vendas por Estado',
           'font': {'size': 28, 'family': 'Arial'}},
    width=1400,  # Largura do gráfico em pixels
    height=800,  # Altura do gráfico em pixels
    xaxis_title='Vendas',
    yaxis_title='Estado',
    xaxis=dict(tickformat=".2s"),  # Formatar os valores do eixo x para facilitar a leitura
    bargap=0.2  # Ajustar o espaço entre as barras
)

# Mudar a cor da barra
fig_barh.update_traces(marker_color='red')

# Mostrar o gráfico
st.plotly_chart(fig_barh)

# Criando os gráficos de correlação

# Definindo um mapa de cores harmonioso
color_map = {
    "Mobílias": "#000000",          
    "Itens de Escritório": "#ff9896", 
    "Técnologia": "rgb(139,0,0)"          
}

# Gráfico de dispersão entre vendas e lucro para as categorias selecionadas

with st. container():
    fig_scatter = px.scatter(
    df_filtered,
    x='Vendas',
    y='Lucro',
    color='Categoria',
    color_discrete_map=color_map
)

# Atualizar o layout para alterar o tamanho da figura
fig_scatter.update_layout(
    title={'text': 'Correlação entre Venda e Lucro',
           'font': {'size': 28, 'family': 'Arial'}}
)

# Criar o gráfico de mapa de calor
# Calcular a matriz de correlação

with st. container():
    if not df_filtered.empty:
        correlation_matrix = df_filtered[['Vendas', 'Lucro', 'Desconto']].corr()
    else:
        correlation_matrix = pd.DataFrame(columns=['Vendas', 'Lucro', 'Desconto'], index=['Vendas', 'Lucro', 'Desconto'])

# Criar o mapa de calor com valores de correlação no centro de cada célula

    fig_heatmap= go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='reds',
        colorbar=dict(title='Correlação'),
        text=correlation_matrix.values,
        texttemplate='%{text:.2f}',
        textfont=dict(size=14)
))

# Atualizar o layout para alterar o tamanho da figura
fig_heatmap.update_layout(
    title={'text': 'Correlação entre Venda, Lucro e Desconto',
           'font': {'size': 28, 'family': 'Arial'}},
    width=600,  # Largura da figura
    height=600  # Altura da figura
)

# Exibindo o gráfico de dispersão
st.plotly_chart(fig_scatter, use_container_width=True)

# Exibindo o gráfico de mapa de calor
st.plotly_chart(fig_heatmap, use_container_width=True)

# Calculando a correlação entre Vendas e Lucro
if not df_filtered.empty:
    correlation = df_filtered['Vendas'].corr(df_filtered['Lucro'])
    st.write(f"A correlação entre Vendas e Lucro para a(s) categoria(s) selecionada(s) é: {correlation:.2f}")
else:
    st.write("Nenhuma categoria selecionada ou não há dados disponíveis para as categorias selecionadas.")