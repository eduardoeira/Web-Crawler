# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 10:55:20 2025

@author: eduardo.eira
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 15:19:29 2024

@author: vtfernand
"""

import nltk
import pymysql
import math


def getIdPalavra(palavra):
    retorno = -1 #não existe a palavra no índice
    conexao = pymysql.connect(host='localhost', user='root',passwd='ceub123456', db='indice', use_unicode=True, charset="utf8mb4")
    cursor = conexao.cursor()
    cursor.execute('select idpalavra from palavras where palavra = %s', palavra)
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return retorno

def frequenciaScore(linhas):
    contagem = dict([(linha[0], 0) for linha in linhas])
    for linha in linhas:
        #print(linha)
        contagem[linha[0]] += 1
    return contagem

def localizacaoScore(linhas):
    localizacoes = dict([linha[0], 1000000] for linha in linhas)
    for linha in linhas:
        #print(linha)
        #agora, saltando linha[0] que é o índice da linha
        soma = sum(linha[1:]) #somando as localizações das palavras encontradas
        if soma < localizacoes[linha[0]]: #se o score da página for menor que 1 milhão, no valor inicial, e menor que os demais
            localizacoes[linha[0]] = soma
    return localizacoes

def distanciaScore(linhas):
    if len(linhas[0]) <= 2: #senão tiver ao menos 2 palavras para calcular a distância entre elas
        return dict([(linha[0], 1.0) for linha in linhas]) #caso seja com 1 palavra, o retorno será 1
    distancias = dict([(linha[0], 1000000) for linha in linhas])
    for linha in linhas: #todos os resultados que retornados pela base de dados
        dist = sum([abs(linha[i] - linha[i - 1]) for i in range(2, len(linha))]) #calcula a distância entre as palavras
        if dist < distancias[linha[0]]: #se a distância for menor do que as demais
            distancias[linha[0]] = dist #substitui a distância por uma menor ainda
    return distancias

def buscaMaisPalavras(consulta):
    listacampos = 'p1.idurl'
    listatabelas = ''
    listaclausulas = ''
    palavrasid = []
    
    palavras = consulta.split(' ')
    numerotabela = 1
    for palavra in palavras:
        idpalavra = getIdPalavra(palavra)
        if idpalavra > 0:
            palavrasid.append(idpalavra)
            if numerotabela > 1:
                listatabelas += ', '
                listaclausulas += ' and '
                listaclausulas += 'p%d.idurl = p%d.idurl and ' % (numerotabela - 1, numerotabela)
            listacampos += ', p%d.localizacao' % numerotabela
            listatabelas += ' palavra_localizacao p%d' % numerotabela
            listaclausulas += 'p%d.idpalavra = %d' % (numerotabela, idpalavra)
            numerotabela += 1
    consultacompleta = 'SELECT %s FROM %s WHERE %s' % (listacampos, listatabelas, listaclausulas)
    
    conexao = pymysql.connect(host='localhost', user='root', passwd='ceub123456', db='indice')
    cursor = conexao.cursor()
    cursor.execute(consultacompleta)
    linhas = [linha for linha in cursor]
    cursor.close()
    conexao.close()  
    return linhas, palavrasid


def pesquisa(consulta, w_freq=2.0, w_loc=3.0, w_dist=1.0):
    """
    Busca e rankeia URLs por relevância.
    Pesos default: frequência 1.0, localização 1.0, distância 3.0 (mais importante)
    """
    linhas, palavrasid = buscaMaisPalavras(consulta)

    freq_scores = frequenciaScore(linhas)
    loc_scores = localizacaoScore(linhas)
    dist_scores = distanciaScore(linhas)

    scores = {}
    for url in freq_scores.keys():
        f = freq_scores.get(url, 0)
        l = loc_scores.get(url, 1000000)
        d = dist_scores.get(url, 1000000)

        f_log = math.log(1 + f)  # escala logarítmica da frequência
        l_norm = 1.0 / (1 + l)   # menor localização -> melhor
        d_norm = 1.0 / (1 + d)   # menor distância -> melhor

        # aplica os pesos
        score_final = w_freq * f_log + w_loc * l_norm + w_dist * d_norm

        scores[url] = score_final

    # ordena do maior para o menor
    scoresordenado = sorted([(score, url) for (url, score) in scores.items()], reverse=True)

    for (score, idurl) in scoresordenado[0:10]:
        print('%.4f\t%s' % (score, getUrl(idurl)))


def getUrl(idurl):
    retorno = ''
    conexao = pymysql.connect(host='localhost', user='root', passwd='ceub123456', db='indice')
    cursor = conexao.cursor()
    cursor.execute('select url from urls where idurl = %s', idurl)
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return retorno

#print(pesquisa('python programação')) # reposta NONE
pesquisa('xxxxx yyyyy') 


