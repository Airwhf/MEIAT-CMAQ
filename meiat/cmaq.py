#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :cmaq.py
# @Time      :2024/09/10 22:00:22
# @Author    :Haofan Wang

import os
import PseudoNetCDF as pnc
import pandas as pd
import logging

# ignored warnings
import warnings
warnings.filterwarnings("ignore")

# os.environ['IOAPI_ISPH'] = '6370000.'
# os.environ['SDATE'] = '1970001'

def create_grid2d_file(griddesc, gridname):
    """This function is used to create the grid2d file.

    Args:
        griddesc (str): The path of the griddesc file.
        gridname (str): The name of the grid in the griddesc file.

    Returns:
        netCDF: The GRIDDESC DataFrame (NetCDF).
    """
    gf = pnc.pncopen(griddesc, format='griddesc', GDNAME=gridname)
    gf.SDATE = 2016001
    gf.TSTEP = 10000
    gf.updatetflag(overwrite=True)
    return gf
    # pass
    

def get_boundary_for_clip(gf):
    """_summary_

    Args:
        gf (NetCDF): The grid2d file.

    Returns:
        bounds: The boundary of the CMAQ domain.
    """
    lon2d = gf.variables['longitude'].__array__()
    lat2d = gf.variables['latitude'].__array__()
    lon_min, lon_max = lon2d.min(), lon2d.max()
    lat_min, lat_max = lat2d.min(), lat2d.max()
    bounds = [lon_min, lon_max, lat_min, lat_max]
    return bounds

def get_area(gf):
    """_summary_

    Args:
        gf (_type_): _description_

    Returns:
        Area: units: m^2
    """
    x = gf.getncattr('XCELL')
    y = gf.getncattr('YCELL')
    return x * y

def create_cmaq_emission_file_all(run_startdate, run_enddate, grid_desc, grid_name):
    df = pd.read_csv('/Users/haofanwang/project_script/MEIAT-CMAQ/total_emission.csv')
    time_range = pd.date_range(run_startdate, run_enddate, freq='H')
    yyyyjjj = run_startdate.strftime('%Y%j')
    time_n = time_range.shape[0]

    # 创建CMAQ排放文件
    gf = pnc.pncopen(grid_desc, GDNAM=grid_name, format="griddesc", SDATE=int(yyyyjjj), TSTEP=10000, withcf=False)
    gf.updatetflag(overwrite=True)
    tmpf = gf.sliceDimensions(TSTEP=[0] * time_n)
    max_col_index = getattr(tmpf, "NCOLS") - 1
    max_row_index = getattr(tmpf, "NROWS") - 1
    
    df_each_specie = df.groupby('species_name')
    for specie_name, specie_df in df_each_specie:
        
        # 计算时间维度
        # 假设 specie_df 是你的 DataFrame
        specie_df['time'] = pd.to_datetime(specie_df['time'])  # 将 time 列转换为 datetime 类型

        # 计算每个时间与起始时间的时间差，并将其转换为整数小时数
        specie_df['hour'] = (specie_df['time'] - run_startdate).dt.total_seconds() // 3600
        
        I, J = gf.ll2ij(specie_df["lon"].values, specie_df["lat"].values)
        # data["I"], data["J"] = data["rownum"], data["colnum"]
        specie_df["i"], specie_df["j"] = I, J
        celltotal = specie_df.groupby(["i", "j", "hour", "layer"], as_index=False).sum()
        celltotal = celltotal[
            (celltotal["i"] >= 0) &
            (celltotal["j"] >= 0) &
            (celltotal["i"] <= max_col_index) &
            (celltotal["j"] <= max_row_index)
        ]
        celltotal[["i", "j", "layer", "hour"]] = celltotal[["i", "j", "layer", "hour"]].astype(int)
        
        h = celltotal['hour'].values
        j = celltotal['j'].values
        i = celltotal['i'].values
        lay = celltotal['layer'].values
        
        evar = tmpf.createVariable(specie_name, "f", ("TSTEP", "LAY", "ROW", "COL"))
        # if target_unit == "mol/s":
        #     evar.setncatts(dict(units="moles/s", long_name=var, var_desc=var))
        # elif target_unit == "g/s":
        #     evar.setncatts(dict(units="g/s", long_name=var, var_desc=var))
        evar[h, lay, j, i] = celltotal["emissions"].values
        
    # Get rid of initial DUMMY variable
    del tmpf.variables["DUMMY"]
    
    # Update TFLAG to be consistent with variables
    tmpf.updatetflag(tstep=10000, overwrite=True)

    # Remove VAR-LIST so that it can be inferred
    delattr(tmpf, "VAR-LIST")
    tmpf.updatemeta()
    
    # Save the file
    output_name = f"./output_{grid_name}/emis_all.nc"
    logging.info(f"Saving to {output_name}.")
    tmpf.save(output_name, format="NETCDF3_CLASSIC")
  
    return tmpf


if __name__ == "__main__":
    run_startdate = pd.to_datetime('2017-01-01 00:00:00')
    run_enddate = pd.to_datetime('2017-01-02 23:00:00')
    
    grid_desc = '/Users/haofanwang/project_script/MEIAT-CMAQ/input/GRIDDESC.CN27km'
    grid_name = 'CN27km'
    
    gf = create_cmaq_emission_file_all(run_startdate, run_enddate, grid_desc, grid_name)
    
    
    