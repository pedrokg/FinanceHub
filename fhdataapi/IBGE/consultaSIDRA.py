# Arquivo para testar a possibilidade de retornar as informações da página de consulta diretamente pelo Python, via webscrapping.

#import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re

#code = input('Insira o código da tabela de agregados. >>>')

def baixadados():

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
    print("\nVariáveis disponíveis na tabela SIDRA requisitada:")
    for i in range(strvar):
        varname = "lstVariaveis_lblNomeVariavel_" + str(i)
        varn = (page_soup.find("span", {"id": varname}).text)

        varcode = "lstVariaveis_lblIdVariavel_" + str(i)
        varc = (page_soup.find("span", {"id": varcode}).text)

        print("[Código: " + varc + "] " + varn)

#varlist()


def loclist():

    page_soup = baixadados()

    # Contando o número de níveis territoriais
    tercont = page_soup.findAll("a",{},True,'Listar unidades territoriais')
    lenter = len(tercont)

    utlist=[]
    msg=[]
    for i in range(lenter):
        locname = "lstNiveisTerritoriais_lblNomeNivelterritorial_" + str(i)
        locn = (page_soup.find("span", {"id": locname}).text)

        loccode = "lstNiveisTerritoriais_lblIdNivelterritorial_" + str(i)
        utcode = str((page_soup.find("span", {"id": loccode}).text))
        locc = "N" + utcode

        msg.append("[Código: " + str(locc) + "] " + str(locn))
        #print(msg)
        utlist.append(utcode)

    #print(utlist)

    # Baixando dados específicos de cada região
    url_utlist = []
    utsl = []
    utsoup = []
    for i in range(len(utlist)):
        url_utlist.append('http://api.sidra.ibge.gov.br/LisUnitTabAPI.aspx?c=' + str(code) + '&n=' + (utlist[i]) + '&i=P')

        # Estabelece conexão e baixa o HTML da página.
        utClient = uReq(url_utlist[i])
        ut_html = utClient.read()
        utClient.close()

        # Faz o parsing para o HTML da página
        utsoup.append(soup(ut_html, "html.parser"))
        utsl.append((utsoup[i].find("table",{"id":"grdUnidadeTerritorial"},"td")).text)
        #print(teste)

    for i in range(len(utlist)):
        print(msg[i])
        print("     " + utsl[i])


#loclist()


def cclist():

    page_soup = baixadados()

    # Contando o número de classificações
    clascont = page_soup.findAll("span",{},True,'/C')
    lenclas = len(clascont)

    #print(lenclas)

    lennum = []

    print("\nA seguir, todas as classificações com suas respectivas categorias.")

    for i in range(lenclas):
        clas_id_code = "lstClassificacoes_lblIdClassificacao_" + str(i)
        clas_id = (page_soup.find("span", {"id": clas_id_code}).text)

        clas_name_code = "lstClassificacoes_lblClassificacao_" + str(i)
        clas_name = str((page_soup.find("span", {"id": clas_name_code}).text))

        # Obtém a quantidade de categorias por classificação. Usar com método de retirar números de strings.
        #clas_quant_code = "lstClassificacoes_lblQuantidadeCategorias_" + str(i)
        #clas_quant = str((page_soup.find("span", {"id": clas_quant_code}).text))

        print("\n[Código: /C" + clas_id + "/] " + clas_name)

        clast_code = "lstClassificacoes_lblQuantidadeCategorias_" + str(i)
        clast = (page_soup.find("span",{"id":clast_code}).text)
        strclas = str(clast)
        strclas_num = (re.findall('\d+', strclas))
        lennum.append(int(strclas_num[0]))
        #print(lennum[i])

        for j in range(lennum[i]):

            cat_name_code = "lstClassificacoes_lstCategorias_0_lblNomeCategoria_" + str(j)
            cat_name = (page_soup.find("span", {"id": cat_name_code}).text)

            cat_id_code = "lstClassificacoes_lstCategorias_0_lblIdCategoria_" + str(j)
            cat_id = (page_soup.find("span", {"id": cat_id_code}).text)

            print("     [Código: " + cat_id + "] " + cat_name)

#cclist()


def plist():
    # Gera lista dos períodos disponíveis.

    page_soup = baixadados()

    pnome = (page_soup.find("span", {"id": "lblNomePeriodo"}).text)

    pdisp = (page_soup.find("span", {"id":"lblPeriodoDisponibilidade"}).text)

    print('\nOs períodos disponíveis encontram-se no formato "' + str(pnome) +
          '". \nSão esses os períodos disponíveis:')
    print(pdisp)

def data_type():
    page_soup = baixadados()
    data_type_text = str((page_soup.find("span", {"id":'lblNomePeriodo'}).text))

    if data_type_text[0] == "M":
        period = 'Mensal'
    elif data_type_text[0] == "S":
        period = 'Semestral'
    elif data_type_text[0] == "A":
        period = 'Anual'
    elif data_type_text[0] == "T":
        period = 'Trimestral'
    print('\nPeriodicidade: ' + period)
