#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :temporal_scale.py
# @Time      :2024/09/15 22:13:51
# @Author    :Haofan Wang

import logging

def temporal_allocation(emis_ds, current_time, temporal_profile, monthly, weekly, hourly):
    """_summary_

    Args:
        emis_ds (_type_): _description_
        current_time (_type_): _description_
        temporal_profile (_type_): _description_
        monthly (_type_, optional): _description_. Defaults to None.
        weekly (_type_, optional): _description_. Defaults to None.
        hourly (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    
    if monthly is not None:
        result = next((item for item in temporal_profile['monthly'] if item['index'] == int(monthly)), None)
        
        if result is None:
            logging.ERROR(f'The monthly profile (index = {monthly}) is not found.')
            exit()
        
        mm = current_time.strftime('%m')
        monthly_profile = result['profile']
        current_month_emis = emis_ds * monthly_profile[int(mm)-1]
        
    if weekly is not None:
        result = next((item for item in temporal_profile['weekly'] if item['index'] == int(weekly)), None)
        
        if result is None:
            logging.ERROR(f'The weekly profile (index = {weekly}) is not found.')
            exit()

        ww = current_time.strftime('%w')  # Get the day of the week (0 for Sunday, 1-6 for Monday-Saturday)
        if ww == '0':
            ww = '7'
        weekly_profile = result['profile']
        
        if monthly is not None:
            current_week_emis = current_month_emis * 0.25 * weekly_profile[int(ww)-1]
        else:
            current_week_emis = emis_ds * 0.25 * weekly_profile[int(ww)-1]
        
    if hourly is not None:
        result = next((item for item in temporal_profile['hourly'] if item['index'] == int(hourly)), None)
        
        if result is None:
            logging.ERROR(f'The hourly profile (index = {hourly}) is not found.')
            exit()
            
        hh = current_time.strftime('%H')
        hourly_profile = result['profile']
        
        # 目前支持的最小原始排放清单分辨率为月尺度排放
        current_hour_emis = current_week_emis * hourly_profile[int(hh)-1]
    
    return current_hour_emis


        