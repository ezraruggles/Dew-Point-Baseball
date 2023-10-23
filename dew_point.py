# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 13:13:54 2023

@author: ezrar
"""
#%%
# Ezra Ruggles
# The Impact of Humidity Conditions on Pitching Performance
# 10/23/23
 
#%% IMPORT PACKAGES------------------------------------------------------------------------------------
import pandas as pd

#%% READING IN DATA AND GROUPING BY PITCHER---------------------------------------------------------------------

df = pd.read_csv('data.csv')

# Get unique pitcher IDs
pitchers = df['PITCHER_KEY'].unique()

# Create a dictionary to store DataFrames for each pitcher
pitcher_dataframes = {}

for pitcher_id in pitchers:
    # Create a DataFrame for each pitcher
    pitcher_df = df[df['PITCHER_KEY'] == pitcher_id].copy()
    
    # Store the pitcher's DataFrame in the dictionary with the pitcher's ID as the key
    pitcher_dataframes[pitcher_id] = pitcher_df
    
    
#%% EXPECTED COMPARISON ANALYSIS


def find_final_report(dataframe):
    
    def find_report(pitcher_ID):
        
        data = pitcher_dataframes[pitcher_ID]
            #Create empty data frame to store data
        df_pitch_type_means = pd.DataFrame({'Pitch Types': [],
                                                    'RPMS': [],
                                                    'MPH': [],
                                                    'HB': [],
                                                    'IVB': [],
                                                    'X': [],
                                                    'Z': []})
            
        for i in data['PITCH_TYPE_TRACKED_KEY'].unique():
                rows_pitch_type = data[data['PITCH_TYPE_TRACKED_KEY'] == i]
                #Find the averages to store in the df
                mean_RPMS = rows_pitch_type['SPIN_RATE_ABSOLUTE'].mean()
                mean_MPH = rows_pitch_type['RELEASE_SPEED'].mean()
                mean_HB = rows_pitch_type['HORIZONTAL_BREAK'].mean()
                mean_IVB = rows_pitch_type['INDUCED_VERTICAL_BREAK'].mean()
                mean_X = rows_pitch_type['PLATE_X'].mean()
                mean_Z = rows_pitch_type['PLATE_Z'].mean()
                #Store data in row
                new_row = {'Pitch Types': i,
                           'RPMS': mean_RPMS ,
                           'MPH': mean_MPH,
                           'HB': mean_HB,
                           'IVB': mean_IVB,
                           'X': mean_X,
                           'Z': mean_Z}
        
                #Append row of stored data to the df
                df_pitch_type_means = df_pitch_type_means.append(new_row, ignore_index=True)
        
        df_report_data = []
        
        for index, row in data.iterrows():
            prob = 0.5
            expected = df_pitch_type_means[df_pitch_type_means['Pitch Types'] == row['PITCH_TYPE_TRACKED_KEY']]
            
            RPM_diff = expected['RPMS'].values[0] - row['SPIN_RATE_ABSOLUTE']
            MPH_diff = expected['MPH'].values[0] - row['RELEASE_SPEED']
            HB_diff = expected['HB'].values[0] - row['HORIZONTAL_BREAK']
            IVB_diff = expected['IVB'].values[0] - row['INDUCED_VERTICAL_BREAK']
            X_diff = expected['X'].values[0] - row['PLATE_X']
            Z_diff = expected['Z'].values[0] - row['PLATE_Z']
            
        #--- WITHIN A CERTAIN DISTANCE TO THE EXPECTED WE SHOULD SEE SIMILARITIES, IF NOT
        #--- THEN WE BLAME DEW POINT-----------------------------------------------------------------------------
            if abs(RPM_diff) <= 100 and abs(MPH_diff) <= 3 and abs(HB_diff) < 1 and abs(IVB_diff) < 1:
                
                if abs(X_diff) >= 0.2:
                    prob += 0.01
                    
                elif abs(Z_diff) >= 0.2:
                    prob += 0.01
                
                else:
                    prob -= 0.01
                
            if abs(RPM_diff) <= 100 and abs(MPH_diff) <= 3:
                
                if abs(HB_diff) >= 1 and abs(IVB_diff) >= 1:
                    prob += 0.01
        #----------------------------------------------------------------------------------------------------------   
        #--- IN THIS BIN, WE LOOK AS PITCHES THAT ARE DIFFERENT THAT THE EXPECTED BUT CLOSE ENOUGH TO SEE A TREND
        
            if RPM_diff < 0 and abs(RPM_diff) > 100: # Checking if the spin on the ball is higher
                    
            
                    if abs(RPM_diff) >= 200 and MPH_diff <= 0: # If the ball is spinning more and slower then the ball should curve more
                        
                        if abs(HB_diff) < 1 and abs(IVB_diff) < 1:
                            prob += 0.01
                        else:
                            prob -= 0.01
                    
                    
        #------------------------------------------------------------------------------------------------------------
        #--- FOR ALL OTHER PITCHES, WE CAN NOT SAY MUCH ABOUT THEIR EFFECTIVENESS DUE TO DEW POINT
        
        
                    
            df_report_data.append({'PID': row['PID'], 'Prob_Dew_Point': prob})
        
        return(pd.DataFrame(df_report_data))
    
    final_df = pd.DataFrame()
    for pitcher in dataframe:
        new_report = find_report(pitcher)
        final_df = pd.concat([final_df, new_report], ignore_index=True)
    
    final_df.to_csv('submission.csv', index=False)

find_final_report(pitcher_dataframes)
    
