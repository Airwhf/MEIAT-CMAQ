#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :config.py
# @Time      :2024/09/11 13:22:23
# @Author    :Haofan Wang

import yaml
import pandas as pd
import logging

def read_config():
    with open('HEMCO_Config.yaml', 'r') as file:
        data = yaml.safe_load(file)
        
    # Get the Emissions switch configuration.
    switch_config = data['switch']
    
    # Get the global configuration.
    global_config = data['global']
    
    # Get the emission configuration.
    emission_config = data['emissions']
    
    # Get the temporal profile configuration.
    temporal_profile = data['temporal_profile']
    
    return global_config, switch_config, emission_config, temporal_profile


def replace_global_variables(df, global_config):
    """This function is used to replace the global variables in the DataFrame.

    Args:
        df (Pandas.DataFrame): This is the sorted DataFrame.
        global_config (dict): This is the global configuration from the YAML file.
    """
     
    # 记录path的list
    path_list = []
    for _path in df['path'].values:
        _path = _path.replace('$ROOT', global_config['ROOT'])
        path_list.append(_path)
        
    df['path'] = path_list
    return df


def convert_config_to_df(switch_config, emission_config, global_config):
    """This function is used to convert the configuration to a DataFrame.

    Args:
        switch_config (dict): This is the switch configuration from the YAML file.
        emission_config (dict): This is the emission configuration from the YAML file.
        global_config (dict): This is the global configuration from the YAML file.

    Returns:
        DataFrame: This is the sorted DataFrame.
    """
    # Loop the switch_config and record the configuration which is True.
    emission_labels = []
    logging.info("The Emission configuration:")
    for key, value in switch_config.items():
        if value:
            emission_labels.append(key)
            logging.info(f"     ---- {key} is True.")
    logging.info(" ")
    
    # Get the all species names.
    species_repo = []
    for emission_label in emission_labels:
        # print(len(emission_config[emission_label]))
        for _dict in emission_config[emission_label]:
            if _dict['species_name'] not in species_repo:
                species_repo.append(_dict['species_name'])
                
    # 创建一个DataFrame，每个DataFrame对应一个物种，每个物种的处理顺序按照layer从低到高进行排序。
    dfs = []
    for _species in species_repo:
        df = pd.DataFrame(
            columns=[
                'species_name', 'layer', 'path', 'units',
                'species_profile', 'mask', 'temporal_format'
            ]
        )
    
        for emission_label in emission_labels:
            emission_repo = emission_config[emission_label]
            for _dict in emission_repo:
                if _dict['species_name'] == _species:
                    df = pd.concat([df, pd.DataFrame([_dict])], ignore_index=True)
                    
        # df = df.sort_values(by=['layer'])
        
        # Replace the ROOT to the global_config
        df = replace_global_variables(df, global_config)
        
        # Append the DataFrame to the list
        dfs.append(df)
        
    # Concatenate all the DataFrames
    df = pd.concat(dfs, ignore_index=True)
        
    return df

def read_temporal_format(temporal_format_str):
    """This function is used to read the temporal format string from the YAML file.

    Args:
        temporal_format_str (str): This is the temporal format string from the YAML file.

    Returns:
        time_periods (turple): This is the list of time periods.
    """
    _ = temporal_format_str.split('/')
    
    # Check if there is 0.
    if _[0] == '0':  # year
        start_year = -1
        end_year = -1
    else:
        start_year = int(_[0].split('-')[0])
        end_year = int(_[0].split('-')[1])
        
    if _[1] == '0':  # month
        start_month = -1
        end_month = -1
    else:
        start_month = int(_[1].split('-')[0])
        end_month = int(_[1].split('-')[1])
        
    if _[2] == '0':  # day
        start_day = -1
        end_day = -1
    else:
        start_day = int(_[2].split('-')[0])
        end_day = int(_[2].split('-')[1])
        
    if _[3] == '0':  # hour
        start_hour = -1
        end_hour = -1
    else:
        start_hour = int(_[3].split('-')[0])
        end_hour = int(_[3].split('-')[1])
    return (start_year, end_year, start_month, end_month, start_day, end_day, start_hour, end_hour)

    