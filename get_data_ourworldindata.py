import pandas as pd
import numpy as np
import requests
from pandas import ExcelWriter

def run_create_csv(path=""):
    print(path)
    path_world = "https://raw.githubusercontent.com/globaldothealth/monkeypox/main/latest.csv"
    link = requests.get(path_world)
    data = pd.read_csv(link.url)

    data.Date_confirmation = pd.to_datetime(data.Date_confirmation)

    #Filtros
    pox = data.query("Status == 'confirmed'", engine='python')

    # Criando tibble com todas as datas:
    all_dates = pox.Date_confirmation.dropna()
    date_df = pd.DataFrame(pd.date_range(start=all_dates.min(), end=all_dates.max(), freq="D"), columns=["Date_confirmation"])

    #Pegando todos os países
    countries = pox.Country.unique()
    
    list_new_cases = []
    list_accumulated_cases = []

    calculated_cases = cases_country_fun(countries[0], pox, date_df)

    list_new_cases.append(calculated_cases[0])
    list_accumulated_cases.append(calculated_cases[1])

    for i in range(1, len(countries)):
        calculated_cases = cases_country_fun(countries[i], pox, date_df)
        new_cases_df = calculated_cases[0].drop('date', axis=1)
        accumulated_cases_df = calculated_cases[1].drop('date', axis=1)
        list_new_cases.append(new_cases_df)
        list_accumulated_cases.append(accumulated_cases_df)
        
    new_cases = pd.concat(list_new_cases, axis=1)
    accumulated_cases = pd.concat(list_accumulated_cases, axis=1)

    path_new = 'data/pox_new_cases.csv'
    path_accumulated = 'data/pox_accumulated_cases.csv'
    
    if (path != ""):
        path_new = path + 'data/pox_new_cases.csv'
        path_accumulated = path + 'data/pox_accumulated_cases.csv'
        
    new_cases.to_csv(path_new, encoding='utf-8', index=False)
    accumulated_cases.to_csv(path_accumulated, encoding='utf-8', index=False)
    
def cases_country_fun(country, pox, date_df):
    
    query = "Date_confirmation.notna() & Country == '" + country + "'"
    
    country_pox_df = pox.query(query, engine="python").groupby(["Date_confirmation"]).count()
    country_pox_df["cases"] = country_pox_df["ID"]

    #Adicionando novos casos
    cases_country_df = pd.merge(date_df, country_pox_df, how="left", on=["Date_confirmation"])
    cases_country_df['cases'] = cases_country_df['cases'].fillna(0)
    
    #Adicionando casos acumulados
    cases_country_df["accumulated_cases"] =  cases_country_df["cases"].cumsum()
    
    cases = pd.DataFrame(data={}, columns=["date", country])
    accumulated_cases = pd.DataFrame(data={}, columns=["date", country])
    
    cases["date"] = cases_country_df["Date_confirmation"]
    cases[country] = cases_country_df["cases"].apply(np.int64)
    
    accumulated_cases["date"] = cases_country_df["Date_confirmation"]
    accumulated_cases[country] = cases_country_df["accumulated_cases"].apply(np.int64)
    
    return [cases, accumulated_cases]

def run_create_world_pop(path=""):
    run_create_population(path, 0)
    
def run_create_countrys_pop(path=""):
    run_create_population(path, 1)
    
def run_create_population(path, type):
    
    data_pop = pd.read_csv("data/world_population.csv")
    
    # Retirando a última coluna
    data_pop = data_pop.iloc[: , :-1]
    
    # Pegando o ano mais recente
    metadata = data_pop.columns
    years = metadata.drop(labels=["Country Name","Country Code","Indicator Name","Indicator Code"]).dropna().sort_values().to_series()
    last_year = years.tail(1).values[0]
    
    #
    population = data_pop[last_year].values
    countrys = data_pop["Country Name"].values
    
    df = pd.DataFrame([population], columns=countrys)
    df_world = df["World"].reset_index(drop=True)
    df_country = df.drop(columns=["World"]).reset_index(drop=True)
    
    path_pop = 'data'
    
    if (path != ""):
        path_pop = path + 'data'
        
    if (type == 0):        
        with ExcelWriter(path_pop + '/pop_world.xlsx') as writer:
                df_world.to_excel(writer, index=False)
                
    elif (type == 1):
        with ExcelWriter(path_pop + '/pop_world_country.xlsx') as writer:
                df_country.to_excel(writer, index=False)
    else:
        print("Não foi possível gerar um arquivo de população!")