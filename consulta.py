# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 10:16:15 2025

@author: eduardo.eira
"""

from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin
import re
import nltk
import pymysql


def abrirConexao():
# Use 127.0.0.1 para garantir TCP. Autocommit DESLIGADO para commits por página.
    return pymysql.connect(
            host='127.0.0.1',
            user='root',
            passwd='ceub123456',
            db='indice',
            autocommit=False,
            use_unicode=True,
            charset='utf8mb4'
            )

def paginaIndexada(conn, url: str) -> int:
    """
    Retorna:
    -2 se URL já indexada (tem registros em palavra_localizacao)
    -1 se URL não existe na tabela urls
    >0 idurl se existe mas ainda não tem indexação
    """
    with conn.cursor() as cur:
        cur.execute('SELECT idurl FROM urls WHERE url = %s', (url,))
        row = cur.fetchone()
        if not row:
            return -1
        idurl = row[0]
        cur.execute('SELECT 1 FROM palavra_localizacao WHERE idurl = %s LIMIT 1', (idurl,))
        return -2 if cur.fetchone() else idurl


def insertPagina(conn, url: str) -> int:
    with conn.cursor() as cur:
        cur.execute('INSERT IGNORE INTO urls (url) VALUES (%s)', (url,))
        if cur.lastrowid:   # nova URL
            return cur.lastrowid
        # se já existia, buscar id
        cur.execute('SELECT idurl FROM urls WHERE url = %s', (url,))
        return cur.fetchone()[0]


def get_or_create_palavra(conn, palavra: str, cache: dict) -> int:
    """Busca id da palavra usando cache; se não existir, insere e cacheia."""
    if palavra in cache:
        return cache[palavra]
    with conn.cursor() as cur:
        cur.execute('SELECT idpalavra FROM palavras WHERE palavra = %s', (palavra,))
        row = cur.fetchone()
        if row:
            cache[palavra] = row[0]
            return row[0]
        cur.execute('INSERT INTO palavras (palavra) VALUES (%s)', (palavra,))
        pid = cur.lastrowid
        cache[palavra] = pid
        return pid

def insert_localizacoes_batch(conn, lotes):
    if not lotes:
        return
    with conn.cursor() as cur:
        cur.executemany(
            'INSERT INTO palavra_localizacao (idurl, idpalavra, localizacao) VALUES (%s, %s, %s)',
            lotes
        )


# Trata a sopa do html removendo tags de script e estilos
def getTexto(sopa):
   for tags in sopa(['script', 'style']):
       tags.decompose()
   return ' '.join(sopa.stripped_strings)



def separaPalavras(texto: str):
    stop = nltk.corpus.stopwords.words('portuguese')
    splitter = re.compile(r'\W+')
    lista_palavras = []
    for p in (x for x in splitter.split(texto) if x):
        plower = p.lower()
        if plower not in stop and len(plower) > 1:
            lista_palavras.append(plower)  # salva a palavra completa
    return lista_palavras


def indexador(conn, url: str, sopa: BeautifulSoup, cache_palavras: dict):
    status = paginaIndexada(conn, url)
    if status == -2:
        print('Url já indexada:', url)
        return
    elif status == -1:
        idpagina = insertPagina(conn, url)
    else:
        idpagina = status
    
    
    print('Indexando:', url)
    texto = getTexto(sopa)
    palavras = separaPalavras(texto)
    
    
    lotes = []
    for i, palavra in enumerate(palavras):
        pid = get_or_create_palavra(conn, palavra, cache_palavras)
        lotes.append((idpagina, pid, i))
    
    
    insert_localizacoes_batch(conn, lotes)
    conn.commit() # commit por página   
 
    
def crawl(paginas_iniciais, profundidade):
    print('Iniciando crawl para', len(paginas_iniciais), 'paginas')
    
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(
        num_pools=10,
        maxsize=20,
        retries=urllib3.Retry(total=2, redirect=2, backoff_factor=0.5),
        timeout=urllib3.Timeout(connect=5, read=10),
    )
    
    
    conn = abrirConexao()
    cache_palavras = {}
    visitados = set()
    
    
    try:
        _crawl_rec(paginas_iniciais, profundidade, http, conn, cache_palavras, visitados)
    finally:
        try:
            conn.commit()
        except Exception:
            pass
        conn.close()


def _crawl_rec(paginas, profundidade, http, conn, cache_palavras, visitados):
    novas_paginas = set()
    
    
    for pagina in paginas:
        if pagina in visitados:
            continue
        visitados.add(pagina)
        
        
        try:
            resp = http.request('GET', pagina)
        except Exception as e:
            print('Erro ao abrir a pagina', pagina, '-', e)
            continue
        
        
        sopa = BeautifulSoup(resp.data, 'lxml')
        indexador(conn, pagina, sopa, cache_palavras)
        
        
        if profundidade > 0:
            for a in sopa.find_all('a', href=True):
                href = a['href']
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                url = urljoin(pagina, href)
                novas_paginas.add(url)
        
    
    if profundidade > 0 and novas_paginas:
        print('Iniciando crawl para', len(novas_paginas), 'paginas (profundidade', profundidade-1, ')')
        _crawl_rec(novas_paginas, profundidade - 1, http, conn, cache_palavras, visitados)




if __name__ == '__main__':
    listapaginas = ['https://ge.globo.com/futebol/times/fluminense/']
    crawl(listapaginas, 1)
    print('Finalizado!!')

