import sys
import os
# permite importar arquivos da pasta nucleo/, que fica um nivel acima desta pasta (app/)
sys.path.append(os.path.dirname(__file__) + "/..")

from scipy import stats
import random
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from nucleo.minhastats import (
    media, mediana, moda, amplitude, variancia, desvio_padrao,
    coeficiente_variacao, quartis, iqr, correlacao_pearson, regressao_linear, r_quadrado, prever
)


def simular_lancamentos_moeda(n_lancamentos):
    """Simula n lancamentos de moeda (0=coroa, 1=cara) e retorna a lista de resultados."""
    return [random.randint(0, 1) for _ in range(n_lancamentos)]


def frequencia_relativa_acumulada(resultados):
    """Para cada lancamento, calcula a frequencia relativa acumulada de caras ate aquele ponto.
    Isso gera os pontos do grafico que mostra a convergencia."""
    frequencias = []
    soma_caras = 0
    for i, resultado in enumerate(resultados):
        soma_caras += resultado
        frequencias.append(soma_caras / (i + 1))
    return frequencias


def simular_medias_amostrais(dados_originais, tamanho_amostra, n_repeticoes):
    """Sorteia 'n_repeticoes' amostras de tamanho 'tamanho_amostra' da lista original,
    calcula a media de cada amostra sorteada e retorna a lista dessas medias."""
    medias_amostrais = []
    for _ in range(n_repeticoes):
        # random.sample sorteia sem reposicao (nao repete o mesmo registro na mesma amostra)
        amostra = random.sample(dados_originais, tamanho_amostra)
        media_da_amostra = media(amostra)
        medias_amostrais.append(media_da_amostra)
    return medias_amostrais


st.set_page_config(layout="wide")
st.title("Laboratório Estatístico - Saúde Cardiovascular")

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

# tamanho fixo dos graficos, pensado para caber dentro de meia tela (coluna)
TAMANHO_GRAFICO = (3.5, 2)

# ========== LINHA 1: MODULO 2 - DESCRITIVA NUMERICAS (esquerda) x CATEGORICAS (direita) ==========
linha1_esq, linha1_dir = st.columns(2, gap="large")

with linha1_esq:
    st.subheader("Estatística Descritiva - Variáveis Numéricas")

    # selectbox mostra o nome traduzido (format_func), mas guarda o nome real da coluna por baixo
    variavel_num = st.selectbox(
        "Escolha uma variável numérica:",
        colunas_numericas,
        format_func=lambda c: nomes_numericas[c]
    )

    # pega a coluna escolhida do DataFrame e transforma em lista Python simples,
    # que e o formato que nossas funcoes do minhastats.py esperam receber
    valores = dados[variavel_num].tolist()

    media_valor = media(valores)
    mediana_valor = mediana(valores)
    st.write(f"Média: {media_valor:.2f} | Mediana: {mediana_valor:.2f} | Moda: {moda(valores)}")
    st.write(f"Amplitude: {amplitude(valores):.2f} | Variância: {variancia(valores):.2f} | Desvio Padrão: {desvio_padrao(valores):.2f} | CV: {coeficiente_variacao(valores):.2f}%")

    # interpretacao textual automatica: compara media e mediana para inferir assimetria.
    # a diferenca e dividida pelo desvio padrao para ter uma escala comparavel entre variaveis diferentes
    diferenca_relativa = (media_valor - mediana_valor) / desvio_padrao(valores)
    if abs(diferenca_relativa) < 0.05:
        interpretacao = "A distribuição parece **aproximadamente simétrica**."
    elif diferenca_relativa > 0:
        interpretacao = "A distribuição parece **assimétrica à direita**."
    else:
        interpretacao = "A distribuição parece **assimétrica à esquerda**."
    st.info(interpretacao)

    # graficos empilhados verticalmente (a coluna ja e estreita, evita espremer mais ainda)
    fig1, ax1 = plt.subplots(figsize=TAMANHO_GRAFICO)
    ax1.hist(valores, bins=20, color="#4C72B0")
    ax1.set_title(f"Histograma — {nomes_numericas[variavel_num]}")
    st.pyplot(fig1, use_container_width=False)

    fig2, ax2 = plt.subplots(figsize=TAMANHO_GRAFICO)
    ax2.boxplot(valores, vert=True)
    ax2.set_title(f"Boxplot — {nomes_numericas[variavel_num]}")
    st.pyplot(fig2, use_container_width=False)

    # deteccao de outliers pela regra do IQR: valores fora de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
    q1, q2, q3 = quartis(valores)
    valor_iqr = iqr(valores)
    limite_inferior = q1 - 1.5 * valor_iqr
    limite_superior = q3 + 1.5 * valor_iqr
    outliers = [v for v in valores if v < limite_inferior or v > limite_superior]
    st.write(f"Q1={q1:.2f} | Q3={q3:.2f} | IQR={valor_iqr:.2f}")
    st.write(f"Outliers encontrados: **{len(outliers)}** ({len(outliers)/len(valores)*100:.1f}% dos dados)")

with linha1_dir:
    st.subheader("Estatística Descritiva - Variáveis Categóricas")

    # mesmo padrao do selectbox anterior: mostra nome traduzido, guarda nome real da coluna
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
    st.dataframe(tabela_frequencia)

    fig3, ax3 = plt.subplots(figsize=TAMANHO_GRAFICO)
    ax3.bar(tabela_frequencia["Categoria"], tabela_frequencia["Frequência"], color="#55A868")
    ax3.set_title(f"Barras — {nomes_categoricas[variavel_cat]}")
    st.pyplot(fig3, use_container_width=False)

    fig4, ax4 = plt.subplots(figsize=TAMANHO_GRAFICO)
    ax4.pie(tabela_frequencia["Frequência"], labels=tabela_frequencia["Categoria"], autopct="%1.1f%%")
    ax4.set_title(f"Pizza — {nomes_categoricas[variavel_cat]}")
    st.pyplot(fig4, use_container_width=False)

st.write("---")

# ========== LINHA 2: MODULO 3 - LEI DOS GRANDES NUMEROS (esquerda) x TEOREMA CENTRAL DO LIMITE (direita) ==========
linha2_esq, linha2_dir = st.columns(2, gap="large")

with linha2_esq:
    st.subheader("Simulação de Monte Carlo: Lei dos Grandes Números")

    # usuario controla quantos lancamentos de moeda serao simulados
    n_lancamentos = st.slider("Número de lançamentos da moeda:", min_value=10, max_value=10000, value=1000, step=10)

    resultados = simular_lancamentos_moeda(n_lancamentos)
    frequencias = frequencia_relativa_acumulada(resultados)

    fig5, ax5 = plt.subplots(figsize=TAMANHO_GRAFICO)
    ax5.plot(frequencias, color="#C44E52")
    ax5.axhline(y=0.5, color="black", linestyle="--", label="Prob. teórica (0.5)")
    ax5.set_xlabel("Nº de lançamentos")
    ax5.set_ylabel("Freq. relativa de caras")
    ax5.legend()
    st.pyplot(fig5, use_container_width=False)

    st.write(f"Frequência relativa final: {frequencias[-1]:.4f}")
    st.write("Quanto maior o número de lançamentos, mais a frequência relativa se aproxima da probabilidade teórica (0.5).")

with linha2_dir:
    st.subheader("Simulação de Monte Carlo: Teorema Central do Limite")

    # selectbox separado do de cima, precisa de 'key' unica para o Streamlit nao confundir os dois
    variavel_tcl = st.selectbox(
        "Escolha a variável para sortear amostras:",
        colunas_numericas,
        format_func=lambda c: nomes_numericas[c],
        key="tcl_variavel"
    )

    # usuario controla tamanho da amostra e numero de repeticoes
    tamanho_amostra = st.slider("Tamanho de cada amostra:", min_value=2, max_value=200, value=30, key="tcl_tamanho")
    n_repeticoes = st.slider("Número de amostras sorteadas:", min_value=10, max_value=5000, value=1000, key="tcl_repeticoes")

    dados_variavel_tcl = dados[variavel_tcl].tolist()
    medias_amostrais = simular_medias_amostrais(dados_variavel_tcl, tamanho_amostra, n_repeticoes)

    # histograma das medias amostrais: quanto maior o tamanho da amostra, mais proximo de uma Normal
    fig6, ax6 = plt.subplots(figsize=TAMANHO_GRAFICO)
    ax6.hist(medias_amostrais, bins=30, color="#8172B2")
    ax6.set_title(f"Médias amostrais — {nomes_numericas[variavel_tcl]}")
    ax6.set_xlabel("Média da amostra")
    ax6.set_ylabel("Frequência")
    st.pyplot(fig6, use_container_width=False)

    st.write(f"Média das médias: {media(medias_amostrais):.2f} | Desvio padrão: {desvio_padrao(medias_amostrais):.2f}")
    st.write("Aumentar o tamanho da amostra deixa esse histograma mais parecido com uma curva Normal.")

st.write("---")

# ========== LINHA 3: MODULO 4 - DISTRIBUICOES TEORICAS (esquerda) x MODULO 5 - REGRESSAO (direita) ==========
linha3_esq, linha3_dir = st.columns(2, gap="large")

with linha3_esq:
    st.subheader("Distribuições Teóricas")

    variavel_dist = st.selectbox(
        "Escolha a variável para ajustar a distribuição:",
        colunas_numericas,
        format_func=lambda c: nomes_numericas[c],
        key="dist_variavel"
    )

    dados_dist = dados[variavel_dist].tolist()
    media_dist = media(dados_dist)
    desvio_dist = desvio_padrao(dados_dist)
    x = sorted(dados_dist)

    fig7, ax7 = plt.subplots(figsize=TAMANHO_GRAFICO)
    # density=True normaliza o histograma para a mesma escala das curvas teoricas
    ax7.hist(dados_dist, bins=30, density=True, color="#4C72B0", alpha=0.6, label="Dados reais")

    # altura teorica da curva normal em cada ponto x, parametros vindos dos nossos proprios calculos
    curva_normal = stats.norm.pdf(x, media_dist, desvio_dist)
    ax7.plot(x, curva_normal, color="red", label="Normal")

    # uniforme.pdf espera (inicio, largura), por isso o segundo parametro e maximo - minimo
    minimo, maximo = min(dados_dist), max(dados_dist)
    curva_uniforme = stats.uniform.pdf(x, minimo, maximo - minimo)
    ax7.plot(x, curva_uniforme, color="green", label="Uniforme")

    ax7.set_title(f"Ajuste — {nomes_numericas[variavel_dist]}")
    ax7.legend()
    st.pyplot(fig7, use_container_width=False)

    st.write(f"Média = {media_dist:.2f}, Desvio padrão = {desvio_dist:.2f}")
    st.write("Quanto mais próxima a curva vermelha (Normal) estiver do histograma, mais a variável se aproxima de uma distribuição normal.")

with linha3_dir:
    st.subheader("Correlação e Regressão Linear")

    # dois selectbox lado a lado: usuario escolhe as duas variaveis a comparar
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        var_x = st.selectbox("Variável X:", colunas_numericas, format_func=lambda c: nomes_numericas[c], key="reg_x")
    with sub_col2:
        var_y = st.selectbox("Variável Y:", colunas_numericas, format_func=lambda c: nomes_numericas[c], key="reg_y")

    dados_x = dados[var_x].tolist()
    dados_y = dados[var_y].tolist()

    # calcula os tres resultados principais: forca da relacao, equacao da reta e qualidade do ajuste
    correlacao = correlacao_pearson(dados_x, dados_y)
    a, b = regressao_linear(dados_x, dados_y)
    r2 = r_quadrado(dados_x, dados_y)

    # dispersao dos dados reais + reta de regressao desenhada por cima
    fig8, ax8 = plt.subplots(figsize=TAMANHO_GRAFICO)
    ax8.scatter(dados_x, dados_y, alpha=0.3, color="#4C72B0", label="Dados")
    # a reta so precisa de 2 pontos (inicio e fim) para ser desenhada
    x_linha = [min(dados_x), max(dados_x)]
    y_linha = [prever(x_linha[0], a, b), prever(x_linha[1], a, b)]
    ax8.plot(x_linha, y_linha, color="red", label="Reta")
    ax8.set_xlabel(nomes_numericas[var_x])
    ax8.set_ylabel(nomes_numericas[var_y])
    ax8.legend()
    st.pyplot(fig8, use_container_width=False)

    st.write(f"Correlação: {correlacao:.4f} | Equação: Ŷ = {a:.4f} + {b:.4f}·X | R²: {r2:.4f}")
    # exigencia do enunciado: alertar que correlacao nao prova causa e efeito
    st.warning("Correlação não implica causalidade.")

    # predicao interativa: usuario digita um X e ve o Y previsto pela reta
    # valor inicial do campo e a propria media de X, para dar um ponto de partida razoavel
    x_input = st.number_input(f"Valor de {nomes_numericas[var_x]}:", value=float(media(dados_x)))
    y_previsto = prever(x_input, a, b)
    st.write(f"Previsão de {nomes_numericas[var_y]}: {y_previsto:.2f}")