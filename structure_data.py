import os
import pandas as pd
import numpy as np
import requests
import random

link = "https://raw.githubusercontent.com/owid/monkeypox/main/owid-monkeypox-data.csv"

requisicao = requests.get(link)
data = pd.read_csv(requisicao.url)

# Remover colunas desnecessárias para a análise
colunas_excluidas = ["total_deaths","new_deaths","new_cases_smoothed",
                     "new_deaths_smoothed","new_cases_per_million","total_cases_per_million",
                     "new_cases_smoothed_per_million","new_deaths_per_million","total_deaths_per_million",
                     "new_deaths_smoothed_per_million"]

data = data.drop(colunas_excluidas, axis=1)

# Montando um dataframe com as datas

# definir a data inicial e final
# data_inicial = data.sort_values("date", ascending=True).head(1).date.values[0]
data_inicial = "2022-05-06"
data_final = data.sort_values("date", ascending=True).tail(1).date.values[0]
# Teste
# data_inicial = "2023-01-01"
# data_final = "2022-09-01"

# criar um DataFrame com datas entre a data inicial e final
dataframe_dias = pd.DataFrame({'date': pd.date_range(start=data_inicial, end=data_final)})
casos_acumulados = dataframe_dias.copy()
casos_novos = dataframe_dias.copy()

# Filtrando para os países que serão analisados no estudo
codigos_pais_para_analise = ["USA", "BRA", "GBR", "ESP", "COL", "FRA", 
                             "OWID_SAM", "OWID_EUR", "OWID_NAM", "OWID_ASI", "OWID_AFR"]
filtro_paises_para_analise = data["iso_code"].isin(codigos_pais_para_analise)
data_resultante = data[filtro_paises_para_analise]


valor_acumulado = 0
qtd_dias = len(dataframe_dias.date)

dados_usa = {"cum": [], "new": []}
dados_bra = {"cum": [], "new": []}
dados_gbr = {"cum": [], "new": []}
dados_esp = {"cum": [], "new": []}
dados_col = {"cum": [], "new": []}
dados_fra = {"cum": [], "new": []}

dados_africa = {"cum": [], "new": []}
dados_america_sul = {"cum": [], "new": []}
dados_america_norte = {"cum": [], "new": []}
dados_europa = {"cum": [], "new": []}
dados_asia = {"cum": [], "new": []}

for c in range(0, len(codigos_pais_para_analise)):
    valor_acumulado = 0
    dados_novos = []
    dados_acumulados = []
    codigo = codigos_pais_para_analise[c]
    
    for i in range(0, qtd_dias):
        data_completa = dataframe_dias.date[i]
        data_sem_horas = str(data_completa).split(" ")[0]
        filtroCompleto = (data_resultante["iso_code"] == codigo) & (data_resultante["date"] == data_sem_horas)
        
        valores_data = data_resultante[filtroCompleto]
        
        if valores_data.empty:
            dados_novos.append(0)
            dados_acumulados.append(valor_acumulado)
        else :
            dados_novos.append(int(valores_data.new_cases.values[0]))
            valor_acumulado = int(valores_data.total_cases.values[0])
            dados_acumulados.append(valor_acumulado)
            
    if(codigo == "USA"): 
        dados_usa["new"] = dados_novos
        dados_usa["cum"] = dados_acumulados
    if(codigo == "BRA"):
        dados_bra["new"] = dados_novos
        dados_bra["cum"] = dados_acumulados
    if(codigo == "GBR"):
        dados_gbr["new"] = dados_novos
        dados_gbr["cum"] = dados_acumulados
    if(codigo == "ESP"):
        dados_esp["new"] = dados_novos
        dados_esp["cum"] = dados_acumulados
    if(codigo == "COL"):
        dados_col["new"] = dados_novos
        dados_col["cum"] = dados_acumulados
    if(codigo == "FRA"):
        dados_fra["new"] = dados_novos
        dados_fra["cum"] = dados_acumulados
    
    if(codigo == "OWID_SAM"):
        dados_america_sul["new"] = dados_novos
        dados_america_sul["cum"] = dados_acumulados
    if(codigo == "OWID_EUR"):
        dados_europa["new"] = dados_novos
        dados_europa["cum"] = dados_acumulados
    if(codigo == "OWID_NAM"):
        dados_america_norte["new"] = dados_novos
        dados_america_norte["cum"] = dados_acumulados
    if(codigo == "OWID_ASI"):
        dados_asia["new"] = dados_novos
        dados_asia["cum"] = dados_acumulados
    if(codigo == "OWID_AFR"):
        dados_africa["new"] = dados_novos
        dados_africa["cum"] = dados_acumulados
        
casos_novos["United States"] = dados_usa["new"]
casos_novos["Brazil"] = dados_bra["new"]
casos_novos["United Kingdom"] = dados_gbr["new"]
casos_novos["Spain"] = dados_esp["new"]
casos_novos["Colombia"] = dados_col["new"]
casos_novos["France"] = dados_fra["new"]

casos_acumulados["United States"] = dados_usa["cum"]
casos_acumulados["Brazil"] = dados_bra["cum"]
casos_acumulados["United Kingdom"] = dados_gbr["cum"]
casos_acumulados["Spain"] = dados_esp["cum"]
casos_acumulados["Colombia"] = dados_col["cum"]
casos_acumulados["France"] = dados_fra["cum"]


casos_novos["Asia"] = dados_asia["new"]
casos_novos["Africa"] = dados_africa["new"]
casos_novos["Europa"] = dados_europa["new"]
casos_novos["America do Sul"] = dados_america_sul["new"]
casos_novos["America do Norte"] = dados_america_norte["new"]

casos_acumulados["Asia"] = dados_asia["cum"]
casos_acumulados["Africa"] = dados_africa["cum"]
casos_acumulados["Europa"] = dados_europa["cum"]
casos_acumulados["America do Sul"] = dados_america_sul["cum"]
casos_acumulados["America do Norte"] = dados_america_norte["cum"]
new = []
cum = []

valor = 0
aux = 0

for j in range(0, qtd_dias):
    new.append(aux)
    cum.append(valor)
    
    x = random.randint(0, 9)
    y = random.randint(500, 8000)
    
    aux = random.randint(x, y)
    valor += aux
    
    if (j % 10) == 0:
        aux = 3
        valor += aux
    
# casos_novos["Simulado"] = new
# casos_acumulados["Simulado"] = cum

casos_novos.to_csv("data/casos_novos_att.csv", index=False)
casos_acumulados.to_csv("data/casos_acumulados_att.csv", index=False)

print("CRIAÇÃO DOS ARQUIVOS NA PASTA DATA FINALIZADA!")

# x: 7, y: 4