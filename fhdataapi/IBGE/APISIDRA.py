import requests
import json
import pandas as pd
import webbrowser

print('Em caso de dúvidas ao longo da inserção dos parâmetros, consulte http://api.sidra.ibge.gov.br/home/ajuda')

# https://servicodados.ibge.gov.br/api/v3/agregados    ####   dados agregados
# http://api.sidra.ibge.gov.br/    ####   consulta SIDRA
# http://api.sidra.ibge.gov.br/home/ajuda    ###   documentação API SIDRA

def conector():

    url = 'http://api.sidra.ibge.gov.br/values/'

    # Primera parte da função pede ao usuário o nome do agregado de dados desejado, e obtém o ID.
    # Esse ID obtido permite o acesso ao documento com as variáveis disponíveis para aquele agregado.
    # Ex1 a ser inserido: "IPCA - Variação mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços (de julho/1989 até dezembro/1990)"
    # Ex2 a ser inserido: "Comercialização de agrotóxicos e afins, total e por área plantada, segundo a classe de uso"

    # t -> código do agregado de onde serão retirados os dados para as variáveis desejadas. Pode ser obtido pela API de agregados.
    # (Ex: '1327')
    nome = input('Insira o nome do agregado de dados desejado, de onde os dados deverão ser retirados:')
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

    if pesqid != None:
        url = url + '/t/' + str(pesqid) + "/"

    # Página com vaariáveis a serem inseridas na consulta é aberta para o usuário.
    # Tal formato pode ser menos ideal em comparação a um web scraping que permite a visualização dessas informações no próprio Python.
    # Com isso, essa parte do código é provisória e será refinada.
    urlcon = 'http://api.sidra.ibge.gov.br/desctabapi.aspx?c=' + str(pesqid)
    webbrowser.open(urlcon, new=1, autoraise=True)

    print('Com base nas informações desejadas observadas, insira as informações a seguir.')

    # unt -> nível territorial + unidade territorial. Pode assumir inúmeros valores, separados por barras.
    # (Ex: 'n1/1/n2/1').
    untlist = []
    untlen = input('[OBRIGATÓRIO] Insira quantos níveis territoriais você deseja inserir. Ex: "1", "3", etc.:')
    assert int(untlen) > 0, 'Mínimo de 1 (um) nível territorial.'
    for i in range(int(untlen)):
        unt = input('[OBRIGATÓRIO] Insira os níveis territoriais, um a um, separados por uma barra "/" de suas'
                    ' respectivas unidades territoriais separadas por vírgulas.'
                    ' Ex: "N1/1", "N7/2901,3101", etc.')
        untlist.append(unt)
        url = url + str(untlist[i]) + '/'

    # p -> períodos desejados.
    # (Ex: '2008,2010-2012' – especifica os anos de 2008, e 2010 a 2012).
    p = input('[OBRIGATÓRIO] Insira o período desejado para a pesquisa, no formato adequado.'
              ' Ex: "2008,2010-2012" – especifica os anos de 2008, e 2010 a 2012. '
              ' Para todos os períodos, insira "all". Para o último período, insira "last"')
    assert p != str(), 'O valor de "p" é obrigatório para a consulta.'
    url = url + 'p/' + str(p)

    # v -> especifica o código das variáveis desejadas, separadas por vírgulas.
    # (Ex: '643,1127')
    v = input('[OBRIGATÓRIO] Insira o código das variáveis desejadas, no formato adequado.'
              ' Ex: "63,69" - especifica as variáveis 63 e 69. Para não especificar o parâmetro, insira "all".')
    assert v != str(), 'O valor de "v" é obrigatório para a consulta.'
    url = url + '/v/' + str(v) + '/'

    # cc -> classificação e categoria
    cc = None
    cclist = []
    clen = input('Quantas classificações você deseja especificar?. Ex: "None", "2", etc.')
    if clen != str('None'):
        for i in range(int(clen)):
            cc = input('Insira as classificações, uma a uma, separadas por uma barra "/" de suas'
                    ' respectivas categorias separadas por vírgulas.'
                    ' Ex: "C81/2692,2702", "C81/all", etc.')
            cclist.append(cc)
            url = url + str(cclist[i]) + '/'

    f = input('Especifique a formatação dos dados retornados ("None", "c", "n", "u" ou "a").')
    if f != str('None'):
        url = url + 'f/' + str(f) + '/'

    d = input('Especifique o número de casas decimais, ("s" (padrão), "m", ou um valor de 0 até 9).')
    if d != str('None'):
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

    pd.options.display.max_columns = 20

    ### Corrige o índice de entradas do DataFrame
    df.to_dict('records')
    df = df.reset_index(drop=True)
    print(df.dtypes)
    #print(df.head())
    print(df.tail())

#####

treat()