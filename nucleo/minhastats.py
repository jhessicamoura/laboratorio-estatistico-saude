def media (numeros):
    soma = sum(numeros)
    quantidade = len(numeros)
    resultado = soma / quantidade
    return resultado

def mediana (numeros):
    ordenado = sorted(numeros)
    n = len(ordenado)
    meio = n // 2
    if n % 2 == 1:
        return ordenado[meio]
    else:
        return (ordenado[meio - 1] + ordenado[meio]) / 2

def moda (numeros):
    contagem = {}
    for numero in numeros:
        contagem[numero] = contagem.get(numero, 0) + 1
    maior_frequencia = max(contagem.values())
    modas = [numero for numero, freq in contagem.items() if freq == maior_frequencia]
    return modas 

def amplitude(numeros):
    return max(numeros) - min(numeros)

def variancia(numeros, populacional=False):
    n = len(numeros)
    media_dados = media(numeros)
    soma_quadrados = sum((x - media_dados) ** 2 for x in numeros)
    if populacional:
        return soma_quadrados / n
    else:
        return soma_quadrados / (n - 1)

def desvio_padrao(numeros, populacional=False):
    return variancia(numeros, populacional) ** 0.5

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
