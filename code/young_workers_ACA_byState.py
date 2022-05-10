#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  2 21:01:18 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np
import statsmodels.api as sm

# Graph packages
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

### Set working directory and folders
project_folder = "/Users/caseymcquillan/Desktop/Research/ACA and Young Workers"
code_folder = project_folder+"code"
data_folder = project_folder+"data"
output_folder = project_folder+"output"
os.chdir(code_folder)


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00022.csv')

## Dataset Variables
variables = ['YEAR', 'SERIAL', 'MONTH', 'CPSID', 'ASECFLAG', 'HFLAG', 'ASECWTH',
           'STATEFIP', 'PERNUM', 'CPSIDP', 'ASECWT', 'AGE', 'SEX', 'RACE', 'MARST',
           'EDUC', 'SCHLCOLL', 'CLASSWLY', 'WORKLY', 'WKSWORK1', 'WKSWORK2',
           'UHRSWORKLY', 'FULLPART', 'FIRMSIZE', 'WHYPTLY', 'WHYNWLY', 'INCWAGE',
           'INCLUGH', 'PAIDGH', 'EMCONTRB', 'HIMCAIDLY', 'HIMCARELY', 'COVERGH',
           'COVERPI', 'CAIDLY', 'CARELY', 'VERIFY', 'ANYCOVLY', 'ANYCOVNW',
           'GRPDEPLY', 'GRPOWNLY', 'GRPOUTLY', 'GRPTYPLY', 'OUT', 'DATE']

#Create time period variable
df['DATE'] = pd.to_datetime(df[['YEAR', 'MONTH']].assign(DAY=1))
df['DATE'] = df["DATE"].dt.strftime('%Y-%m')

#Differentiate variables in reference to this year or last
df['AGENW'] = df['AGE'] 
df['AGELY'] = (df['AGE']-1)
ages = range(18,33)

df['YEARNW'] = df['YEAR']
df['YEARLY'] = (df['YEAR']-1)
years = range(2000,2021)


# Keep the single adults 
df = df[df['MARST']==6]

# Define working
hours_requirement =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirement =  1*(df['WKSWORK2'] >= 4)
df['FTFY'] = hours_requirement * weeks_requirement

# Define relevant health insurance variables
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['Public HI'] = 1*(df['HIMCAIDLY']==2) \
    + (1-1*(df['HIMCAIDLY']==2))*(df['HIMCARELY']==2)
df['No HI'] = 1*(df['VERIFY']==1) \
    + (1-1*(df['VERIFY']==1))*(df['ANYCOVNW']==2)

# Define Relevant working variables
df['SELFEMP'] = 1*(df['CLASSWLY']==13) + 1*(df['CLASSWLY']==14) 

### Define bounded states
bounded_states = ['OR', 'CA', 'MI', 'NV', 'AZ', 'AK', 'KS', 'OK',
                  'AR', 'MS', 'AL', 'SC', 'NC', 'VT', 'HI', 'DC', 'WY']
# State FIPS Dictionary
state_codes_dict = {
        'AK': 2, 'AL': 1, 'AR': 5, 'AZ': 4, 'CA': 6,
        'CO': 8, 'CT': 9, 'DC': 11, 'DE': 10, 'FL': 12,
        'GA': 13, 'HI': 15, 'IA': 19, 'ID': 16, 'IL': 17,
        'IN': 18, 'KS': 20, 'KY': 21, 'LA': 22, 'MA': 25,
        'MD': 24, 'ME': 23, 'MI': 26, 'MN': 27, 'MO': 29,
        'MS': 28, 'MT': 30, 'NC': 37, 'ND': 38, 'NE': 31,
        'NH': 33, 'NJ': 34, 'NM': 35, 'NV': 32, 'NY': 36,
        'OH': 39, 'OK': 40, 'OR': 41, 'PA': 42, 'RI': 44,
        'SC': 45, 'SD': 46, 'TN': 47, 'TX': 48, 'UT': 49,
        'VA': 51, 'VT': 50, 'WA': 53, 'WI': 55, 'WV': 54, 'WY': 56}
inv_state_codes_dict = {v: k for k, v in state_codes_dict.items()}

# Define binding in df
df['binding']= [int(inv_state_codes_dict[state_fip] in bounded_states) for state_fip in df['STATEFIP']]  

# Create dataframe based on binding  
df_binding = df[df['binding']==1]
df_control = df[df['binding']==0]

#Reset index
df.reset_index(inplace=True)
df_binding.reset_index(inplace=True)
df_control.reset_index(inplace=True)


## Define Age Groups:
age_groups=[[18,19,20,21],[22,23,24,25], [26,27,28,29], [30, 31,32]]
age_group2name_Dict = {22:"Ages 22-25",
                       26:"Ages 26-29",
                       18:"Ages 18-21",
                       30:"Ages 30-32"}
age_group2color_Dict = {"Ages 22-25":"maroon",
                       "Ages 26-29":'navy',
                       "Ages 18-21":'lightcoral',
                       "Ages 30-32":'lightsteelblue'}


#%% Result 1: Change in Share Reporting ESHI Dependent  (binding) #%%
os.chdir(output_folder)

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df_binding[[x in age_group for x in df_binding['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:        
        results.loc[group_name, year] = \
            100*np.average(df_age_group['GRPDEPLY']==2, \
                           weights=df_age_group['YEARLY']==year)
for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Dependent on ESHI')
plt.legend()
plt.tight_layout()
plt.savefig('binding_Effect_HI_byAgeGroup_ESHI_Dependent.png', dpi=500)
plt.clf()

##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years)
for age in ages:
    df_age = df_binding[df_binding['AGELY']==age]
    for year in years:        
        results.loc[age, year] = \
            100*np.average(df_age['GRPDEPLY']==2, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Dependent on ESHI')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('binding_Effect_HI_byAge_ESHI_Dependent.png', bbox_inches="tight", dpi=500)
plt.clf() 


#%% Result 1: Change in Share Reporting ESHI Dependent  (control) #%%
os.chdir(output_folder)

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df_control[[x in age_group for x in df_control['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:        
        results.loc[group_name, year] = \
            100*np.average(df_age_group['GRPDEPLY']==2, \
                           weights=df_age_group['YEARLY']==year)
for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Dependent on ESHI')
plt.legend()
plt.tight_layout()
plt.savefig('control_Effect_HI_byAgeGroup_ESHI_Dependent.png', dpi=500)
plt.clf()

##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years)
for age in ages:
    df_age = df_control[df_control['AGELY']==age]
    for year in years:        
        results.loc[age, year] = \
            100*np.average(df_age['GRPDEPLY']==2, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Dependent on ESHI')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('control_Effect_HI_byAge_ESHI_Dependent.png', bbox_inches="tight", dpi=500)
plt.clf() 