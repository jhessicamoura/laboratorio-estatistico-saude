import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from nucleo.minhastats import (
    media, mediana, moda, amplitude, variancia, desvio_padrao,
    percentil, quartis, iqr, coeficiente_variacao, covariancia, correlacao_pearson, regressao_linear, r_quadrado
)


def test_media_bate_com_numpy():
    dados = [2, 6, 10, 10, 15, 20, 3]
    assert abs(media(dados) - np.mean(dados)) < 1e-9


def test_mediana_bate_com_numpy():
    dados = [2, 6, 10, 10, 15, 20, 3]
    assert abs(mediana(dados) - np.median(dados)) < 1e-9


def test_moda_bate_com_valor_esperado():
    # moda nao tem funcao direta e universal no numpy, entao comparamos
    # com o valor que sabemos ser correto manualmente
    dados = [7, 8, 8, 9, 8, 6]
    assert moda(dados) == [8]


def test_amplitude_bate_com_numpy():
    dados = [2, 6, 10, 10, 15, 20, 3]
    esperado = np.max(dados) - np.min(dados)
    assert amplitude(dados) == esperado


def test_variancia_amostral_bate_com_numpy():
    dados = [2, 6, 10, 10, 15, 20, 3]
    # ddof=1 diz ao numpy para usar n-1 (amostral), o padrao dele e ddof=0 (populacional)
    esperado = np.var(dados, ddof=1)
    assert abs(variancia(dados) - esperado) < 1e-9


def test_variancia_populacional_bate_com_numpy():
    dados = [2, 6, 10, 10, 15, 20, 3]
    esperado = np.var(dados, ddof=0)
    assert abs(variancia(dados, populacional=True) - esperado) < 1e-9


def test_desvio_padrao_amostral_bate_com_numpy():
    dados = [2, 6, 10, 10, 15, 20, 3]
    esperado = np.std(dados, ddof=1)
    assert abs(desvio_padrao(dados) - esperado) < 1e-9


def test_percentil_bate_com_numpy():
    dados = [8, 2, 12, 4, 10, 4, 6]
    esperado = np.percentile(dados, 75)
    assert abs(percentil(dados, 75) - esperado) < 1e-9


def test_quartis_bate_com_numpy():
    dados = [8, 2, 12, 4, 10, 4, 6]
    q1, q2, q3 = quartis(dados)
    assert abs(q1 - np.percentile(dados, 25)) < 1e-9
    assert abs(q2 - np.percentile(dados, 50)) < 1e-9
    assert abs(q3 - np.percentile(dados, 75)) < 1e-9


def test_iqr_bate_com_numpy():
    dados = [8, 2, 12, 4, 10, 4, 6]
    esperado = np.percentile(dados, 75) - np.percentile(dados, 25)
    assert abs(iqr(dados) - esperado) < 1e-9


def test_coeficiente_variacao_bate_com_calculo_manual():
    dados = [2, 6, 10, 10]
    # nao existe funcao pronta de CV no numpy, entao calculamos manualmente aqui
    esperado = (np.std(dados, ddof=1) / np.mean(dados)) * 100
    assert abs(coeficiente_variacao(dados) - esperado) < 1e-9


def test_covariancia_bate_com_numpy():
    x = [60, 70, 80, 90, 100]
    y = [160, 165, 175, 180, 190]
    # numpy.cov retorna uma matriz 2x2; a covariancia entre x e y fica na posicao [0][1]
    esperado = np.cov(x, y, ddof=1)[0][1]
    assert abs(covariancia(x, y) - esperado) < 1e-9


def test_correlacao_pearson_bate_com_numpy():
    x = [60, 70, 80, 90, 100]
    y = [160, 165, 175, 180, 190]
    # numpy.corrcoef tambem retorna matriz 2x2; correlacao fica na posicao [0][1]
    esperado = np.corrcoef(x, y)[0][1]
    assert abs(correlacao_pearson(x, y) - esperado) < 1e-9

def test_regressao_linear_bate_com_numpy():
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 5, 4, 5]
    a, b = regressao_linear(x, y)
    # numpy.polyfit retorna [b, a] nessa ordem (inclinacao primeiro, intercepto depois)
    b_esperado, a_esperado = np.polyfit(x, y, 1)
    assert abs(a - a_esperado) < 1e-9
    assert abs(b - b_esperado) < 1e-9


def test_r_quadrado_bate_com_numpy():
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 5, 4, 5]
    esperado = np.corrcoef(x, y)[0][1] ** 2
    assert abs(r_quadrado(x, y) - esperado) < 1e-9