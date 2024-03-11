import os
import pandas as pd
import numpy as np
import requests

link = "https://raw.githubusercontent.com/owid/monkeypox/main/owid-monkeypox-data.csv"

requisicao = requests.get(link)
data = pd.read_csv(requisicao.url)
    
diretorio = "/home/filipe/projetos/riskdiagrams_monkeypox/data"

dados_diretorio = diretorio + "/days"

_, _, files = next(os.walk(dados_diretorio))

files.sort()

qtd_arquivos = len(files)

datas_catalogadas = []

for indice in range(0, qtd_arquivos - 1):
    datas_catalogadas.append(files[indice].split(".")[0])
    
primeiro_arquivo_data = files[0]

ultimo_arquivo_data = files[qtd_arquivos-1]

colunas_excluidas = ["DisplayOrder", "WHO_REGION", "WHO_REGION_SHORTNAME", "DeathsAll",
"DeathsLast24Hours", "DeathsLast7Days", "Latitude", "Longitude", "MPX_DataAvailable", "LASTREPDATE"]

# PROCURAR OS 10 PAÍSES COM MAIS CASOS
data_ultimo_dia = pd.read_csv(dados_diretorio + "/" + ultimo_arquivo_data)

# TIPO 1
dados_total = data_ultimo_dia.query("DisplayOrder == 1", engine='python')

# TIPO 2
dados_por_regiao = data_ultimo_dia.query("DisplayOrder == 2", engine='python')

# TIPO 3
dados_por_pais = data_ultimo_dia.query("DisplayOrder == 3", engine='python')
cases = dados_por_pais.sort_values("CasesAll", ascending=False).drop(colunas_excluidas, axis=1)
top_seis_maiores_casos = cases.head(6)
# print(top_seis_maiores_casos)

# Após análise foram escolhidos para a análise de risco os países abaixo
paises_para_analise = top_seis_maiores_casos.COUNTRY

# Montando um dataframe com as datas

# definir a data inicial e final
data_inicial = primeiro_arquivo_data.split(".")[0]
data_final = ultimo_arquivo_data.split(".")[0]

# criar um DataFrame com datas entre a data inicial e final
dataframe_dias = pd.DataFrame({'Data': pd.date_range(start=data_inicial, end=data_final)})

qtd_dias = len(dataframe_dias.Data)

casos_eua = {"acumulados": [], "novos": []}
casos_brasil = {"acumulados": [], "novos": []}
casos_uk = {"acumulados": [], "novos": []}
casos_espanha = {"acumulados": [], "novos": []}
casos_colombia = {"acumulados": [], "novos": []}
casos_franca = {"acumulados": [], "novos": []}

casos_acumulados_eua = 0
casos_acumulados_brasil = 0
casos_acumulados_uk = 0
casos_acumulados_espanha = 0
casos_acumulados_colombia = 0
casos_acumulados_franca = 0

casos_acumulados = dataframe_dias.copy()
casos_novos = dataframe_dias.copy()

for i in range(0, qtd_dias):    
    data_completa = dataframe_dias.Data[i]
    data_sem_horas = str(data_completa).split(" ")[0]
    
    if data_sem_horas in datas_catalogadas:
        
        aux_df = pd.read_csv(dados_diretorio + "/" + data_sem_horas + '.csv')
        
        aux_df = aux_df.query("DisplayOrder == 3")
        
        # Casos novos
        if (i == 0):
            casos_eua["novos"].append(aux_df[aux_df["ISO3"] == "USA"].CasesAll.values[0])
            casos_brasil["novos"].append(aux_df[aux_df["ISO3"] == "BRA"].CasesAll.values[0])
            casos_uk["novos"].append(aux_df[aux_df["ISO3"] == "GBR"].CasesAll.values[0])
            casos_espanha["novos"].append(aux_df[aux_df["ISO3"] == "ESP"].CasesAll.values[0])
            casos_colombia["novos"].append(aux_df[aux_df["ISO3"] == "COL"].CasesAll.values[0])
            casos_franca["novos"].append(aux_df[aux_df["ISO3"] == "FRA"].CasesAll.values[0])
            
        else:
            casos_eua["novos"].append(aux_df[aux_df["ISO3"] == "USA"].CasesAll.values[0] - casos_acumulados_eua)
            casos_brasil["novos"].append(aux_df[aux_df["ISO3"] == "BRA"].CasesAll.values[0] - casos_acumulados_brasil)
            casos_uk["novos"].append(aux_df[aux_df["ISO3"] == "GBR"].CasesAll.values[0] - casos_acumulados_uk)
            casos_espanha["novos"].append(aux_df[aux_df["ISO3"] == "ESP"].CasesAll.values[0] - casos_acumulados_espanha)
            casos_colombia["novos"].append(aux_df[aux_df["ISO3"] == "COL"].CasesAll.values[0] -casos_acumulados_colombia)
            casos_franca["novos"].append(aux_df[aux_df["ISO3"] == "FRA"].CasesAll.values[0] - casos_acumulados_franca)
            
        
        casos_acumulados_eua = aux_df[aux_df["ISO3"] == "USA"].CasesAll.values[0]
        casos_acumulados_brasil = aux_df[aux_df["ISO3"] == "BRA"].CasesAll.values[0]
        casos_acumulados_uk = aux_df[aux_df["ISO3"] == "GBR"].CasesAll.values[0]
        casos_acumulados_espanha = aux_df[aux_df["ISO3"] == "ESP"].CasesAll.values[0]
        casos_acumulados_colombia = aux_df[aux_df["ISO3"] == "COL"].CasesAll.values[0]
        casos_acumulados_franca = aux_df[aux_df["ISO3"] == "FRA"].CasesAll.values[0] 
        
        # Casos acumulados      
        casos_eua["acumulados"].append(casos_acumulados_eua)
        casos_brasil["acumulados"].append(casos_acumulados_brasil)
        casos_uk["acumulados"].append(casos_acumulados_uk)
        casos_espanha["acumulados"].append(casos_acumulados_espanha)
        casos_colombia["acumulados"].append(casos_acumulados_colombia)
        casos_franca["acumulados"].append(casos_acumulados_franca)
        
    else:
        # Casos novos
        casos_eua["novos"].append(0)
        casos_brasil["novos"].append(0)
        casos_uk["novos"].append(0)
        casos_espanha["novos"].append(0)
        casos_colombia["novos"].append(0)
        casos_franca["novos"].append(0)
        
        # Casos acumulados
        casos_eua["acumulados"].append(casos_acumulados_eua)
        casos_brasil["acumulados"].append(casos_acumulados_brasil)
        casos_uk["acumulados"].append(casos_acumulados_uk)
        casos_espanha["acumulados"].append(casos_acumulados_espanha)
        casos_colombia["acumulados"].append(casos_acumulados_colombia)
        casos_franca["acumulados"].append(casos_acumulados_franca)

casos_novos["United States"] = casos_eua["novos"]
casos_novos["Brazil"] = casos_brasil["novos"]
casos_novos["United Kingdom"] = casos_uk["novos"]
casos_novos["Spain"] = casos_espanha["novos"]
casos_novos["Colombia"] = casos_colombia["novos"]
casos_novos["France"] = casos_franca["novos"]

casos_acumulados["United States"] = casos_eua["acumulados"]
casos_acumulados["Brazil"] = casos_brasil["acumulados"]
casos_acumulados["United Kingdom"] = casos_uk["acumulados"]
casos_acumulados["Spain"] = casos_espanha["acumulados"]
casos_acumulados["Colombia"] = casos_colombia["acumulados"]
casos_acumulados["France"] = casos_franca["acumulados"]

casos_novos.to_csv("casos_novos_att.csv", index=False)
casos_acumulados.to_csv("casos_acumulados_att.csv", index=False)