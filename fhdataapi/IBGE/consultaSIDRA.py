# Arquivo para testar a possibilidade de retornar as informações da página de consulta diretamente pelo Python, via webscrapping.

#import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re

def baixadados():
    code = input('Insira o código da tabela de agregados. >>>')
    myurl = 'http://api.sidra.ibge.gov.br/desctabapi.aspx?c=' + str(code)
    #print(myurl)

    #Estabelece conexão e baixa o HTML da página.
    uClient = uReq(myurl)
    page_html = uClient.read()
    uClient.close()

    # Faz o parsing para o HTML da página
    pagesoup = soup(page_html, "html.parser")
    return pagesoup

def varlist():
    # Gera lista das variáveis disponíveis.

    page_soup = baixadados()

    # Obtém o título da parte de variáveis do HTML, que fornece o número de variáveis disponiveis.
    # O número de variáveis disponíveis é retirado do título.
    # Com esse número de variáveis poderemos obter o nome de cada uma delas, via iteração.
    vart = (page_soup.find("span",{"id":"lblVariaveis"}).text)
    strvar = str(vart)
    strnum = (re.findall('\d+', strvar))
    strvar = int(strnum[0])

    # Uma vez obtido o número de variáveis, expomos seus nomes e códigos para o usuário.
    print("Variáveis disponíveis na tabela SIDRA requisitada:")
    for i in range(strvar):
        varname = "lstVariaveis_lblNomeVariavel_" + str(i)
        varn = (page_soup.find("span", {"id": varname}).text)

        varcode = "lstVariaveis_lblIdVariavel_" + str(i)
        varc = (page_soup.find("span", {"id": varcode}).text)

        print("[Código: " + varc + "] " + varn)

#varlist()

#### Função para nível territorial deverá ser melhor pensada, já que incluirá dados de outras
#### páginas (as de unidades territoriais, para cada um dos níveis territoriais).

def plist():
    # Gera lista dos períodos disponíveis.

    page_soup = baixadados()

    pnome = (page_soup.find("span", {"id": "lblNomePeriodo"}).text)

    pdisp = (page_soup.find("span", {"id":"lblPeriodoDisponibilidade"}).text)

    print('Os períodos disponíveis encontram-se no formato "' + str(pnome) +
          '". \nOs quatro primeiros digitos correspondem ao ano, e os últimos dois ao mês em questão. \nSão esses os períodos disponíveis:')
    print(pdisp)

#plist()

#### Função para classificações e categorias deverá ser melhor pensada, já que preciso
#### pensar em um modo para torná-la iterável universalmente entre as diferentes tabelas de agregados.

### Uma vez que eu consiga criar a função para "nível e unidade territorial" e "classificação e categoria",
### essas funções poderão ser inseridas no arquivo "APISIDRA" (com devidas correções) para visualização do usuário,
### que reconhecerá os inputs possíveis sem necessidade de acessar uma página da web.


