from importlib.metadata import metadata
from math import ceil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from classes import *
from risk_diagrams import get_archive_name
from pandas import ExcelWriter
import colormap
import plotly.graph_objs as go
import base64
import os
from datetime import date

today = date.today()

# dd/mm/YY
today_str = today.strftime("%Y-%m-%d")

fator_risco = 1
last_days_time = 30
brasil = False
pt = False
html = True
last_days = False
animation = False
argv_1 = "ourworldindata"

fatores = np.arange(1, 10.1, 0.1)
    
COLUNAS = ["continente", "data", "data_inteiro", "p7", "IA21", "EPG"]

COLUNAS_ANALISE_MEDIA = ["continente", "mes", "p7", "IA21", "EPG"]

analise = pd.DataFrame(columns=COLUNAS)

analise_por_mes = pd.DataFrame(columns=COLUNAS_ANALISE_MEDIA)

list_continente = []
list_fator_risco = []
list_p7 = []
list_IA21 = []
list_EPG = []
list_date = []
list_data_inteiro = []

#Parâmetros base
propagation_rate = 9
x_days_attack_rate = 21

dataTable = []
dataTable_EPG = []

cases_File: casesFile = get_archive_name()

error = cases_File.error

# error = False

if(error == False):
    filename_new_cases = cases_File.new
    filename_accumulated_cases = cases_File.accumulated            
    
    data_new_cases = pd.read_csv(filename_new_cases)
    data_accumulated_cases = pd.read_csv(filename_accumulated_cases)
    
    data_new_cases = data_new_cases.where(data_new_cases["date"] < '2022-10-01').dropna()
    data_accumulated_cases = data_accumulated_cases.where(data_accumulated_cases["date"] < '2022-10-01').dropna()
    
    data_save = data_accumulated_cases.copy()
    
    dia = pd.to_datetime(data_new_cases['date']).dt.strftime('%d/%m/%Y').dropna().to_numpy()
    periodo = pd.to_datetime(data_new_cases['date']).dt.strftime('%Y%m%d').dropna().to_numpy()
    population = pd.read_excel(cases_File.population)
    countrys = data_accumulated_cases.columns.drop(labels=["date"]).sort_values().to_series()
    
    #Linha para conseguir testar
    countrys = population.columns
    countrys = ["Asia", "Africa", "Europa", "America do Sul", "America do Norte"]
    
    dia_test = dia[20:]
    
    periodo_formatado = periodo[20:].astype(int)
    
    for indice in range(len(countrys)):
        country = countrys[indice]
        
        teste = data_save[country]
        new_cases_per_day = data_new_cases[country].to_numpy() #new_cases
        accumulated_cases_per_day = data_accumulated_cases[country].to_numpy() #cumulative_cases
        p = np.zeros((len(new_cases_per_day)), dtype=np.float)
        
        continente = [country] * (len(new_cases_per_day))
        
        continente = continente[20:]
                    
        for i in range(propagation_rate + 2, len(new_cases_per_day)):
            denominador = 0
            aux = new_cases_per_day[i - (propagation_rate)] + new_cases_per_day[i - (propagation_rate + 1)] + new_cases_per_day[i - (propagation_rate + 2)]
            if aux == 0:
                denominador = 1
            else:
                denominador = aux
            p[i] = min((new_cases_per_day[i] + new_cases_per_day[i - 1] + new_cases_per_day[i - 2]) / denominador, 4)

        p_seven = np.zeros((len(new_cases_per_day)), dtype=np.float)
        n_21_days = np.zeros((len(new_cases_per_day)), dtype=np.float)
        a_21_days = np.zeros((len(new_cases_per_day)), dtype=np.float)
        risk = np.zeros((len(new_cases_per_day)), dtype=np.float)
        risk_per_10 = np.zeros((len(new_cases_per_day)), dtype=np.float)
        
        for i in range(x_days_attack_rate-1, len(new_cases_per_day)):
            p_seven[i] = np.average(p[i - 6:i + 1])
            n_21_days[i] = np.sum(new_cases_per_day[i - x_days_attack_rate-1: i + 1])
            pop = population[country]
            population_multiplier = 100000
            a_21_days[i] = n_21_days[i] / pop * population_multiplier
            
            p_seven[i] = p_seven[i] * fator_risco
            a_21_days[i] = a_21_days[i] * fator_risco
            
            risk[i] = n_21_days[i] * p_seven[i]
            risk_per_10[i] = a_21_days[i] * p_seven[i]
            
            list_p7.append(p_seven[i])
            list_IA21.append(a_21_days[i])
            list_EPG.append(risk_per_10[i])
        
        list_continente.extend(continente)    
            
        list_date.extend(dia_test)
        
        list_data_inteiro.extend(periodo_formatado)
        
    
    analise["continente"] = list_continente
    analise["p7"] = list_p7
    analise["IA21"] = list_IA21
    analise["EPG"] = list_EPG
    analise["data"] = list_date
    analise["data_inteiro"] = list_data_inteiro
    
    dic_analysis = {"Asia": {}, "Africa": {}, "Europa": {}, "America do Sul": {}, "America do Norte": {}}
    
    l_continente =[]
    l_mes =[]
    l_p7 =[]
    l_IA21 =[]
    l_EPG =[]
    
    for c in countrys:
        p = analise[analise["continente"] == c]
        
        p7_jul = p.query('data_inteiro < 20220801 & data_inteiro >= 20220701').p7.mean()
        p7_ago = p.query('data_inteiro < 20220901 & data_inteiro >= 20220801').p7.mean()
        p7_set = p.query('data_inteiro < 20221001 & data_inteiro >= 20220901').p7.mean()
        
        IA21_jul = p.query('data_inteiro < 20220801 & data_inteiro >= 20220701').IA21.mean()
        IA21_ago = p.query('data_inteiro < 20220901 & data_inteiro >= 20220801').IA21.mean()
        IA21_set = p.query('data_inteiro < 20221001 & data_inteiro >= 20220901').IA21.mean()
        
        epg_jul = p.query('data_inteiro < 20220801 & data_inteiro >= 20220701').EPG.mean()
        epg_ago = p.query('data_inteiro < 20220901 & data_inteiro >= 20220801').EPG.mean()
        epg_set = p.query('data_inteiro < 20221001 & data_inteiro >= 20220901').EPG.mean()
        
        l_continente.extend([c]*3)
        l_mes.extend(['jul', 'ago', 'set'])
        l_p7.extend([p7_jul, p7_ago, p7_set])
        l_IA21.extend([IA21_jul, IA21_ago, IA21_set])
        l_EPG.extend([epg_jul, epg_ago, epg_set])
    
    analise.to_csv("data/analise" + today_str + ".csv", index=False)
    
    analise_por_mes["continente"] = l_continente
    analise_por_mes["p7"] = l_p7
    analise_por_mes["IA21"] = l_IA21
    analise_por_mes["EPG"] = l_EPG
    analise_por_mes["mes"] = l_mes
    
    analise_por_mes.to_csv("data/analise-por-mes" + today_str + ".csv", index=False)