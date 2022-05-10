#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 10:35:04 2022

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

## Define Part-Time, Part-Year
hours_requirement_PTPY =  1*(df['UHRSWORKLY'] > 0)
weeks_requirement_PTPY =  1*(df['WKSWORK2'] > 0)
df['PTPY'] = hours_requirement_PTPY * weeks_requirement_PTPY
df['PTPY'] = df['PTPY']-df['FTFY']

# Define relevant health insurance variables
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['Public HI'] = 1*(df['HIMCAIDLY']==2) \
    + (1-1*(df['HIMCAIDLY']==2))*(df['HIMCARELY']==2)
df['No HI'] = 1*(df['VERIFY']==1) \
    + (1-1*(df['VERIFY']==1))*(df['ANYCOVNW']==2)

# Define Relevant working variables
df['SELFEMP'] = 1*(df['CLASSWLY']==13) + 1*(df['CLASSWLY']==14) 

#Reset index
df.reset_index(inplace=True)

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


#%% Result 1: Change in Share Reporting ESHI Dependent  #%%
os.chdir(output_folder)

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
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
plt.savefig('Effect_HI_byAgeGroup_ESHI_Dependent.png', dpi=500)
plt.clf()

##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years)
for age in ages:
    df_age = df[df['AGELY']==age]
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
plt.savefig('Effect_HI_byAge_ESHI_Dependent.png', bbox_inches="tight", dpi=500)
plt.clf() 


#%% Result 2: Change in Share Reporting ESHI Policyholder  #%%
os.chdir(output_folder)

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:        
        results.loc[group_name, year] = \
            100*np.average(df_age_group['GRPOWNLY']==2, \
                           weights=df_age_group['YEARLY']==year)
for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting ESHI Policyholder')
plt.legend()
plt.tight_layout()
plt.savefig('Effect_HI_byAgeGroup_ESHI_Policyholder.png', dpi=500)
plt.clf()

##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years)
for age in ages:
    df_age = df[df['AGELY']==age]
    for year in years:
        results.loc[age, year] = \
            100*np.average(df_age['GRPOWNLY']==2, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting ESHI Policyholder')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_ESHI_Policyholder.png', bbox_inches="tight", dpi=500)
plt.clf()


#%% Result 3: No Change in Share Reporting Public HI  #%%
os.chdir(output_folder)

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:
        results.loc[group_name, year] = \
            100*np.average(df_age_group['Public HI']==1, \
                           weights=df_age_group['YEARLY']==year)
for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Public HI')
plt.legend()
plt.tight_layout()
plt.savefig('Effect_HI_byAgeGroup_Public_HI.png', dpi=500)
plt.clf()
plt.show()

##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years)
for age in ages:
    df_age = df[df['AGELY']==age]
    for year in years:        
        results.loc[age, year] = \
            100*np.average(df_age['Public HI']==1, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Public HI')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_Public_HI.png', bbox_inches="tight", dpi=500)
plt.clf()


#%% Result 4: Change in Share Reporting Coverage by Person outside HH  #%%
os.chdir(output_folder)

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:        
        results.loc[group_name, year] = \
            100*np.average(df_age_group['OUT']==2, \
                           weights=df_age_group['YEARLY']==year)
for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct HI Coverage Outside HH')
plt.legend()
plt.tight_layout()
plt.savefig('Effect_HI_byAgeGroup_Outside_HI.png', dpi=500)
plt.clf()

##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years)
for age in ages:
    df_age = df[df['AGELY']==age]
    for year in years:        
        results.loc[age, year] = \
            100*np.average(df_age['OUT']==2, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct HI Coverage Outside HH')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_Outside_HI.png', bbox_inches="tight", dpi=500)
plt.clf()


#%% Result 5: Change in Share Reporting No HI  #%%
os.chdir(output_folder)

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years[1:])
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years[1:]:
        results.loc[group_name, year] = \
            100*np.average(df_age_group['No HI']==1, \
                           weights=df_age_group['YEARLY']==year)
for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting No HI')
plt.legend()
plt.tight_layout()
plt.savefig('Effect_HI_byAgeGroup_No_HI.png', dpi=500)
plt.clf()

##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years[1:])
for age in ages:
    df_age = df[df['AGELY']==age]
    for year in years[1:]:        
        results.loc[age, year] = \
            100*np.average(df_age['No HI']==1, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting No HI')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_No_HI.png', bbox_inches="tight", dpi=500)
plt.clf()


#%% Result 6: No Change in Share reporting self-employment  #%%
os.chdir(output_folder)

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:        
        results.loc[group_name, year] = \
            100*np.average(df_age_group['SELFEMP']==1, \
                           weights=df_age_group['YEARLY']==year)
for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Self-Employed')
plt.legend()
plt.tight_layout()
plt.savefig('Effect_HI_byAgeGroup_Self_Employed.png', dpi=500)
plt.clf()

##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years)
for age in ages:
    df_age = df[df['AGELY']==age]
    for year in years[1:]:        
        results.loc[age, year] = \
            100*np.average(df_age['SELFEMP']==1, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Self-Employed')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_Self_Employed.png', bbox_inches="tight", dpi=500)
plt.clf()


#%% Result 7: No Change in Share reporting part-time employment  #%%


##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:        
        results.loc[group_name, year] = \
            100*np.average(df_age_group['FULLPART']==2, \
                           weights=df_age_group['YEARLY']==year)

for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Part-Time Employment')
plt.legend()
plt.tight_layout()
plt.savefig('Effect_HI_byAgeGroup_part.png', dpi=500)
plt.clf()



##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years[1:])
for age in ages:
    df_age = df[df['AGELY']==age]
    for year in years[1:]:
        results.loc[age, year] = \
            100*np.average(df_age['FULLPART']==2, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Part-Time Employment')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_part.png', bbox_inches="tight", dpi=500)
plt.clf()


#%% Result 8: No Change in Share reporting FTFY employment  #%%

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:        
        results.loc[group_name, year] = \
            100*np.average(df_age_group['FTFY'], \
                           weights=df_age_group['YEARLY']==year)

for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Full-Time Employment')
plt.legend()
plt.tight_layout()
plt.savefig('Effect_HI_byAgeGroup_full.png', dpi=500)
plt.clf()



##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years[1:])

for age in ages:
    df_age = df[df['AGELY']==age]
    for year in years[1:]:
        results.loc[age, year] = \
            100*np.average(df_age['FTFY'], \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Full-Time Employment')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_full.png', bbox_inches="tight", dpi=500)
plt.clf()



#%% Result 9: No Change in Share 16-24 reporting full-time student  #%%

##### Results by Age (full-time college #####
results = pd.DataFrame(index=ages[:6], columns = years[1:])

for age in ages[:6]:
    df_age = df[df['AGELY']==age]
    for year in years[1:]:
        results.loc[age, year] = \
            100*np.average(df_age['SCHLCOLL']==3, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages[:6]:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Full-Time Student')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_student_full.png', bbox_inches="tight", dpi=500)
plt.clf()

##### Results by Age (part-time college) #####
results = pd.DataFrame(index=ages[:6], columns = years[1:])

for age in ages[:6]:
    df_age = df[df['AGELY']==age]
    for year in years[1:]:
        results.loc[age, year] = \
            100*np.average(df_age['SCHLCOLL']==4, \
                           weights=df_age['YEARLY']==year)
cm = plt.get_cmap('coolwarm')
for age in ages[:6]:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Pct Reporting Part-Time Student')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_student_part.png', bbox_inches="tight", dpi=500)
plt.clf()



#%% Result 10: No Change in Wages for ESHI dependents  #%%

##### Results by Age Group #####
results = pd.DataFrame(index=age_group2name_Dict.values(), columns = years)
for age_group in age_groups:
    df_age_group = df[[x in age_group for x in df['AGELY']]]
    group_name = age_group2name_Dict[age_group[0]]
    for year in years:        
        results.loc[group_name, year] = \
            (1e-3)*np.average(df_age_group['INCWAGE'], \
                           weights=(df_age_group['YEARLY']==year)*\
                                   (df_age_group['ESHI_dependent'])*\
                                       (df_age_group['FTFY']))

for age_group in age_group2name_Dict.keys():
    group_name = age_group2name_Dict[age_group]
    group_color = age_group2color_Dict[group_name]
    plt.plot(results.loc[group_name], label=group_name, color=group_color)
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Wages (Thous.)')
plt.legend()
plt.tight_layout()
plt.savefig('Effect_HI_byAgeGroup_wage.png', dpi=500)
plt.clf()


##### Results by Age #####
results = pd.DataFrame(index=ages, columns = years[1:])
for age in ages:
    df_age = df[df['AGELY']==age]
    for year in years[1:]:
        results.loc[age, year] = \
            (1e-3)*np.average(df_age['INCWAGE'], \
                           weights=(df_age['YEARLY']==year)*\
                                   (df_age['ESHI_dependent'])*\
                                       (df_age['FTFY']))
cm = plt.get_cmap('coolwarm')
for age in ages:
    age_color = 0.5 + (age-18)/10
    if age >= 26: age_color = (age-25.9)/14
    plt.plot(results.loc[age], label=age, color=cm(age_color))
plt.xticks(range(2000,2021,4))
plt.axvline(x = 2009.5, color = 'gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Wages (Thous.)')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.savefig('Effect_HI_byAge_wage.png', bbox_inches="tight", dpi=500)
plt.clf()
