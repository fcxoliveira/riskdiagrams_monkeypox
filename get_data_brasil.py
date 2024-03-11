from cmath import nan
import pandas as pd
import numpy as np
import requests

def handle_data_brazil(data: pd.DataFrame):
    
    state = data["Location"].str.strip()
    
    # Corrigindo erros nos nomes dos estados
    state = state.replace(to_replace=["Vinhedo, Sao Paulo"], value="Sao Paulo")
    state = state.replace(to_replace=["Porto Alegre, Rio Grande do Sul", "Rio Grandeo do Sul"], value="Rio Grande do Sul")
    state = state.replace(to_replace=["Matto Grosso"], value="Mato Grosso")
    state = state.replace(to_replace=["Tocatins"], value="Tocantins")
    
    # Adicionando acento a nomes de estados que o possuem
    state = state.replace(to_replace=["Ceara"], value="Ceará")
    state = state.replace(to_replace=["Parana"], value="Paraná")
    state = state.replace(to_replace=["Amapa"], value="Amapá")
    state = state.replace(to_replace=["Maranhao"], value="Maranhão")
    state = state.replace(to_replace=["Para"], value="Pará")
    state = state.replace(to_replace=["Paraiba"], value="Paraíba")
    state = state.replace(to_replace=["Piaui"], value="Piauí")
    state = state.replace(to_replace=["Rondonia"], value="Rondônia")
    state = state.replace(to_replace=["Sao Paulo"], value="São Paulo")
     
    data["state"] = state
    
    data["state"].fillna('NAO NOTIFICADO', inplace=True)
    
    return data

def get_cases_states(state, pox, date_df):
    
    query = ""
    
    if (state == "TOTAL"):
        query = "Date_confirmation.notna()"
    
    else:
        query = "Date_confirmation.notna() & state == '" + state + "'"
        
    country_pox_df = pox.query(query, engine="python").groupby(["Date_confirmation"]).count()
    
    country_pox_df["cases"] = country_pox_df["ID"]

    #Adicionando novos casos
    cases_country_df = pd.merge(date_df, country_pox_df, how="left", on=["Date_confirmation"])
    cases_country_df['cases'] = cases_country_df['cases'].fillna(0)
    
    #Adicionando casos acumulados
    cases_country_df["accumulated_cases"] =  cases_country_df["cases"].cumsum()
    
    cases = pd.DataFrame(data={}, columns=["date", state])
    accumulated_cases = pd.DataFrame(data={}, columns=["date", state])
    
    cases["date"] = cases_country_df["Date_confirmation"]
    cases[state] = cases_country_df["cases"].apply(np.int64)
    
    accumulated_cases["date"] = cases_country_df["Date_confirmation"]
    accumulated_cases[state] = cases_country_df["accumulated_cases"].apply(np.int64)
    
    return [cases, accumulated_cases]

def run_create_brazil_csv(path=""):

    path_world = "https://raw.githubusercontent.com/globaldothealth/monkeypox/main/latest.csv"
    link = requests.get(path_world)
    data = pd.read_csv(link.url)

    data.Date_confirmation = pd.to_datetime(data.Date_confirmation)

    #Filtros
    pox = data.query("Status == 'confirmed'", engine='python')
    # brazil_confirmed = data.where(data.Status == "confirmed")
    brazil_confirmed = data.query("Status == 'confirmed' & Country == 'Brazil'", engine='python')

    states_uf = ["AC", "AL", "AP", "AM", "BA", "CE",
                        "DF", "ES", "GO", "MA", "MT", "MS",
                        "MG", "PA", "PB", "PR", "PE", "PI", "RJ",
                        "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]


    state_names = np.array(["Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará",
                        "Distrito Federal", "Espirito Santo", "Goias", "Maranhão", "Mato Grosso", 
                        "Mato Grosso do Sul", "Minas Gerais", "Pará", "Paraíba", "Paraná", 
                        "Pernambuco", "Piauí", "Rio de Janeiro", "Rio Grande do Norte", 
                        "Rio Grande do Sul", "Rondônia", "Roraima", "Santa Catarina", 
                        "São Paulo", "Sergipe", "Tocantins", "NAO NOTIFICADO", "TOTAL"])

    brazil_confirmed = handle_data_brazil(brazil_confirmed)

    #Pegando todos os países
    states = brazil_confirmed["state"].unique()
    
    list_new_cases = []
    list_accumulated_cases = []
    
    # Criando tibble com todas as datas:
    all_dates = pox.Date_confirmation.dropna()
    date_df = pd.DataFrame(pd.date_range(start=all_dates.min(), end=all_dates.max(), freq="D"), columns=["Date_confirmation"])
    
    calculated_cases = get_cases_states(state_names[0], brazil_confirmed, date_df)

    list_new_cases.append(calculated_cases[0])
    list_accumulated_cases.append(calculated_cases[1])
    
    for i in range(1, len(state_names)):
        calculated_cases = get_cases_states(state_names[i], brazil_confirmed, date_df)
        new_cases_df = calculated_cases[0].drop('date', axis=1)
        accumulated_cases_df = calculated_cases[1].drop('date', axis=1)
        list_new_cases.append(new_cases_df)
        list_accumulated_cases.append(accumulated_cases_df)
        
    new_cases = pd.concat(list_new_cases, axis=1)
    accumulated_cases = pd.concat(list_accumulated_cases, axis=1)
    
    not_notified = accumulated_cases["NAO NOTIFICADO"].loc[len(accumulated_cases)-1]
    
    cases_not_notified = pd.DataFrame([not_notified], columns=['CASES'])
    
    new_cases = new_cases.drop(columns=["NAO NOTIFICADO"])
    accumulated_cases = accumulated_cases.drop(columns=["NAO NOTIFICADO"])
    
    path_new = 'data/brazil_new_cases.csv'
    path_accumulated = 'data/brazil_accumulated_cases.csv'
    path_not_notified = 'data/brazil_not_notified_cases.csv'
    
    if (path != ""):
        path_new = path + 'data/brazil_new_cases.csv'
        path_accumulated = path + 'data/brazil_accumulated_cases.csv'
        path_not_notified = path + 'data/brazil_not_notified_cases.csv'
        
    new_cases.to_csv(path_new, encoding='utf-8', index=False)
    accumulated_cases.to_csv(path_accumulated, encoding='utf-8', index=False)
    cases_not_notified.to_csv(path_not_notified, encoding='utf-8', index=False)
    
run_create_brazil_csv()