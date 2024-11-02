# importlibriries
import streamlit as st
import pandas as pd
import yfinance as yf
import math
from datetime import timedelta, datetime


# criar as funcoes de carregamento de dados
# cotacoes do itau - ITUB4.SA - 2010 a 2024


@st.cache_data  # armazena os dados gerados em carregar_dados no cache
def carregar_dados(empresas):
    
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period="1d", start="2010-1-1", end=datetime.now())
    cotacoes_acao = cotacoes_acao["Close"]
    return cotacoes_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=",")
    tickers = list(base_tickers["Codigo"])
    tickers = [item.rstrip(" ") + ".SA" for item in tickers]
    return tickers



acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes)

# prepara as visualizacoes - filtros
st.sidebar.header("Filtros:")

lista_acoes = st.sidebar.multiselect("Selecione as ações a exibir", dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica:"Close"})

# filtros de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_datas = st.sidebar.slider("Selecione o intervalo de datas:",
                  min_value=data_inicial, max_value=data_final, value=(data_inicial, data_final), step=timedelta(days=1))

dados = dados.loc[intervalo_datas[0]:intervalo_datas[1]] # .loc para selecionar por datas
# criar interface do streamlit
st.write(""" 
         # App de Cotação de Ativos 
         O gráfico abaixo representa a evolução de cotação das acoes selecionadas.
         """)  # markdown

# criar graficos
st.line_chart(dados)

# calculo de performance

texto_performance = ""
if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={"Close": acao_unica})


carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):
    performance = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1
    performance = float(performance)

    carteira[i] = carteira[i] * (1 + performance)

    if  math.isnan(performance) is False:
        if performance > 0:
            texto_performance = texto_performance + f"  \n{acao}: :green[{performance:.1f}]%"
        elif performance < 0:
            texto_performance = texto_performance + f"  \n{acao}: :red[{performance:.1f}%]"
        else:
            texto_performance = texto_performance + f"  \n{acao}: {performance:.1f}%"


total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1
performance_carteira = float(performance_carteira)


if performance_carteira > 0:
    texto_performance_carteira = f"  \nTotal para as ações selecionadas: :green[{performance_carteira:.1f}%]"
elif performance_carteira < 0:
    texto_performance_carteira = f"  \nTotal para as ações selecionadas: :red[{performance_carteira:.1f}%]"
else:
    texto_performance_carteira = f"  \nTotal para as ações selecionadas: {performance_carteira:.1f}%"



st.write(f"""
### Performance da Carteira
{texto_performance_carteira}         

### Performance dos Ativos
Essa for a performance das ações selecionadas no periodo selecionado.
{texto_performance}


""")
