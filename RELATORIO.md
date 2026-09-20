# Relatório — Laboratório Estatístico Interativo

**Autora:** Jhéssica de Moura Lima — RA/DRT 72650126

## 1. Dataset e justificativa

Escolhi o **Cardiovascular Disease Dataset** (Kaggle), com 3.000 registros de pacientes, 5 variáveis numéricas (idade, altura, peso, pressão sistólica, pressão diastólica) e 6 variáveis categóricas (gênero, colesterol, glicose, fumante, consumo de álcool, atividade física). Escolhi esse tema porque o dataset traz relações fisiologicamente esperadas entre as variáveis (por exemplo, entre as duas medidas de pressão arterial), o que permite discutir com mais profundidade os resultados de correlação e regressão, além do alerta de que correlação não implica causalidade.

## 2. Decisões de implementação do núcleo estatístico

Todas as funções abaixo foram implementadas em `nucleo/minhastats.py`, sem usar funções estatísticas prontas de nenhuma biblioteca — apenas operações básicas de Python (`sum`, `len`, `sorted`, `min`, `max`).

### Medidas de tendência central

- **Média:** $\bar{x} = \dfrac{\sum x_i}{n}$
- **Mediana:** valor central da lista ordenada (média dos dois centrais quando `n` é par)
- **Moda:** valor(es) de maior frequência

### Medidas de dispersão

- **Amplitude:** $x_{max} - x_{min}$
- **Variância amostral:** $s^2 = \dfrac{\sum (x_i - \bar{x})^2}{n-1}$ (correção de Bessel, usada por padrão, já que o dataset é uma amostra de pacientes, não a população inteira)
- **Variância populacional:** $\sigma^2 = \dfrac{\sum (x_i - \bar{x})^2}{n}$
- **Desvio padrão:** raiz quadrada da variância
- **Coeficiente de variação:** $CV = \dfrac{s}{\bar{x}} \times 100$

### Posição

- **Percentil/Quartis:** calculados por interpolação linear (mesmo método padrão do `numpy.percentile`), para permitir validação direta contra o NumPy
- **IQR:** $Q_3 - Q_1$, usado na detecção de outliers pela regra $[Q_1 - 1{,}5 \cdot IQR,\ Q_3 + 1{,}5 \cdot IQR]$

### Relação entre variáveis

- **Covariância:** $Cov(x,y) = \dfrac{\sum(x_i - \bar{x})(y_i - \bar{y})}{n-1}$
- **Correlação de Pearson:** $r = \dfrac{Cov(x,y)}{s_x \cdot s_y}$
- **Regressão linear (mínimos quadrados):** $b = \dfrac{Cov(x,y)}{Var(x)}$, $a = \bar{y} - b\bar{x}$
- **R²:** $r^2$ (o quadrado da correlação de Pearson)

## 3. Resultados da validação

Todas as 15 funções do núcleo foram testadas automaticamente (`pytest`) comparando o resultado com NumPy/SciPy, com tolerância numérica de $1\times10^{-9}$. Todos os testes passaram (`15 passed`). A única exceção é a função `moda`, que não tem equivalente direto no NumPy — nesse caso, a validação foi feita comparando com o valor calculado manualmente.

## 4. Módulos da aplicação

**Módulo 2 - Estatística Descritiva:** o usuário escolhe uma variável (numérica ou categórica) e recebe medidas de tendência central e dispersão, tabela de frequências, histograma, boxplot, gráficos de barra/pizza, detecção de outliers via IQR e uma interpretação textual automática de assimetria (comparando média e mediana).

**Módulo 3 - Simulação de Monte Carlo:** duas demonstrações interativas — a Lei dos Grandes Números (frequência relativa de "cara" em lançamentos simulados de moeda se estabilizando perto de 0,5) e o Teorema Central do Limite (distribuição das médias de amostras repetidas se aproximando de uma Normal conforme o tamanho da amostra cresce).

**Módulo 4 - Distribuições Teóricas:** sobreposição de curvas teóricas (Normal e Uniforme) ao histograma real de qualquer variável numérica, com parâmetros estimados a partir dos próprios dados.

**Módulo 5 - Correlação e Regressão Linear:** o usuário escolhe duas variáveis numéricas e recebe o diagrama de dispersão, a reta de regressão, a equação, o R² e um campo de predição interativa.

![Estatística Descritiva](imagens/modulo2_descritiva.png)

![Simulação de Monte Carlo](imagens/modulo3_simulacao.png)

![Distribuições Teóricas](imagens/modulo4_distribuicoes.png)

![Correlação e Regressão](imagens/modulo5_regressao.png)

## 5. As três descobertas

**1. Outliers extremos na Pressão Diastólica.** Ao aplicar a regra do IQR na variável Pressão Diastólica, identifiquei 194 registros (6,5% do dataset) classificados como outliers, muitos com valores acima de 8.000, biologicamente impossíveis para pressão arterial humana. Isso indica erro de digitação na coleta original dos dados, não uma característica real da população.

**2. A Altura se aproxima bem de uma distribuição Normal.** Ao sobrepor a curva Normal teórica (Módulo 4) ao histograma da variável Altura, o ajuste visual foi muito bom, a curva acompanha de perto o formato dos dados reais, diferente da curva Uniforme, que claramente não representa a variável.

**3. Outliers distorcem a análise de correlação entre as pressões.** Era esperado que Pressão Sistólica e Pressão Diastólica tivessem correlação forte entre si (fisiologicamente, uma tende a acompanhar a outra). No entanto, a regressão calculada sobre todos os dados mostrou R² = 0,0073, praticamente nulo. Ao observar o gráfico de dispersão, ficou evidente que os mesmos outliers extremos identificados na descoberta 1 estão distorcendo o cálculo, os pontos "normais" (pressão sistólica abaixo de 200) mostram um padrão bem mais consistente entre si do que a reta de regressão final sugere. Isso reforça a importância de tratar outliers antes de qualquer análise de relação entre variáveis.