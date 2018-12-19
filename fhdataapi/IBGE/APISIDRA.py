import requests
import json
import pandas as pd

# https://servicodados.ibge.gov.br/api/v3/agregados    ####   dados agregados
# http://api.sidra.ibge.gov.br/    ####   consulta SIDRA
# http://api.sidra.ibge.gov.br/home/ajuda    ###   documentação API SIDRA

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

    ### Especifica o tipo da variável associada à coluna "Mês (Código)"
    ### SÓ FUNCIONA PARA DADOS MENSAIS. COMO LIDAR?
    df['Mês (Código)'] = df['Mês (Código)'].apply(lambda x: pd.to_datetime(x, format='%Y%m'))

    ### Especifica o tipo da variável associada à coluna "Valor"
    df['Valor'] = df['Valor'].apply(lambda x: pd.to_numeric(x, errors='coerce'))

    ### Especifica o tipo da variável associada à coluna "Variável (Código)"
    df['Variável (Código)'] = df['Variável (Código)'].apply(lambda x: pd.to_numeric(x, errors='coerce'))

    ### Especifica o tipo da variável associada à coluna "Unidade de Medida (Código)"
    df['Unidade de Medida (Código)'] = df['Unidade de Medida (Código)'].apply(lambda x: pd.to_numeric(x, errors='coerce'))

    ### Especificaria o tipo da variável associada à coluna de código de nível territorial (p.e., "Região Metropolitana (Código)")
    # Funcionamento seria provisório, pois coluna altera de nome.
    # Como resolver fato de que nome dessa coluna se altera?
    # Mesmo problema se aplica ao ano/mês, por exemplo. Ou fato de que novas colunas surgem com diferentes variáveis,

    pd.options.display.max_columns = 14

    ### Corrige o índice de entradas do DataFrame
    df.to_dict('records')
    df = df.reset_index(drop=True)
    print(df.dtypes)
    print(df.head())
    #print(df.tail())

#####

### Testes:
#treat('n1/1','all','63,9798',6691,None,None,None,None,None)
#treat('n7/3301,'all',8,13,None,None,None,None,None)

#treat('n1/1','all','63,9798',6691,None,None,None,None,None) #Exemplo Brasil
treat('n7/3301,2601','all',8,13,None,None,None,None,None) # Exemplo região metropolitana

#treat('n1/1','all',63,6691,None,None,None,None,None) #Exemplo mensal
#treat('n1/1','all',150,254,None,None,None,None,None) #Exemplo semestral
#treat('n1/1','2008,2010-2012','643,1127',1399,None,None,None,None,None) #Exemplo anual
