from cmath import nan
import pandas as pd
import numpy as np
import requests

df = pd.read_csv("data/date_cases.csv")
df["file"] = df["file"].astype(str)
df[['day', 'type']] = df["file"].apply(lambda x: pd.Series(str(x).split(".")))


files = df["file"].to_list()
days = df["day"].to_list()

casesAll = []
casesLast24Hours = []



for i in range(len(files)):
    days_df = pd.read_csv("data/days/" + files[i])
    brazil_days_df = days_df[days_df["ISO3"] == "BRA"]
    casesAll.append(brazil_days_df['CasesAll'].item())
    casesLast24Hours.append(brazil_days_df['CasesLast24Hours'].item())
    
    
print(casesAll)
# print(casesLast24Hours)
# print(casesLast7Days)
# new_df = brazil_days_df[['CasesAll','CasesLast24Hours', 'CasesLast7Days']].copy()

final_file = pd.DataFrame([], columns=['Day', 'CasesAll', 'CasesLast24Hours'])
final_file['Day'] = days
final_file["CasesAll"] = casesAll
final_file["CasesLast24Hours"] = casesLast24Hours
# final_file["CasesLast7Days"] = casesLast7Days

final_file.reset_index()
print(final_file)