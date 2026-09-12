import sys
import os
# permite importar arquivos da pasta nucleo/, que fica um nivel acima desta pasta (app/)
sys.path.append(os.path.dirname(__file__) + "/..")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from nucleo.minhastats import (
    media, mediana, moda, amplitude, variancia, desvio_padrao,
    coeficiente_variacao, quartis, iqr
)

st.title("Laboratório Estatístico — Saúde Cardiovascular")

# carrega o CSV com Pandas (usado so para leitura/manipulacao, nunca para calcular estatisticas)
dados = pd.read_csv("dados/cardio_train.csv")

st.write("Prévia dos dados:")
st.dataframe(dados.head())
st.write(f"O dataset possui {dados.shape[0]} registros e {dados.shape[1]} colunas.")

# --- dicionarios de traducao: nomes das colunas estao em ingles no CSV original,
# aqui mapeamos para portugues, para exibir ao usuario da aplicacao ---
nomes_numericas = {
    "age": "Idade (dias)",
    "height": "Altura (cm)",
    "weight": "Peso (kg)",
    "ap_hi": "Pressão Sistólica",
    "ap_lo": "Pressão Diastólica",
}

nomes_categoricas = {
    "gender": "Gênero",
    "cholesterol": "Colesterol",
    "gluc": "Glicose",
    "smoke": "Fumante",
    "alco": "Consome Álcool",
    "active": "Ativo Fisicamente",
}

# alem do nome da coluna, os VALORES das categoricas tambem sao codigos numericos (1, 2, 3...)
# aqui traduzimos cada codigo para o rotulo que ele realmente representa
mapas_categoricas = {
    "gender": {1: "Feminino", 2: "Masculino"},
    "cholesterol": {1: "Normal", 2: "Acima do normal", 3: "Muito acima"},
    "gluc": {1: "Normal", 2: "Acima do normal", 3: "Muito acima"},
    "smoke": {0: "Não", 1: "Sim"},
    "alco": {0: "Não", 1: "Sim"},
    "active": {0: "Não", 1: "Sim"},
}

colunas_numericas = list(nomes_numericas.keys())
colunas_categoricas = list(nomes_categoricas.keys())

# ========== SECAO: VARIAVEIS NUMERICAS ==========
st.write("---")
st.subheader("Estatística Descritiva — Variáveis Numéricas")

# selectbox mostra o nome traduzido (format_func), mas guarda o nome real da coluna por baixo
variavel_num = st.selectbox(
    "Escolha uma variável numérica:",
    colunas_numericas,
    format_func=lambda c: nomes_numericas[c]
)

# pega a coluna escolhida do DataFrame e transforma em lista Python simples,
# que e o formato que nossas funcoes do minhastats.py esperam receber
valores = dados[variavel_num].tolist()

col1, col2 = st.columns(2)
with col1:
    media_valor = media(valores)
    mediana_valor = mediana(valores)
    st.metric("Média", f"{media_valor:.2f}")
    st.metric("Mediana", f"{mediana_valor:.2f}")
    st.metric("Moda", str(moda(valores)))
    st.metric("Amplitude", f"{amplitude(valores):.2f}")
with col2:
    st.metric("Variância (amostral)", f"{variancia(valores):.2f}")
    st.metric("Desvio Padrão (amostral)", f"{desvio_padrao(valores):.2f}")
    st.metric("Coeficiente de Variação", f"{coeficiente_variacao(valores):.2f}%")

# interpretacao textual automatica: compara media e mediana para inferir assimetria.
# a diferenca e dividida pelo desvio padrao para ter uma escala comparavel entre variaveis diferentes
diferenca_relativa = (media_valor - mediana_valor) / desvio_padrao(valores)
if abs(diferenca_relativa) < 0.05:
    interpretacao = "A distribuição parece **aproximadamente simétrica** (média e mediana próximas)."
elif diferenca_relativa > 0:
    interpretacao = "A distribuição parece **assimétrica à direita** (média maior que a mediana, indicando cauda de valores altos)."
else:
    interpretacao = "A distribuição parece **assimétrica à esquerda** (média menor que a mediana, indicando cauda de valores baixos)."
st.info(interpretacao)

# graficos da variavel numerica escolhida
col3, col4 = st.columns(2)
with col3:
    fig1, ax1 = plt.subplots()
    ax1.hist(valores, bins=20, color="#4C72B0")
    ax1.set_title(f"Histograma — {nomes_numericas[variavel_num]}")
    st.pyplot(fig1)
with col4:
    fig2, ax2 = plt.subplots()
    ax2.boxplot(valores, vert=True)
    ax2.set_title(f"Boxplot — {nomes_numericas[variavel_num]}")
    st.pyplot(fig2)

# deteccao de outliers pela regra do IQR: valores fora de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
q1, q2, q3 = quartis(valores)
valor_iqr = iqr(valores)
limite_inferior = q1 - 1.5 * valor_iqr
limite_superior = q3 + 1.5 * valor_iqr
outliers = [v for v in valores if v < limite_inferior or v > limite_superior]

st.write(f"Q1 = {q1:.2f} | Q3 = {q3:.2f} | IQR = {valor_iqr:.2f}")
st.write(f"Limite inferior: {limite_inferior:.2f} | Limite superior: {limite_superior:.2f}")
st.write(f"Foram encontrados **{len(outliers)}** outliers ({len(outliers)/len(valores)*100:.1f}% dos dados).")

# ========== SECAO: VARIAVEIS CATEGORICAS ==========
st.write("---")
st.subheader("Estatística Descritiva — Variáveis Categóricas")

variavel_cat = st.selectbox(
    "Escolha uma variável categórica:",
    colunas_categoricas,
    format_func=lambda c: nomes_categoricas[c]
)

# traduz os codigos numericos da coluna escolhida (1, 2, 3...) para os rotulos legiveis
mapa_atual = mapas_categoricas[variavel_cat]
valores_traduzidos = dados[variavel_cat].map(mapa_atual)

# tabela de frequencias: conta quantas vezes cada categoria aparece (contagem simples, nao estatistica)
tabela_frequencia = valores_traduzidos.value_counts().reset_index()
tabela_frequencia.columns = ["Categoria", "Frequência"]
tabela_frequencia["Percentual"] = (tabela_frequencia["Frequência"] / len(dados) * 100).round(2)

st.write("Tabela de frequências:")
st.dataframe(tabela_frequencia)

col5, col6 = st.columns(2)
with col5:
    fig3, ax3 = plt.subplots()
    ax3.bar(tabela_frequencia["Categoria"], tabela_frequencia["Frequência"], color="#55A868")
    ax3.set_title(f"Barras — {nomes_categoricas[variavel_cat]}")
    st.pyplot(fig3)
with col6:
    fig4, ax4 = plt.subplots()
    ax4.pie(tabela_frequencia["Frequência"], labels=tabela_frequencia["Categoria"], autopct="%1.1f%%")
    ax4.set_title(f"Pizza — {nomes_categoricas[variavel_cat]}")
    st.pyplot(fig4)