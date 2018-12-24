import requests
import json
import pandas as pd
import webbrowser

# https://servicodados.ibge.gov.br/api/v3/agregados    ####   dados agregados
# http://api.sidra.ibge.gov.br/    ####   consulta SIDRA
# http://api.sidra.ibge.gov.br/home/ajuda    ###   documentação API SIDRA

# Primera parte do código pede ao usuário o nome do agregado de dados desejado, e obtém o ID.
# Esse ID obtido permite o acesso ao documento com as variáveis disponíveis para aquele agregado.
# Ex1 a ser inserido: "Salários medianos, por categorias profissionais (série encerrada em setembro de 2013)"
# Ex2 a ser inserido: "Comercialização de agrotóxicos e afins, total e por área plantada, segundo a classe de uso"
nome=input('Insira o nome do agregado de dados desejado, para acessar a documentação necessária para o preenchimento da função de busca.')

agregados = requests.get('https://servicodados.ibge.gov.br/api/v3/agregados')
agregadosdata = json.loads(agregados.text)

for i in range(len(agregadosdata)):
    for j in range(len(agregadosdata[i]["agregados"])):
        if agregadosdata[i]["agregados"][j]["nome"] == str(nome):
            pesqid = (agregadosdata[i]["agregados"][j]["id"])
            break
        elif agregadosdata[i]["agregados"][j]["nome"] != str(nome) and j == (len(agregadosdata[i]["agregados"][j]) - 1):
            continue
        elif agregadosdata[i]["agregados"][j]["nome"] != str(nome) \
                and i == (len(agregadosdata)-1) \
                and j == (len(agregadosdata[i]["agregados"][j]) - 1):
            print("Não há esse agregado de dados na base disponível")

print("O ID da pesquisa é", pesqid)

# Página com vaariáveis a serem inseridas na consulta é aberta para o usuário.
# Tal formato pode ser menos ideal em comparação a um web scraping que permite a visualização dessas informações no próprio Python.
# Com isso, essa parte do código é provisória e será refinada.

urlcon='http://api.sidra.ibge.gov.br/desctabapi.aspx?c=' + str(pesqid)
webbrowser.open(urlcon, new=1, autoraise=True)

print('Com base nas informações desejadas observadas, insira as informações a seguir. Dados múltiplos devem ser inseridos'
      ' um a um, e encerrados com um "ok".')

####################################
# Para fazer hoje: construir sistema de input para o usuário que repassa variáveis já "tratadas" direto para a função
# do "conector", retornando para o usuário os dados requisitados. Esse tratamento diz respeito a, por exemplo, permitir
# que o usuário insira mais de uma localidade, variável, etc., uma de cada vez.
####################################

def conector(unt,p='last',v='allxp',t=None,c=None,cc=None,f=None,d=None,h=None):

    # unt -> nível territorial + unidade territorial. Pode assumir inúmeros valores, separados por barras.
    # (Ex: 'n1/1/n2/1').

    # p -> períodos desejados.
    # (Ex: '2008,2010-2012' – especifica os anos de 2008, e 2010 a 2012).

    # v -> especifica o código das variáveis desejadas, separadas por vírgulas.
    # (Ex: '643,1127')

    # t -> código do agregado de onde serão retirados os dados para as variáveis desejadas. Pode ser obtido pela API de agregados.
    # (Ex: '1327')

    # c -> classificação
    # cc -> categoria

    url='http://api.sidra.ibge.gov.br/values' + '/p/' + str(p) + '/' + str(unt) + '/v/' + str(v)

    if t != None:
        url = url + '/t/' + str(t)

    if c != None and cc != None:
        url = url + '/' + str(c) + '/' + str(cc)

    if f != None:
        url = url + '/f/' + str(f)

    if d != None:
        url = url + '/d/' + str(d)

    if h != None:
        url = url + '/h/' + str(h)

    print(url)

    data = requests.get(url)
    datares = json.loads(data.text)
    return datares

########

def treat(unt,p='last',v='allxp',t=None,c=None,cc=None,f=None,d=None,h=None):

    resp = conector(unt,p,v,t,c,cc,f,d,h)

    dflist = []

    for d in resp[1:]:
        s = pd.Series(d)
        dflist.append(s.to_frame().T)

    df = pd.concat(dflist)

    df.columns = df.columns.map(resp[0])

    # Linhas de código para tratamento de variáveis removidas até que eu compreenda se tal tratamento seria possível.

    pd.options.display.max_columns = 14

    ### Corrige o índice de entradas do DataFrame
    df.to_dict('records')
    df = df.reset_index(drop=True)
    print(df.dtypes)
    #print(df.head())
    #print(df.tail())

#####


### Testes:
#treat('n1/1','all','63,9798',6691,None,None,None,None,None)
#treat('n7/3301,'all',8,13,None,None,None,None,None)

#treat('n1/1','all','63,9798',6691,None,None,None,None,None) #Exemplo Brasil
#treat('n7/3301,2601','all',8,13,None,None,None,None,None) # Exemplo região metropolitana

#treat('n1/1','all',63,6691,None,None,None,None,None) #Exemplo mensal
#treat('n1/1','all',150,254,None,None,None,None,None) #Exemplo semestral
#treat('n1/1','2008,2010-2012','643,1127',1399,None,None,None,None,None) #Exemplo anual


