# import sys
from importlib.metadata import metadata
from math import ceil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from classes import *
from pandas import ExcelWriter
import colormap
import plotly.graph_objs as go
import base64
import os

max_x = 8
max_y = 4

def plotly_html(a_21_days, p_seven, datas, region_title, save_path, filename_bg):
    
    print("Etapa de plotar o gráfico")
    
    # dia = []
    # datas_selecionadas = ['22/07/2022', '27/09/2022']
    # for i in range(len(datas)-1):
    #     if(datas[i] in datas_selecionadas):
    #         dia.append(datas[i])
    #     else:
    #         dia.append('')

    for i in range(len(p_seven)):
        if p_seven[i] < 0.0:
            p_seven[i] = 0.0

    color_map = []
    for i in range(len(a_21_days)):
        if i < len(a_21_days) - 60:
            color_map.append('rgba(0, 0, 0, 0.1)')
        elif i == len(a_21_days) - 1:
            color_map.append('rgba(255, 255, 255, 0.6)')
        else:
            color_map.append('Blue')

    fig = go.Figure()
    
    # x = ceil(a_21_days.max())
    max_x = ceil(a_21_days.max())
    # y = ceil(p_seven.max())
    max_y = ceil(p_seven.max())
    
    #mode='lines+markers+text' - Para aparecer o text
    fig.add_trace(go.Scatter(x=a_21_days,
                             y=p_seven,                             
                             text=datas,
                             mode='lines+markers',
                             marker=dict(
                                 color=color_map,
                                 showscale=False,
                                 size=10,
                                 line=dict(
                                     color='Black',
                                     width=0.2)),
                             line=dict(
                                 color="Black",
                                 width=0.5,
                                 dash="dot"),
                             ))
    fig.add_shape(type="line",
                  x0=0,
                  y0=1,
                  x1=max_x,
                  y1=1,
                  line=dict(
                      color="Black",
                      width=1,
                      dash="dot",
                  ))

    image_filename = filename_bg
    img = base64.b64encode(open(image_filename, 'rb').read())    
    
    fig.add_layout_image(
        dict(
            source='data:image/png;base64,{}'.format(img.decode()),
            xref="x",
            yref="y",
            x=0,
            y=max_y,
            sizex=max_x,
            sizey=max_y,
            xanchor="left",
            yanchor="top",
            sizing="stretch",
            opacity=0.95,
            layer="below"))    
    
    # Barrinha
    fig.add_annotation(dict(font=dict(color='black', size=9),
                            xref="paper", yref="paper",
                            x=0.9, y=0.9,
                            text="EPG > 1.26: High", showarrow=False))

    fig.add_shape(type="rect",
                  xref="paper", yref="paper",
                  x0=0.9, x1=0.91, y0=0.87, y1=0.89, fillcolor="Red", line_color="Red")

    # fig.add_annotation(dict(font=dict(color='black', size=9),
    #                         xref="paper", yref="paper",
    #                         x=0.9, y=0.86,
    #                         text=" 70 < EPG < 100: Moderate-high", showarrow=False))

    fig.add_shape(type="rect",
                  xref="paper", yref="paper",
                  x0=0.9, x1=0.91, y0=0.86, y1=0.78, fillcolor="Yellow", line_color="Yellow")

    fig.add_annotation(dict(font=dict(color='black', size=9),
                            xref="paper", yref="paper",
                            x=0.9, y=0.84,
                            text=" 0.25 < EPG < 1.26 : Moderate", showarrow=False))

    fig.add_annotation(dict(font=dict(color='black', size=9),
                            xref="paper", yref="paper",
                            x=0.9, y=0.77,
                            text="EPG < 0.25: Low", showarrow=False))
    
    fig.add_annotation(dict(font=dict(color='blue', size=9),
                            xref="paper", yref="paper",
                            x=0.9, y=0.728,
                            text="Last 60 days", showarrow=False))
    
    fig.add_shape(type="rect",
                  xref="paper", yref="paper",
                  x0=0.9, x1=0.91, y0=0.77, y1=0.74, fillcolor="Green", line_color="Green")
    fig.add_shape(type="rect",
                  xref="paper", yref="paper",
                  x0=0.9, x1=0.91, y0=0.725, y1=0.70, fillcolor="Blue", line_color="Blue")

    fig.update_layout(plot_bgcolor='rgb(255,255,255)',
                      width=800,
                      height=600,
                      xaxis_showgrid=False,
                      yaxis_showgrid=False,
                      xaxis_title="Attack rate per 10⁵ inh. (last 21 days)",
                      yaxis_title="\u03C1 (mean of the last 7 days)",
                      title={
                          'text': region_title,
                          'y': 0.9,
                          'x': 0.5,
                          'xanchor': 'center',
                          'yanchor': 'top'},
                      )

    fig.update_xaxes(rangemode="tozero")

    fig.update_yaxes(rangemode="tozero")

    fig.show()
    
    os.remove(filename_bg)

    fig.write_html(filename_bg+'.html', include_plotlyjs="cdn")

def get_archive_name():
    
    cases_file = casesFile()
    
    try:
        cases_file.set_new('data/casos_novos_att.csv')
        cases_file.set_accumulated('data/casos_acumulados_att.csv')
        cases_file.set_population('data/pop_world_country.xlsx')
    except AttributeError:
        cases_file.error = True
        print('Error! Not found file or could not download!')
        
    return cases_file

def run_risk_diagrams(fator_risco):
    last_days_time = 30
    brasil = False
    pt = False
    html = True
    last_days = False
    animation = False
    argv_1 = "ourworldindata"
    
    #Parâmetros base
    propagation_rate = 9
    x_days_attack_rate = 21
    
    dataTable = []
    dataTable_EPG = []
    
    cases_File: casesFile = get_archive_name()
    
    if(cases_File.error == False):
        filename_new_cases = cases_File.new
        filename_accumulated_cases = cases_File.accumulated            
        
        data_new_cases = pd.read_csv(filename_new_cases)
        data_accumulated_cases = pd.read_csv(filename_accumulated_cases)
        dia = pd.to_datetime(data_new_cases['date']).dt.strftime('%d/%m/%Y').to_numpy()
        population = pd.read_excel(cases_File.population)
        countrys = data_accumulated_cases.columns.drop(labels=["date"]).sort_values().to_series()
        
        #Linha para conseguir testar
        countrys = population.columns
        countrys = ["Brazil", "United States","United Kingdom","Spain", "France", "Colombia"]
        countrys = ["United States"]        
        # countrys = ["Asia", "Africa", "Europa", "America do Sul", "America do Norte"]
        # countrys = ["Europa", "America do Sul"]
        
        for indice in range(len(countrys)):
            
            # Ínicio - Epidemiologia
            country = countrys[indice]
            new_cases_per_day = data_new_cases[country].to_numpy() #new_cases
            accumulated_cases_per_day = data_accumulated_cases[country].to_numpy() #cumulative_cases
            p = np.zeros((len(new_cases_per_day)), dtype=np.float)
            
            # Ínicio - Calculando velocidade de propagação da enfermidade          
            for i in range(propagation_rate + 2, len(new_cases_per_day)):
                denominador = 0
                aux = new_cases_per_day[i - (propagation_rate)] + new_cases_per_day[i - (propagation_rate + 1)] + new_cases_per_day[i - (propagation_rate + 2)]
                if aux == 0:
                    denominador = 1
                else:
                    denominador = aux
                p[i] = min((new_cases_per_day[i] + new_cases_per_day[i - 1] + new_cases_per_day[i - 2]) / denominador, 4)
            # Fim - Calculando velocidade de propagação da enfermidade 
            
            p_seven = np.zeros((len(new_cases_per_day)), dtype=np.float)
            n_21_days = np.zeros((len(new_cases_per_day)), dtype=np.float)
            a_21_days = np.zeros((len(new_cases_per_day)), dtype=np.float)
            risk = np.zeros((len(new_cases_per_day)), dtype=np.float)
            risk_per_10 = np.zeros((len(new_cases_per_day)), dtype=np.float)
            
            # Ínicio - Calculando Número de pessoas infecciosas
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
            # Fim - Calculando Número de pessoas infecciosas
            
            first_day = dia[x_days_attack_rate-1]
            last_day = dia[len(dia) - 1]
            first_day = first_day.replace('/', '-')
            last_day = last_day.replace('/', '-')
            
            save_path = 'static_graphic' + '/' + last_day + '-' + country
            save_path_temp = 'static_graphic' + '/interactive_graphic/' + last_day + '-' + country
            save_path_xlsx = 'static_graphic/xlsx/'
            # Fim - Epidemiologia
        

            #Criando gráfico - Início para projetos sem ser de epidemiologia
            # Ter aqui 3 arrays x(a_21_days), y(p_seven) e Data diária(dia)
            fig1, ax1 = plt.subplots(sharex=True)
            
            #Começar a plotar
            ax1.plot(a_21_days,  p_seven, 'ko--', fillstyle='none', linewidth=0.5)            
            
            # plt.show()
            lim_x = ax1.get_xlim()
            lim_y = ax1.get_ylim()
            
            x = np.ones(int(lim_x[1]))
            ax1.plot(x, 'k--', fillstyle='none', linewidth=0.5)
                
            if (lim_x[1] < 1): 
                lim_x = (lim_x[0], 1)
            
            if (lim_y[1] < 1): 
                lim_y = (lim_y[0], 1)
            
            max_x = ceil(a_21_days.max())
            max_y = ceil(p_seven.max())
            
            
            ax1.set_xlim(0, max_x)
            ax1.set_ylim(0, max_y)
            
            ax1.set_ylabel('$\u03C1$ (mean of the last 7 days)')
            ax1.set_xlabel('Attack rate per $10^5$ inh. (last 21 days)')
            
            plt.subplots_adjust(bottom=0.2)
            
            text_annotate = ("*The risk diagram was developed using the Our World in Data database. Last update: " + str(last_day) + ".")

            plt.text(0, -1, text_annotate, fontsize=7, wrap=False)
            
            # Original
            # rh = np.arange(0, int(lim[1]), 1)  
            
            rh = np.arange(0, max_x, 0.01)
            
            ar = np.linspace(0, max_y, 400)

            RH, AR = np.meshgrid(rh, ar)

            EPG = RH * AR           
            
            # Original
            # nivel_risco_alto = 100
            nivel_risco_alto = 1.26
            
            for i in range(len(EPG)):
                for j in range(len(EPG[i])):
                    if EPG[i][j] > nivel_risco_alto:
                        EPG[i][j] = nivel_risco_alto
                            
            c = colormap.Colormap()
            mycmap = c.cmap_linear('green(w3c)', 'yellow', 'red')
            
            #dia 18 a 22 de julho de 2022
            plt.title(country)
            
            plt.annotate(
                    ' EPG > 1,65: High', xy=(len(x) - abs(len(x) / 3.5), 3.8), color=(0, 0, 0),
                    ha='left', va='center', fontsize='6',
                    bbox=dict(fc=(0, 0, 0, 0), lw=0, pad=2))
            
            plt.annotate(
                " 0,5 < EPG < 1,65 : Moderate", xy=(len(x) - abs(len(x) / 3.5), 3.55), color=(0, 0, 0),
                ha='left', va='center', fontsize='6',
                bbox=dict(fc=(0, 0, 0, 0), lw=0, pad=2))
            
            plt.annotate(
                ' EPG < 0,5: Low', xy=(len(x) - abs(len(x) / 3.5), 3.3), color=(0, 0, 0),
                ha='left', va='center', fontsize='6',
                bbox=dict(fc=(0, 0, 0, 0), lw=0, pad=2))
            
            ax1.pcolorfast([0, max_x], [0, max_y], EPG, cmap=mycmap, alpha=0.6)          
            
            ax1.set_aspect('auto')

            if html:
                figt, axt = plt.subplots(sharex=True)
                
                axt.pcolorfast([0, max_x], [0, max_y], EPG, cmap=mycmap, alpha=0.6)
                axt.set_axis_off()
                figt.savefig(save_path_temp, format='png', bbox_inches='tight', dpi=300, pad_inches=0)
                
                plt.show()
                
                plotly_html(a_21_days, p_seven, dia, country, save_path_xlsx, save_path_temp)
            else:
                plt.savefig(save_path + '.png', bbox_inches='tight', dpi=300)
                plt.close('all')
                
            print("\n\nPrediction for the region of " + country + " performed successfully!\nPath:" + save_path)

    

            dataTable.append([country, accumulated_cases_per_day[len(accumulated_cases_per_day) - 1], new_cases_per_day[len(new_cases_per_day) - 1], p[len(p) - 1], p_seven[len(
                p_seven) - 1], n_21_days[len(n_21_days) - 1], a_21_days[len(a_21_days) - 1], risk[len(risk) - 1], risk_per_10[len(risk_per_10) - 1]])

            for i in range(len(dia)):
                dataTable_EPG.append([dia[i], country, risk_per_10[i]])

def executar_analise(x_days_attack_rate, propagation_rate, fator_risco, country, population, data_new_cases):
    new_cases_per_day = data_new_cases[country].to_numpy()
    
    p = np.zeros((len(new_cases_per_day)), dtype=np.float)
                
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
        
    continentes = [country] * (len(new_cases_per_day))
    fatores = [fator_risco] * (len(new_cases_per_day))
    
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
        
    return p_seven, a_21_days, risk_per_10, continentes, fatores

def gerar_analise():   
    
    fatores = np.arange(1, 10.1, 0.1)
    
    COLUNAS = ["continente", "fator_risco", "p7", "IA21", "EPG"]
    
    analise = pd.DataFrame(columns=COLUNAS)
    
    #Parâmetros base
    propagation_rate = 9
    x_days_attack_rate = 21
    
    cases_File: casesFile = get_archive_name()
    
    filename_new_cases = cases_File.new
    filename_accumulated_cases = cases_File.accumulated            
    
    data_new_cases = pd.read_csv(filename_new_cases)
    data_accumulated_cases = pd.read_csv(filename_accumulated_cases)
    dia = pd.to_datetime(data_new_cases['date']).dt.strftime('%d/%m/%Y').to_numpy()
    population = pd.read_excel(cases_File.population)
    
    countrys = ["Asia", "Africa", "Europa", "America do Sul", "America do Norte"]
    
    list_continente = []
    list_fator_risco = []
    list_p7 = []
    list_IA21 = []
    list_EPG = []
    
    for f in range(0, len(fatores)):
        fator_risco = fatores[f]
        
        for indice in range(len(countrys)):
            country = countrys[indice]            
            p_seven, a_21_days, risk_per_10, continentes, fatores_risco = executar_analise(x_days_attack_rate, propagation_rate, fator_risco, country, population, data_new_cases)
            
            list_p7.extend(p_seven)
            list_IA21.extend(a_21_days)
            list_EPG.extend(risk_per_10)
            
            list_continente.extend(continentes)
            list_fator_risco.extend(fatores_risco)
            
    analise["continente"] = list_continente
    analise["fator_risco"] = list_fator_risco
    analise["p7"] = list_p7
    analise["IA21"] = list_IA21
    analise["EPG"] = list_EPG
    
    analise.to_csv("data/analise.csv", index=False)