# Web Crawler e Motor de Busca com Rank Personalizado

Este projeto implementa um mini-motor de busca que:

1. Rastreia (crawl) uma página inicial, encontra todos os links da página e, de forma recursiva, segue os links descobertos.

2. Indexa o conteúdo de cada página em um banco de dados MySQL, armazenando cada palavra e sua localização no texto.

Pesquisa links mais relevantes com base em duas (ou mais) palavras de busca, aplicando uma fórmula de rank que considera:

Frequência das palavras no texto

Localização das palavras (quanto mais próximo do início, melhor)

Distância entre as palavras no texto

O resultado é uma lista de URLs ordenadas por relevância, simulando o funcionamento básico de buscadores como Google, mas em escala reduzida e com pesos ajustáveis.

⚙️ Funcionalidades

Crawler recursivo:
A partir de uma lista de URLs iniciais, encontra e percorre novos links até a profundidade definida.

Indexação em banco de dados:
Registra cada palavra (exceto stopwords em português) e a posição em que aparece em cada página.

Ranking de relevância:
Combina frequência, localização e distância das palavras usando pesos configuráveis (w_freq, w_loc, w_dist).

🛠️ Tecnologias Utilizadas

Python 3

BeautifulSoup
 – parser HTML

NLTK
 – tratamento de texto e stopwords em português

PyMySQL
 – conexão com MySQL

urllib3
 – requisições HTTP

Banco de dados:

MySQL com tabelas:

urls – URLs indexadas

palavras – palavras encontradas

palavra_localizacao – relação palavra/URL/posição no texto

📊 Fórmula de Rank

Cada URL recebe um score calculado como:

score = (w_freq * log(1 + frequência))
      + (w_loc  * 1/(1 + localização))
      + (w_dist * 1/(1 + distância))


frequência: número de vezes que as palavras aparecem.

localização: soma das posições das palavras no texto (quanto menor, melhor).

distância: distância entre as palavras (quanto menor, melhor).

Pesos padrões:

Frequência: 2.0

Localização: 3.0

Distância: 1.0

Esses valores podem ser ajustados conforme a relevância desejada.

🚀 Como Executar

Configurar o MySQL
Crie um banco de dados chamado indice com as tabelas:

CREATE TABLE urls (
    idurl INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT
);
CREATE TABLE palavras (
    idpalavra INT AUTO_INCREMENT PRIMARY KEY,
    palavra VARCHAR(255)
);
CREATE TABLE palavra_localizacao (
    idurl INT,
    idpalavra INT,
    localizacao INT
);


Configurar o ambiente Python
Instale as dependências:

pip install beautifulsoup4 urllib3 pymysql nltk lxml


Baixe as stopwords do NLTK:

import nltk
nltk.download('stopwords')


Rodar o crawler
No final do script, defina a URL inicial e a profundidade:

listapaginas = ['https://ge.globo.com/futebol/times/fluminense/']
crawl(listapaginas, 1)


Isso vai indexar a página inicial e os links encontrados em 1 nível de profundidade.

Fazer uma pesquisa
Execute:

pesquisa('lesao samuel')


O programa retorna as 10 URLs mais relevantes, com o score calculado.

📌 Exemplo de Saída
8.5926  https://ge.globo.com/futebol/times/fluminense/noticia/2025/08/29/samuel-xavier-volta-ao-rio-de-janeiro...
4.9537  https://ge.globo.com/futebol/times/fluminense/noticia/2025/08/28/atuacoes-do-fluminense-freytes...
3.7268  https://ge.globo.com/futebol/times/fluminense/noticia/2025/08/29/analise-bola-pune-um-fluminense...
...

💡 Observações

As credenciais de acesso ao banco (usuário e senha) devem ser alteradas para o seu ambiente.

O exemplo usa português e stopwords da língua portuguesa.

Ideal para estudos de indexação de texto, web crawling e ranking de relevância.

📜 Licença

Este projeto é distribuído sob a licença MIT – veja o arquivo LICENSE
 para mais detalhes.

Autor

Eduardo Eira – LinkedIn
 | GitHub
