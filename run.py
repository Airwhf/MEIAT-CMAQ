#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :hco_cmaq.py
# @Time      :2024/09/07 17:23:53
# @Author    :Haofan Wang

import os
# import yaml
import logging
import pandas as pd
import xarray as xr

from meiat.system import init_logging
from meiat.config import read_config, convert_config_to_df, read_temporal_format
from meiat.cmaq import get_boundary_for_clip, create_grid2d_file, get_area, create_cmaq_emission_file_all
from meiat.temporal_scale import temporal_allocation
from meiat.interplotation import interplotation_to_cmaq
from meiat.gas_or_particle import convert_kg_to_mol


if __name__ == "__main__":
    
    # Initialize the logging
    init_logging(level=logging.INFO)
    
    # Read YAML file
    config_file = "hco_cmaq.yml"
    global_config, switch_config, emission_config, temporal_profile = read_config()
    
    # Convert the configuration to a DataFrame.
    df = convert_config_to_df(switch_config, emission_config, global_config)
    
    # Create the emission file and get the boundary of the CMAQ domain.
    gf = create_grid2d_file(global_config['GRIDDESC'], global_config['GRIDNAME'])
    bounds = get_boundary_for_clip(gf)
    lon_min, lon_max, lat_min, lat_max = bounds
    lon_min_clip, lon_max_clip = lon_min - 1, lon_max + 1
    lat_min_clip, lat_max_clip = lat_min - 1, lat_max + 1
    
    # 获取行号和列号
    # nrows, ncols = gf.getncattr('NROWS'), gf.getncattr('NCOLS')
    
    # Split the DataFrame by `species_name`.
    df_species = df.groupby('species_name')
    
    # Loop the date from the `run_startdate` and `run_enddate`.
    run_startdate = global_config['RUN_STARTDATE']
    run_enddate = global_config['RUN_ENDDATE']
    time_periods = pd.period_range(run_startdate, run_enddate, freq='H')
    
    #! 这是非常重要的一个记录数据，可能会占用非常大的内存。
    # 把所有物种，所有部门以及所有时间的数据都放到一个DataFrame中.
    df_all = pd.DataFrame(
        columns=[
            'species_name', 'sector', 'time',
            'layer', 'lon', 'lat', 'emissions'
        ]
    )
    
    # 按每天处理数据
    for current_time in time_periods:
        
        # 记录日志
        logging.info(f'Processing {current_time}.')
        
        # 获取当前日期
        yyyy = current_time.strftime('%Y')
        mm = current_time.strftime('%m')
        dd = current_time.strftime('%d')
        hh = current_time.strftime('%H')
        
        # 处理每个物种
        for df_species_name, df_species_value in df_species:
            # 记录日志
            logging.info(f' ---- Writing {df_species_name} ...')
            
            # 按图层从低到高进行排序
            df_species_value = df_species_value.sort_values(by='layer')
            
            # 处理不同排放清单中的同一物种
            for index, current_item in df_species_value.iterrows():
                temporal_config = read_temporal_format(current_item['temporal_format'])
                start_year = temporal_config[0]
                end_year = temporal_config[1]
                start_month = temporal_config[2]
                end_month = temporal_config[3]
                start_day = temporal_config[4]
                end_day = temporal_config[5]
                start_hour = temporal_config[6] 
                end_hour = temporal_config[7]
                
                # 判断当前物种是气体还是颗粒物
                if current_item['gas_or_particle'] == 'gas':
                    gas_or_particle = 'gas'
                elif current_item['gas_or_particle'] == 'particle':
                    gas_or_particle = 'particle'
                else:
                    logging.error(f"{df_species_name} in {yyyy}-{mm}-{dd} can not be processed because of wrong gas_or_particle.")
                    exit()
                
                # 获取摩尔质量
                molecular_mass = current_item['molecular_mass']
                
                #TODO `path` 中的时间处理部分
                # 如果年份处于范围内，将$YYYY替换为对应的年份。
                if start_year <= int(yyyy) <= end_year:
                    current_item['path'] = current_item['path'].replace('$YYYY', yyyy)
                elif start_year == -1 and end_year == -1:
                    # 如果年份不限制，则不进行任何替换。
                    pass
                else:
                    # 如果年份不在范围内，直接退出。
                    logging.error(f"{df_species_name} in {yyyy}-{mm}-{dd} can not be processed.")
                    exit()
                    
                if start_month <= int(mm) <= end_month:
                    current_item['path'] = current_item['path'].replace('$MM', mm)
                elif start_month == -1 and end_month == -1:
                    # 如果月份不限制，则不进行任何替换。
                    pass
                else:
                    # 如果月份不在范围内，直接退出。
                    logging.error(f"{df_species_name} in {yyyy}-{mm}-{dd} can not be processed.")
                    exit()
                
                if start_day <= int(dd) <= end_day:
                    current_item['path'] = current_item['path'].replace('$DD', dd)
                elif start_day == -1 and end_day == -1:
                    # 如果天数不限制，则不进行任何替换。
                    pass
                else:
                    # 如果天数不在范围内，直接退出。
                    logging.error(f"{df_species_name} in {yyyy}-{mm}-{dd} can not be processed.")
                
                if start_hour <= int(yyyy) <= end_hour:
                    current_item['path'] = current_item['path'].replace('$HH', yyyy)
                elif start_hour == -1 and end_hour == -1:
                    # 如果小时不限制，则不进行任何替换。
                    pass
                else:
                    # 如果小时不在范围内，直接退出。
                    logging.error(f"{df_species_name} in {yyyy}-{mm}-{dd} can not be processed.")
                    
                #TODO 获取当前排放文件路径并查看其是否存在。
                current_emis_path = current_item['path']
                if os.path.exists(current_emis_path) == False:
                    logging.error(f"{current_emis_path} does not exist.")
                    exit()
                
                #TODO 读取并裁减当前排放文件以节省内存占用。
                with xr.open_dataset(current_emis_path) as ds:
                    ds = ds.sel(lon=slice(lon_min_clip, lon_max_clip), lat=slice(lat_min_clip, lat_max_clip))
                    ds = ds.sel(time=f'{yyyy}-{mm}-{dd}', method='nearest')
                    emis = ds[current_item['variable_name']]
                    emis_units = emis.units
                    monthly_index = current_item['monthly_profile']
                    weekly_index = current_item['weekly_profile']
                    hourly_index = current_item['hourly_profile']             
                    
                    # 如果物种为气体物种，排放单位为 kg/m2/s，但是物种的摩尔质量为 None，直接退出。
                    if gas_or_particle == 'gas' and emis_units == 'kg m-2 s-1' and molecular_mass == None:
                        logging.error(
                            f"{df_species_name} in {yyyy}-{mm}-{dd} can not be processed because of wrong molecular_mass."
                        )
                        exit()
                    
                    # 单位为 kg/m2/s 或 mol/m2/s，需要修改为 g/s 或 mol/s
                    #* 当前小时的排放通量
                    emis = temporal_allocation(
                        emis, current_time, temporal_profile, 
                        monthly_index, weekly_index, hourly_index
                    )
                    
                    #TODO 插值emis到gf网格，并分别转换kg/m2/s和mol/m2/s为kg/s和mol/s。
                    emis_df = interplotation_to_cmaq(emis, gf)        
                    emis_df['emissions'] = emis_df['emissions'] * get_area(gf)
                    
                    # 如果物种为气体，但是排放单位为 kg m-2 s-1，则需要进行转换。
                    if gas_or_particle == 'gas' and emis_units == 'kg m-2 s-1':
                        emis_df = convert_kg_to_mol(emis_df, molecular_mass)  # 此时的排放清单单位为mol/s
                    
                    # 增加其他信息。
                    #! Layer在后续需要进行更新，以标识垂直分配过程。
                    emis_df['species_name'] = df_species_name
                    emis_df['sector'] = current_item['sector']
                    emis_df['time'] = current_time
                    emis_df['layer'] = 0
                    
                    # 将当前排放数据添加到总排放数据中。
                    df_all = pd.concat([df_all, emis_df])
    
    # 至此已经输出总的排放文件目录
    #TODO 创建排放文件并写入数据
    if global_config['EMIS_TYPE'] == 'ALL':
        tmpf = create_cmaq_emission_file_all(
            run_startdate, run_enddate, global_config['GRIDDESC'], global_config['GRIDNAME']
        )
    
        
