import requests
import json
import pandas as pd
import webbrowser
import re
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

import consultaSIDRA

#######
# IMPORTANTE: A atual composição desse arquivo visa uma interface mais "user-friendly".
# Pensando nisso, tranformei o modelo passado (no qual o usuário deveria chamar uma função com as
# variáveis desejadas) em um modelo no qual o usuário vai respondendo a pedidos de inputs.
# Acredito, entretanto, que esse formato não seja o mais adequado.

#######

print('Em caso de dúvidas ao longo da inserção dos parâmetros, consulte http://api.sidra.ibge.gov.br/home/ajuda')

# https://servicodados.ibge.gov.br/api/v3/agregados    ####   dados agregados
# http://api.sidra.ibge.gov.br/    ####   consulta SIDRA
# http://api.sidra.ibge.gov.br/home/ajuda    ###   documentação API SIDRA

def conector():

    url = 'http://api.sidra.ibge.gov.br/values/'

    # Primera parte da função pede ao usuário o nome do agregado de dados desejado, e obtém o ID.
    # Esse ID obtido permite o acesso ao documento com as variáveis disponíveis para aquele agregado.
    # Ex1: "IPCA - Variação mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços (de julho/1989 até dezembro/1990)"
    # Ex2: "Comercialização de agrotóxicos e afins, total e por área plantada, segundo a classe de uso"

    # t -> código do agregado de onde serão retirados os dados para as variáveis desejadas. Pode ser obtido pela API de agregados.
    # (Ex: '1327')

    nome = input('\nInsira o nome da tabela de dados agregagos. >>>')
    pesqid = None
    agregados = requests.get('https://servicodados.ibge.gov.br/api/v3/agregados')
    agregadosdata = json.loads(agregados.text)
    for i in range(len(agregadosdata)):
        for j in range(len(agregadosdata[i]["agregados"])):
            if agregadosdata[i]["agregados"][j]["nome"] == str(nome):
                pesqid = (agregadosdata[i]["agregados"][j]["id"])
                break
            elif agregadosdata[i]["agregados"][j]["nome"] != str(nome) and j == (
                    len(agregadosdata[i]["agregados"][j]) - 1):
                continue
            elif agregadosdata[i]["agregados"][j]["nome"] != str(nome) \
                    and i == (len(agregadosdata) - 1) \
                    and j == (len(agregadosdata[i]["agregados"][j]) - 1):
                print("Não há esse agregado de dados na base disponível")

    consultaSIDRA.code = pesqid
    if pesqid != None:
        url = url + 't/' + str(pesqid) + "/"

    print('\nCom base nas informações desejadas observadas, insira as informações a seguir.')

    # unt -> nível territorial + unidade territorial. Pode assumir inúmeros valores, separados por barras.
    # (Ex: 'n1/1/n2/1').

    from consultaSIDRA import loclist
    loclist()

    untlist = []
    untlen = input('\n[OBRIGATÓRIO] Insira quantos níveis territoriais você deseja inserir. \n'
                   ' Ex: "1", "3", etc. >>>')
    assert int(untlen) > 0, 'Mínimo de 1 (um) nível territorial.'
    for i in range(int(untlen)):
        unt = input('\n[OBRIGATÓRIO] Insira os níveis territoriais, um a um, separados por uma barra "/" \n'
                    'de suas respectivas unidades territoriais separadas por vírgulas. \n'
                    ' Ex: "N1/1", "N7/2901,3101", etc. >>>')
        untlist.append(unt)
        url = url + str(untlist[i]) + '/'

    # p -> períodos desejados.
    # (Ex: '2008,2010-2012' – especifica os anos de 2008, e 2010 a 2012).

    from consultaSIDRA import plist
    plist()

    p = input('\n[OBRIGATÓRIO] Insira o período desejado para a pesquisa, no formato adequado. \n'
              ' Ex: "2008,2010-2012" – especifica os anos de 2008, e 2010 a 2012. \n'
              ' Para todos os períodos, insira "all". Para o último período, insira "last" >>>')
    assert p != str(), 'O valor de "p" é obrigatório para a consulta.'
    url = url + 'p/' + str(p)

    # v -> especifica o código das variáveis desejadas, separadas por vírgulas.
    # (Ex: '643,1127')

    from consultaSIDRA import varlist
    varlist()

    v = input('\n[OBRIGATÓRIO] Insira o código das variáveis desejadas, no formato adequado. \n'
              ' Ex: "63,69" - especifica as variáveis 63 e 69. Para não especificar o parâmetro, insira "all". >>>  ')
    assert v != str(), 'O valor de "v" é obrigatório para a consulta.'
    url = url + '/v/' + str(v) + '/'

    # cc -> classificação e categoria

    from consultaSIDRA import cclist
    cclist()

    cc = None
    cclist = []
    clen = input('\nQuantas classificações você deseja especificar?. Ex: "None", "2", etc.')
    if clen != str('None'):
        for i in range(int(clen)):
            cc = input('Insira as classificações, uma a uma, separadas por uma barra "/" de suas respectivas categorias separadas por vírgulas. \n'
                    'Ex: "C81/2692,2702", "C81/all", etc. >>>')
            cclist.append(str(cc))
            url = url + str(cclist[i]) + '/'

    f = input('\nEspecifique a formatação dos dados retornados ("a" (padrão), "c", "n" (recomendado) ou "u").')
    assert f == "c" or f == "n" or f == "u" or f == "a", 'O valor de 'f' inserido não é válido.'
    if f != str('None'):
        url = url + 'f/' + str(f) + '/'

    d = input('\nEspecifique o número de casas decimais, \n'
              '("s" (padrão para cada pesquisa), "m" (máximo disponível), ou um valor de 0 até 9). >>>')
    for i in range(9):
        assert d == "s" or d == "m" or d == int(i), 'O valor de "d" inserido não é válido.'

    if d != str('None') and d != str():
        url = url + 'd/' + str(d)

    #if h != None:
        #url = url + '/h/' + str(h)

    print(url)

    data = requests.get(url)
    datares = json.loads(data.text)
    return datares

########

def treat():

    resp = conector()

    dflist = []

    for d in resp[1:]:
        s = pd.Series(d)
        dflist.append(s.to_frame().T)

    df = pd.concat(dflist)

    df.columns = df.columns.map(resp[0])

    # Linhas de código para tratamento de variáveis removidas até que eu compreenda se tal tratamento seria possível.

    #pd.options.display.max_columns = 14

    ### Corrige o índice de entradas do DataFrame
    df.to_dict('records')
    df = df.reset_index(drop=True)
    print(df.dtypes)
    #print(df.head())
    print(df.tail())

#####

treat()
