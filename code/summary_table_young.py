#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  8 21:23:02 2022

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

#%% Data Cleaning #%%

# Drop invalid responses
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'ANYCOVLY', 'GRPCOVLY']:
    df = df[[not np.isnan(x) for x in df[var]]]
df = df[[not x in [0,1,999] for x in df['EDUC']]]
df = df[df['WKSWORK2']!=9]

# Drop self-employed workers
df = df[[(not x in [10,13,14,29]) for x in df['CLASSWLY']]]

# Adjust year bc survey data corresponds to prev year
df[df['YEAR'] >= 2019]
df['YEAR'] = df['YEAR'] - 1

# Define college attendance
df['College'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College'] = 1-df['College']

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
df_FTFY = df[df['FTFY']==1]

## Define Part-Time, Part-Year
hours_requirement_PTPY =  1*(df['UHRSWORKLY'] > 0)
weeks_requirement_PTPY =  1*(df['WKSWORK2'] > 0)
df['PTPY'] = hours_requirement_PTPY * weeks_requirement_PTPY
df['PTPY'] = df['PTPY']-df['FTFY']
df_PTPY = df[df['PTPY']==1]

# Constant column
df['Total'] = 1


### Focus on Young workers
#Differentiate variables in reference to this year or last
df['AGENW'] = df['AGE'] 
df['AGELY'] = (df['AGE']-1)
ages = range(18,33)

df = df[1*(df['AGELY'] <= 32)*(df['AGELY'] >= 18)==1] 

#%% Create Table Data #%%

## Create Dataframe with Table Data
table_data = pd.DataFrame(columns=['Group', 'Subgroup', 'Variable', 'Value'])
for group in ['Total', 'FTFY', 'PTPY']:
    group_var = df[group]
    
    for column in ['Total', 'College', 'Non-College']:
        column_var = df[column]
        
        ### Calculations        
        ## Health Insurance
        PUB_HI = np.average(df['Public HI'], weights=df['ASECWT']*group_var*column_var)
        PUB_HI_Medicaid = np.average(df['Public HI (Medicaid)'], weights=df['ASECWT']*group_var*column_var)
        PUB_HI_Medicare = np.average(df['Public HI (Medicare)'], weights=df['ASECWT']*group_var*column_var)
        PRVT_HI = np.average(df['Private HI'], weights=df['ASECWT']*group_var*column_var)
        ESHI = np.average(df['ESHI'], weights=df['ASECWT']*group_var*column_var)
        ESHI_own = np.average(df['ESHI_own'], weights=df['ASECWT']*group_var*column_var)
        ESHI_dependent = np.average(df['ESHI_dependent'], weights=df['ASECWT']*group_var*column_var)
        Other_PRVT_HI = np.average(df['Other Private'], weights=df['ASECWT']*group_var*column_var)
        HI_Other = np.average(df['HI Other'], weights=df['ASECWT']*group_var*column_var)
        No_HI = np.average(df['No HI'], weights=df['ASECWT']*group_var*column_var)
        
        ### Append to Dataframe
        ### Define rows of table:
        table_data.loc[len(table_data)]= group, column, 'Share with Private HI', PRVT_HI
        table_data.loc[len(table_data)]= group, column, 'Employer-Sponsored', ESHI
        table_data.loc[len(table_data)]= group, column, 'Policyholder', ESHI_own
        table_data.loc[len(table_data)]= group, column, 'Dependent', ESHI_dependent
        table_data.loc[len(table_data)]= group, column, 'Share with Other HI', HI_Other
        table_data.loc[len(table_data)]= group, column, 'Other Private', Other_PRVT_HI
        table_data.loc[len(table_data)]= group, column, 'Public HI', PUB_HI
        table_data.loc[len(table_data)]= group, column, 'Medicaid', PUB_HI_Medicaid
        table_data.loc[len(table_data)]= group, column, 'Medicare', PUB_HI_Medicare
        table_data.loc[len(table_data)]= group, column, 'Uninsured', No_HI
        

#%% Output Latex Table: Summary Stats #%%

#List of rows
variables = ['Employer-Sponsored',
               'Policyholder', 
               'Dependent',
               'Other Private',
               'Public HI',
               'Medicaid',
               'Medicare',
               'Uninsured']

indented_variables = ['Policyholder', 
               'Dependent',
               'Medicaid',
               'Medicare']


#Dictionaries for each group to panel title
group2title_Dict={'Total':'Panel A: Population ages 18-32', 
                  'FTFY':'Panel B: Full-Time, Full-Year Workers ages 18-32', 
                  'PTPY':'Panel C: Part-Time or Part-Year Workers ages 18-32'}

#Loop through each group
table_values = []
for group in ['Total', 'FTFY', 'PTPY']:
    df_panel = table_data[table_data['Group']==group]
        
    # For column in ['Total', 'College', 'Non-college']:
    df_panel_t = df_panel[df_panel['Subgroup']=='Total']
    df_panel_c = df_panel[df_panel['Subgroup']=='College']
    df_panel_n = df_panel[df_panel['Subgroup']=='Non-College']
    
    # Set index to variable
    df_panel_t=df_panel_t.set_index('Variable')
    df_panel_c=df_panel_c.set_index('Variable')
    df_panel_n=df_panel_n.set_index('Variable')
    
    # Loop through each variable
    panel_values = []
    for var in variables:
        var_t = df_panel_t.loc[var, 'Value']
        var_c = df_panel_c.loc[var, 'Value']
        var_n = df_panel_n.loc[var, 'Value']
        string = f'\t {var} & {var_t:,.3f} & {var_c:,.3f} & {var_n:,.3f} & \\\\ \n'
        
        #Indent 'policyholder' and 'dependent;
        if var in indented_variables:
            string = '\t \\ \\ \\ \\ \\small '+ string[2:] 
    
        #Add row to panel values
        panel_values.append(string)
        
    #Concatenate strigns for the panel
    panel_header = ['\multicolumn{5}{l} \n{\\textsl{',
                    group2title_Dict[group],
                    '}} \\\\ \n\hline \n',
                    '& Total & College & Non-College \\\\ \n\hline \n']
    
    panel_bottom = ['\hline \hline \\\\  \n']
    
    #Add panel to table values
    table_values = table_values + panel_header + panel_values + panel_bottom


## Create Table Header and Bottom
table_header = ['\centering \n',
                '\\begin{tabular}{lcccccc} \n'
                '\hline  \n']


table_bottom = ['\end{tabular}']
        
#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open(f"summary_stats_young.tex","w")
file.writelines(table_header) 
file.writelines(table_values)   
file.writelines(table_bottom)   
file.close()

