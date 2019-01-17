import requests
import json
import pandas as pd
import webbrowser
import re
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

import consultaSIDRA

print('\n> Utilize a função "core()" diretamente, ou a função "guided()" para uma aplicação guiada.')
print('> Utilize "agr_table()" para consultar os agregados disponíveis.')
print('> Utilize "data_type_consulting(agr_id)", informando o ID do agregado, para conferir sua periodicidade.')

#######

print('\n*Em caso de dúvidas ao longo da inserção dos parâmetros, consulte http://api.sidra.ibge.gov.br/home/ajuda')

# https://servicodados.ibge.gov.br/api/v3/agregados    ####   dados agregados
# http://api.sidra.ibge.gov.br/    ####   consulta SIDRA
# http://api.sidra.ibge.gov.br/home/ajuda    ###   documentação API SIDRA

# A função "agr_table" apresenta ao usuário um DataFrame com todas as pesquisas e seus respectivos agregados disponíveis.

def agr_table():

    agregados = requests.get('https://servicodados.ibge.gov.br/api/v3/agregados')
    agregadosdata = json.loads(agregados.text)
    pesq_agr=[]
    for i in range(len(agregadosdata)):
        for j in range(len(agregadosdata[i]["agregados"])):
            id_pesquisa = (agregadosdata[i]["id"])
            nome_pesquisa = (agregadosdata[i]["nome"])
            id_agregado = (agregadosdata[i]["agregados"][j]["id"])
            nome_agregado = (agregadosdata[i]["agregados"][j]["nome"])
            pesq_agr.append({'ID pesquisa': id_pesquisa, 'Nome pesquisa': nome_pesquisa, 'ID agregado': id_agregado,
                            'Nome agregado': nome_agregado})
    df_pesq_agr = pd.DataFrame(pesq_agr)
    print(df_pesq_agr)

# A função "treat" é a responsável por tratar os dados que iremos requisitar da API com as funções "core" ou "guided".

def treat(resp):

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
    #print(df.dtypes)
    print(df.head())
    print(df.tail())

# A função data_type_consulting informa o usuário a respeito da periodicidade do agregado em questão.

def data_type_consulting(agr_id):
    from consultaSIDRA import data_type
    consultaSIDRA.code = agr_id
    data_type()

# A função 'guided', secundária nesse projeto, permite uma busca "guiada" para um usuário não familiarizado com a programação.

def guided():

    url = 'http://api.sidra.ibge.gov.br/values/'

    # Primera parte da função pede ao usuário o nome do agregado de dados desejado, e obtém o ID.
    # Esse ID obtido permite o acesso ao documento com as variáveis disponíveis para aquele agregado.
    # Ex1: "Número de estabelecimentos agropecuários, com agricultura familiar e não familiar, e Área dos estabelecimentos por grupos de atividade econômica, condição produtor em relação às terras e tipo de prática agrícola - (MDA)"
    # Ex2: "Comercialização de agrotóxicos e afins, total e por área plantada, segundo a classe de uso"
    # Ex3: "IPCA dessazonalizado - Variação mensal, acumulada no ano e peso mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços (a partir de janeiro/2012)"

    # t -> código do agregado de onde serão retirados os dados para as variáveis desejadas. Pode ser obtido pela API de agregados.
    # (Ex: '1327')

    nome = input('\nInsira o nome ou ID da tabela de dados agregados. >>>')

    if nome.isdigit():
        pesqid = nome

    else:
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
    treat(datares)
    return datares

# A função 'core' é a principal do projeto. Permite busca dos dados apenas com os parâmetros fornecidos pelo usuário.

def core(t,unt,p_ini,p_fim,v='allxp',c=None,f=None,d=None,h=None):

    # unt -> nível territorial + unidade territorial. Devem ser listadas em dicionários, dentro de uma lista.
    # Ex: [{"nvl_t": 1, "un_t": 1}]
    # Ex: [{"nvl_t": 7, "un_t": [2901,2301]}]
    # Ex: [{"nvl_t": 7, "un_t": [2901,2301]}, {"nvl_t": 1, "un_t": 1}]

    # p_ini -> período de início desejado para os dados.
    # Ex: 2008 -> Ano de 2008. Agregado de periodicidade anual.
    # Ex: 200809 -> Mês de setembro do ano de 2008. Agregado de periodicidade mensal.

    # p_fim -> período de término desejado para os dados.
    # Ex: 2010 -> Ano de 2010. Agregado de periodicidade anual.
    # Ex: 201009 -> Mês de setembro do ano de 2010. Agregado de periodicidade mensal.

    ### Vale ressaltar, para 'p_ini' e 'p_fim', que são diversos os tipos de periodicidade dentre as pesquisas.
    ### O usuário pode ser informado sobre a periodicidade do agregado desejado via a função 'data_type_consulting(agr_id)'.

    # v -> especifica o código das variáveis desejadas.
    # Ex: 132
    # Ex: [643,1127]

    # t -> código do agregado de onde serão retirados os dados para as variáveis desejadas. Pode ser obtido pela API de agregados.
    # Ex: 1327

    # c -> Classificação e categoria. Devem ser listadas em dicionários, dentro de uma lista.
    # Ex: [{"clas": 315, "cat": 7169}]
    # Ex: [{"clas": 315, "cat": [7173,7179]}]

    ##########

    # Construindo string com lista de variáveis inseridas pelo usuário:

    v_string = v
    if type(v) == list:
        v_string = str()
        for i in range(len(v)):
            if i != (len(v)-1):
                v_string = v_string + str(v[i]) + ","
            else:
                v_string = v_string + str(v[i])

    # Formatando o string relativo ao período desejado para a pesquisa, inserido pelo usuário:

    if p_ini == p_fim:
        p = str(p_ini)
    elif p_ini != p_fim:
        p = str(p_ini) + '-' + str(p_fim)

    url='http://api.sidra.ibge.gov.br/values' + '/p/' + str(p) + '/v/' + str(v_string)

    # Garantindo que temos o parâmetro 't', sem o qual os dados não podem ser obtidos.

    assert t != None, "O parâmetro 't' deve ser informado."

    # Permitindo que o usuário entre tanto com o código do agregado, quanto com o nome dele.

    if str(t).isdigit():
        url = url + '/t/' + str(t)

    else:
        pesqid = None
        agregados = requests.get('https://servicodados.ibge.gov.br/api/v3/agregados')
        agregadosdata = json.loads(agregados.text)
        for i in range(len(agregadosdata)):
            for j in range(len(agregadosdata[i]["agregados"])):
                if agregadosdata[i]["agregados"][j]["nome"] == str(t):
                    pesqid = (agregadosdata[i]["agregados"][j]["id"])
                    url = url + '/t/' + str(pesqid)
                    break
                elif agregadosdata[i]["agregados"][j]["nome"] != str(t) and j == (
                        len(agregadosdata[i]["agregados"][j]) - 1):
                    continue
                elif agregadosdata[i]["agregados"][j]["nome"] != str(t) \
                        and i == (len(agregadosdata) - 1) \
                        and j == (len(agregadosdata[i]["agregados"][j]) - 1):
                    print("Não há esse agregado de dados na base disponível")

    # Iteração dentro da lista de dicionários fornecidas pelo leitor para níveis e unidades territoriais:

    assert type(unt) == list, "O parâmentro 'unt' deve receber uma lista de dicionários."

    for i in range(len(unt)):
        url = str(url) + '/N' + str(unt[i]["nvl_t"]) + '/' + str(unt[i]["un_t"]).strip('[]')

    # Iteração dentro da lista de dicionários fornecidas pelo leitor para classificações e categorias:

    for i in range(len(c)):
        url = str(url) + '/C' + str(c[i]["clas"]) + '/' + str(c[i]["cat"]).strip('[]')

    # Correção para as duas iterações anteriores, que acrescentam espaços desnecessários no url:

    url = url.replace(" ", "")

    # Acréscimo, no URL, dos demais parâmetros da API, os quais não demandam maior manipulação.

    if f != None:
        url = url + '/f/' + str(f)

    if d != None:
        url = url + '/d/' + str(d)

    if h != None:
        url = url + '/h/' + str(h)

    # Visualização do URL:

    print(url)

    # Requisição a tratamento da base de dados recebida pela API:

    data = requests.get(url)
    datares = json.loads(data.text)
    treat(datares)
    return datares


# Testes:

#core(656,[{"nvl_t": 7, "un_t": [2901,2301]}, {"nvl_t": 1, "un_t": 1}],'last','last',66,[{"clas": 315, "cat": [7173,7179]}])
#core('IPCA - Peso mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços (de agosto/1999 até junho/2006)',[{"nvl_t": 7, "un_t": [2901,2301]}, {"nvl_t": 1, "un_t": 1}],'last','last',66,[{"clas": 315, "cat": [7173,7179]}])
#core(656,[{"nvl_t": 1, "un_t": 1}],'last','last',66,[{"clas": 315, "cat": [7173,7179]}])
#core(656,[{"nvl_t": 7, "un_t": [2901,2301]}],199910,200408,66,[{"clas": 315, "cat": 7169}])
#core(1998,[{"nvl_t":1,"un_t":1}],1996,1998,[630,864],[{"clas":11939,"cat":[96912,96913]}])
#core(1300,[{"nvl_t":1,"un_t":1},{"nvl_t":2,"un_t":[3,5]}],2008,2008,[337,1000337],[{"clas":12007,"cat":[98732,98807]}])

#guided()
#agr_table()
#data_type_consulting(656)

