def media(numeros):
    """Calcula a media aritmetica simples de uma lista de numeros."""
    soma = sum(numeros)
    quantidade = len(numeros)
    resultado = soma / quantidade
    return resultado


def mediana(numeros):
    """Calcula a mediana: valor central de uma lista ordenada."""
    ordenado = sorted(numeros)  # faz o "rol": organiza do menor para o maior
    n = len(ordenado)
    meio = n // 2  # posicao central (divisao inteira)
    if n % 2 == 1:
        # quantidade impar: pega o valor exatamente do meio
        return ordenado[meio]
    else:
        # quantidade par: tira a media dos dois valores centrais
        return (ordenado[meio - 1] + ordenado[meio]) / 2


def moda(numeros):
    """Calcula a moda: valor(es) mais frequente(s). Retorna lista (pode ter mais de uma moda)."""
    contagem = {}  # dicionario: numero -> quantas vezes apareceu
    for numero in numeros:
        contagem[numero] = contagem.get(numero, 0) + 1
    maior_frequencia = max(contagem.values())
    # pega todos os numeros que empataram na maior frequencia (multimodal)
    modas = [numero for numero, freq in contagem.items() if freq == maior_frequencia]
    return modas


def amplitude(numeros):
    """Calcula a amplitude: diferenca entre o maior e o menor valor."""
    return max(numeros) - min(numeros)


def variancia(numeros, populacional=False):
    """Calcula a variancia. Por padrao, amostral (divide por n-1, correcao de Bessel),
    pois nosso dataset e uma amostra de pacientes, nao a populacao inteira."""
    n = len(numeros)
    media_dados = media(numeros)
    soma_quadrados = sum((x - media_dados) ** 2 for x in numeros)
    if populacional:
        return soma_quadrados / n
    else:
        return soma_quadrados / (n - 1)


def desvio_padrao(numeros, populacional=False):
    """Calcula o desvio padrao: raiz quadrada da variancia.
    Devolve o resultado na mesma unidade original dos dados."""
    return variancia(numeros, populacional) ** 0.5


def percentil(numeros, p):
    """Calcula o percentil p de uma lista, usando interpolacao linear
    (mesmo metodo padrao do numpy.percentile), para bater na validacao."""
    ordenado = sorted(numeros)
    n = len(ordenado)
    posicao = (p / 100) * (n - 1)  # posicao teorica (pode ser fracionaria)
    piso = int(posicao)  # parte inteira da posicao
    resto = posicao - piso  # parte decimal, usada para interpolar
    if piso + 1 < n:
        # interpola entre o valor na posicao 'piso' e o proximo
        return ordenado[piso] + resto * (ordenado[piso + 1] - ordenado[piso])
    else:
        # caso de borda: ultima posicao da lista, sem proximo valor
        return ordenado[piso]


def quartis(numeros):
    """Calcula Q1 (25%), Q2/mediana (50%) e Q3 (75%)."""
    q1 = percentil(numeros, 25)
    q2 = percentil(numeros, 50)
    q3 = percentil(numeros, 75)
    return q1, q2, q3


def iqr(numeros):
    """Calcula o IQR (intervalo interquartil): Q3 - Q1.
    Usado para detectar outliers pela regra de 1.5*IQR."""
    q1, _, q3 = quartis(numeros)  # "_" descarta a mediana, nao usada aqui
    return q3 - q1


def coeficiente_variacao(numeros):
    """Calcula o coeficiente de variacao: desvio padrao relativo a media, em %.
    Util para comparar dispersao entre variaveis de escalas diferentes."""
    media_dados = media(numeros)
    desvio = desvio_padrao(numeros)
    return (desvio / media_dados) * 100


def covariancia(x, y, populacional=False):
    """Calcula a covariancia entre duas variaveis (listas de mesmo tamanho).
    Positiva: variam juntas. Negativa: variam em sentidos opostos."""
    n = len(x)
    media_x = media(x)
    media_y = media(y)
    soma_produtos = sum((x[i] - media_x) * (y[i] - media_y) for i in range(n))
    if populacional:
        return soma_produtos / n
    else:
        return soma_produtos / (n - 1)


def correlacao_pearson(x, y):
    """Calcula a correlacao de Pearson: covariancia normalizada entre -1 e 1,
    independente da unidade das variaveis."""
    cov = covariancia(x, y)
    desvio_x = desvio_padrao(x)
    desvio_y = desvio_padrao(y)
    return cov / (desvio_x * desvio_y)


if __name__ == "__main__":
    idades = [18393, 20228, 18857, 17623, 17474]
    print(media(idades))

    notas = [7, 8, 8, 9, 8, 6]
    print(mediana(notas))
    print(moda(notas))

    turma_b = [2, 6, 10, 10]
    print(amplitude(turma_b))
    print(variancia(turma_b))
    print(desvio_padrao(turma_b))

    dados_iqr = [8, 2, 12, 4, 10, 4, 6]
    print(percentil(dados_iqr, 90))
    print(quartis(dados_iqr))
    print(iqr(dados_iqr))

    pesos = [60, 70, 80, 90, 100]
    alturas = [160, 165, 175, 180, 190]
    print(coeficiente_variacao(turma_b))
    print(covariancia(pesos, alturas))
    print(correlacao_pearson(pesos, alturas))