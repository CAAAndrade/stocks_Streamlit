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
    cotacoes_acao = dados_acao.history(
        period="1d", start="2020-1-1", end=datetime.now()
    )
    cotacoes_acao = cotacoes_acao["Close"]
    return cotacoes_acao


@st.cache_data
def get_stocks_tickets(market):
    base_tickers = pd.read_csv(f"{market}.csv", sep=",", header=0)
    if market == "IBOV":
        tickers = base_tickers.iloc[:, 0].tolist()
        tickers = [item.rstrip(" ") + ".SA" for item in tickers]
    else:
        tickers = base_tickers.iloc[:, 0].tolist()
    return tickers


@st.cache_data
def get_stocks_name(market):
    base_tickers = pd.read_csv(f"{market}.csv", sep=",", header=0)
    tickers = base_tickers.iloc[:, 0].tolist()
    tickers = [item.rstrip(" ") for item in tickers]
    name = base_tickers.iloc[:, 1].tolist()
    names = dict(zip(tickers, name))
    return names


# prepara as visualizacoes - filtros
st.sidebar.header("Filters:")

market = st.sidebar.selectbox("Choose a market:", ("IBOV", "NASDAQ"))

acoes = get_stocks_tickets(market)
dados = carregar_dados(acoes)
dic_names = get_stocks_name(market)




lista_acoes = st.sidebar.multiselect(
    "Choose stocks for your portfolio:", dados.columns
)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})

# filtros de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_datas = st.sidebar.slider(
    "Select a date range:  \n",
    min_value=data_inicial,
    max_value=data_final,
    value=(data_inicial, data_final),
    step=timedelta(days=1),
)

dados = dados.loc[
    intervalo_datas[0] : intervalo_datas[1]
]  # .loc para selecionar por datas
# criar interface do streamlit
st.write(""" 
         # Equity Prices Analysis
         Value in Local Currency  \n
         The chart below shows the value variations for the selected shares.
         """)  # markdown

# criar graficos
if len(lista_acoes) == 0:
    st.line_chart()
    st.write("No share selected")
if len(lista_acoes) >= 1:
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
        nome = dic_names[acao.split(".")[0]]
        performance = float(performance)

        carteira[i] = carteira[i] * (1 + performance)

        if math.isnan(performance) is False:
            if performance > 0:
                texto_performance = (
                    texto_performance + f"  \n{acao} -  Current Value: {round((dados[acao].iloc[0]), 2)} - Company Name: {nome}: :green[{performance:.1f}]%"
                )
            elif performance < 0:
                texto_performance = (
                    texto_performance + f"  \n{acao} -  Current Value: {round((dados[acao].iloc[0]), 2)} - Company Name: {nome}: :red[{performance:.1f}%]"
                )
            else:
                texto_performance = (
                    texto_performance + f"  \n{acao} -  Current Value: {round((dados[acao].iloc[0]), 2)} - Company Name: {nome}: {performance:.1f}%"
                )

        total_final_carteira = sum(carteira)
        performance_carteira = total_final_carteira / total_inicial_carteira - 1
        performance_carteira = float(performance_carteira)

        if performance_carteira > 0:
            texto_performance_carteira = f"  \nSummary for your portfolio:   :green[{performance_carteira:.1f}%]"
        elif performance_carteira < 0:
            texto_performance_carteira = f"  \nSummary for your portfolio:   :red[{performance_carteira:.1f}%]"
        else:
            texto_performance_carteira = (
                f"  \nSummary for your portfolio:   {performance_carteira:.1f}%"
            )

    st.write(f"""
    ### Performance for your portfolio.
    {texto_performance_carteira}
    \nNote: If you detect an error when displaying the data, try changing the period to match the values in the chart.
    """)
    st.write(f"""
    ### Performance for each share - Value in Local Currency
    {texto_performance}


    """)
