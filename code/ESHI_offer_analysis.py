#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  8 21:18:20 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
project_folder = "/Users/caseymcquillan/Desktop/Research/ACA and Young Workers"
code_folder = project_folder+"code"
data_folder = project_folder+"data"
output_folder = project_folder+"output"
os.chdir(code_folder)


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00025.csv')


#%% Data Wrangling #%%

# Adjust year bc survey data corresponds to prev year
df[df['YEAR'] >= 2019]
df['YEAR'] = df['YEAR'] - 1

# Define Health Insurance
df['HI'] = 1*(df['ANYCOVLY']==2)
df['Public HI'] =   1*(df['PUBCOVLY']==2)
df['Public HI (Medicaid)'] =   1*(df['HIMCAIDLY']==2)
df['Public HI (Medicare)'] =   1*(df['HIMCARELY']==2)
df['Private HI'] =   1*(df['PRVTCOVLY']==2)
df['ESHI'] =   1*(df['GRPCOVLY']==2)
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['Other Private'] = df['Private HI'] - df['ESHI']
df['HI Other'] = df['HI'] - df['ESHI']
df['No HI'] = 1 - df['HI']


## Define Full-Time, Full-Year
hours_requirement_FTFY =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirement_FTFY =  1*(df['WKSWORK2'] >= 4)
df['FTFY'] = hours_requirement_FTFY * weeks_requirement_FTFY

## Define Part-Time, Part-Year
hours_requirement_PTPY =  1*(df['UHRSWORKLY'] > 0)
weeks_requirement_PTPY =  1*(df['WKSWORK2'] > 0)
df['PTPY'] = hours_requirement_PTPY * weeks_requirement_PTPY
df['PTPY'] = df['PTPY']-df['FTFY']

df['ESHI_eligible'] = df['ESHI_own'] + (1-df['ESHI_own'])*(df['HIELIG']==2)

#%% Reasons for being ineligible #%%
variables = ["Share without access to ESHI:",
            "Share eligible for ESHI:",
            "Share not eligible for ESHI:",
            "Did not work enough hours",
            "Contract/temporary employee",
            "Tenure requirement not met",
            "Pre-existing condition",
            "Too expensive",
            "Other"]

groups = ['All', 'FTFY', 'PTPY']

group2weight_Dict ={'All':1,
                    'FTFY':df['FTFY'],
                    'PTPY':df['PTPY']}

num2ineligble_Dict={1:"Did not work enough hours",
                    2:"Contract/temporary employee",
                    3:"Tenure requirement not met",
                    4:"Pre-existing condition",
                    5:"Too expensive",
                    6:"Other"}

table_data = pd.DataFrame(index= variables, columns=groups)
for group in groups:
    group_weight =group2weight_Dict[group]
    
    #Calculate shares    
    table_data.loc["Share without access to ESHI:", group] =\
                    np.average((df['HIELIG']==99)-df['ESHI_own'], 
                               weights=1*(df['ASECWTH']*group_weight))

    table_data.loc["Share reporting eligible for ESHI:", group] =\
                    np.average(df['ESHI_eligible'] , 
                               weights=1*(df['ASECWTH']*group_weight))
        
    table_data.loc["Share not eligible for ESHI:", group] =\
                    np.average(df['HIELIG']==1, 
                               weights=1*(df['ASECWTH']*group_weight))
                    
    #Calculate reason for ineligible
    for i in range(1,7):
        var = f'HINELIG{i}'
        row = num2ineligble_Dict[i]
        table_data.loc[row, group] = \
                        np.average(df[var]==2, 
                                   weights=1*(df['HIELIG']==1)*df['ASECWTH']*group_weight)

print(table_data.to_latex())


#%%  Reasons for not taking up ESHI #%%

groups = ['All', 'FTFY', 'PTPY']

group2weight_Dict ={'All':1,
                    'FTFY':df['FTFY'],
                    'PTPY':df['PTPY']}

num2ineligble_Dict={1:"Covered by another plan",
                    2:"Traded for higher pay",
                    3:"Too expensive",
                    4:"Do not need health insurance",
                    5:"Pre-existing condition",
                    6:"Tenure requirement not met",
                    7:"Contract/emporary employee",
                    8:"Other:"}

variables = num2ineligble_Dict.values()

table_data = pd.DataFrame(index= variables, columns=groups)
for group in groups:
    group_weight =group2weight_Dict[group]
                        
    #Calculate reason for ineligible
    for i in range(1,9):
        var = f'HINTAKE{i}'
        row = num2ineligble_Dict[i]
        table_data.loc[row, group] = \
                        np.average(df[var]==2, 
                                   weights=1*(df['HIELIG']==2)*df['ASECWTH']*group_weight)


    table_data.loc["Covered as an ESHI Dependent", group] = \
                                np.average((df['HINTAKE1']==2)*df['ESHI_dependent'], 
                                   weights=1*(df['HIELIG']==2)*df['ASECWTH']*group_weight)
print(table_data.to_latex())
                      
                        
#%%  If covered another way, then how? #%%                       

np.average(df['HI'], 
           weights=1*(df['HINTAKE1']==2)*df['ASECWTH'])

np.average(df['ESHI_own'], 
           weights=1*(df['HINTAKE1']==2)*df['ASECWTH'])

np.average(df['ESHI_dependent'], 
           weights=1*(df['HINTAKE1']==2)*df['ASECWTH'])

np.average(df['Other Private'], 
           weights=1*(df['HINTAKE1']==2)*df['ASECWTH'])

np.average(df['Public HI (Medicaid)'], 
           weights=1*(df['HINTAKE1']==2)*df['ASECWTH'])

np.average(df['Public HI (Medicare)'], 
           weights=1*(df['HINTAKE1']==2)*df['ASECWTH'])