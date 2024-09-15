#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :src.py
# @Time      :2024/09/15 14:34:22
# @Author    :Haofan Wang

import os
import pandas as pd


def user_control():
    # import datetime
    # specified_time = datetime.datetime(2500, 6, 30, 23, 59)
    # # 获取当前时间
    # current_time = datetime.datetime.now()
    # # 检查当前时间是否已经超过指定时间
    # if current_time > specified_time:
    #     return False
    # else:
    #     return True
    return True

def time_format():
    import datetime
    return f'{datetime.datetime.now()}|> '

# def vertical_allocation(eipath, output_dir):
def vertical_allocation(eipath, output_dir, sector):  # Modify by Haofan Wang.
    import PseudoNetCDF as pnc
    # import pandas as pd
    # import numpy as np
    # --------------------------------------------------------------------------------------------------------
    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)
    e2df = pnc.pncopen(eipath, format='ioapi')
    varliststr = getattr(e2df, 'VAR-LIST')
    varlist = [varliststr[i:i + 16].strip() for i in range(0, len(varliststr), 16)]
    profpath = 'profile.csv'
    profile = pd.read_csv(profpath)
    nz = profile.shape[0]
    # outpath = 'example_3d_emissions.nc'
    outpath = f"{output_dir}/{os.path.basename(eipath)}"
    verbose = 0
    e3df = e2df.slice(LAY=[0] * nz)
    e3df.VGLVLS = profile.vglvltop.values.astype('f')
    e3df.NLAYS = nz
    e3df.VGTOP = e2df.VGTOP
    for key, var3d in e3df.variables.items():
        if key not in varlist:
            continue
        var2d = e2df.variables[key]
        vals2d = var2d[:]
        # vals3d = vals2d * profile['fraction'].values[None, :, None, None]
        vals3d = vals2d * profile[sector].values[None, :, None, None]  # Modify by Haofan Wang.
        var3d[:] = vals3d
        
    if os.path.exists(outpath):
        os.remove(outpath)
    outf = e3df.save(outpath, verbose=verbose, complevel=1, format="NETCDF3_CLASSIC")
    outf.close()


def create_emission_file(
        emission_date,
        grid_desc,
        grid_name,
        label,
        sector,
        inventory_year,
        inventory_mechanism,
        target_mechanism):
    # --------------------------------------------------------------------------------------------------------
    # import pandas as pd
    import datetime
    import PseudoNetCDF as pnc
    import numpy as np
    # --------------------------------------------------------------------------------------------------------
    # Convert the emission date to other format.
    datetime_emission = pd.to_datetime(emission_date)
    yyyymmdd = datetime.datetime.strftime(datetime_emission, "%Y%m%d")
    # yyyy = datetime.datetime.strftime(datetime_emission, "%Y")
    mm = datetime.datetime.strftime(datetime_emission, "%m")
    # dd = datetime.datetime.strftime(datetime_emission, "%d")
    yyyyjjj = datetime.datetime.strftime(datetime_emission, "%Y%j")
    w = datetime.datetime.strftime(datetime_emission, "%w")

    # Create template file.
    gf = pnc.pncopen(grid_desc, GDNAM=grid_name, format="griddesc", SDATE=int(yyyyjjj), TSTEP=10000, withcf=False)
    gf.updatetflag(overwrite=True)
    tmpf = gf.sliceDimensions(TSTEP=[0] * 25)
    max_col_index = getattr(tmpf, "NCOLS") - 1
    max_row_index = getattr(tmpf, "NROWS") - 1

    # Create the source file and read it.
    source_file = f"output/source/source-{label}-{sector}-{inventory_year}-{mm}.csv"
    data = pd.read_csv(source_file)

    # Add I and J coordinate and calculate the total emission.
    I, J = gf.ll2ij(data["LON"].values, data["LAT"].values)
    # data["I"], data["J"] = data["rownum"], data["colnum"]
    data["I"], data["J"] = I, J
    celltotal = data.groupby(["I", "J"], as_index=False).sum()
    celltotal = celltotal[
        (celltotal["I"] >= 0)
        & (celltotal["J"] >= 0)
        & (celltotal["I"] <= max_col_index)
        & (celltotal["J"] <= max_row_index)
        ]
    # Read species file.
    species_file = (
        f"species/{inventory_mechanism}_{target_mechanism}_speciate_{sector}.csv"
    )
    species_info = pd.read_csv(species_file)
    fname_list = species_info.pollutant.values
    var_list = species_info.emission_species.values
    factor_list = species_info.split_factor.values
    divisor_list = species_info.divisor.values
    origin_units = species_info.inv_unit.values
    target_units = species_info.emi_unit.values

    # Read the temporal file.
    # _monthly_factor = pd.read_csv("temporal/monthly.csv")
    _weekly_factor = pd.read_csv("temporal/weekly.csv")
    _hourly_factor = pd.read_csv("temporal/hourly.csv")
    # monthly_factor = _monthly_factor[sector].values
    weekly_factor = _weekly_factor[sector].values
    hourly_factor = _hourly_factor[sector].values

    # Loop the species and create the variable to IOAPI file.
    items = zip(
        fname_list, var_list, factor_list, divisor_list, origin_units, target_units
    )
    for fname, var, split_factor, divisor, origin_unit, target_unit in items:
        try:
            # Extract the current pollutant.
            df = celltotal[["I", "J", fname]]

            # Convert monthly emission to weekly emission.
            weekly_values = df[fname].values * 0.25  # Version 1.0 and Version 1.1
            # weekly_values = converted_values * 0.25

            # Convert weekly emission to daily emission.
            daily_values = weekly_values * weekly_factor[int(w)]

            # Convert daily emission to hourly emission.
            df_list = []
            for hour_i in range(24):
                _df = pd.DataFrame(columns=["J", "I", "hour", "values"])
                _df["J"] = df.J.values
                _df["I"] = df.I.values
                _df["hour"] = np.zeros(df.shape[0]) + hour_i
                _df["values"] = daily_values * hourly_factor[hour_i]
                df_list.append(_df)
            result = pd.concat(df_list)
            # print(result)

            # Convert original units to target units and input the split_factor.
            if origin_unit == "Mmol" and target_unit == "mol/s":
                result["values"] = result["values"] * 1000000.0 / 3600.0 * split_factor
            elif origin_unit == "Mg" and target_unit == "g/s":
                result["values"] = result["values"] * 1000000.0 / 3600.0 * split_factor
            elif origin_unit == "Mg" and target_unit == "mol/s":
                result["values"] = (result["values"] * 1000000.0 / 3600.0 / divisor * split_factor)

            # Convert the I, J, hour to int.
            result[["hour", "J", "I"]] = result[["hour", "J", "I"]].astype("int")
            h = result.hour
            i = result.I
            j = result.J

            # Create the variable of emission.
            evar = tmpf.createVariable(var, "f", ("TSTEP", "LAY", "ROW", "COL"))
            if target_unit == "mol/s":
                evar.setncatts(dict(units="moles/s", long_name=var, var_desc=var))
            elif target_unit == "g/s":
                evar.setncatts(dict(units="g/s", long_name=var, var_desc=var))
            evar[h, h * 0, j, i] = result["values"].values

        except KeyError:
            # If don not have this pollutant in GeoTIFF, skip it.
            print(f"Warning: Do not have the pollutant named {fname}.")
            continue
        
    # Get rid of initial DUMMY variable
    del tmpf.variables["DUMMY"]

    # Update TFLAG to be consistent with variables
    tmpf.updatetflag(tstep=10000, overwrite=True)

    # Remove VAR-LIST so that it can be inferred
    delattr(tmpf, "VAR-LIST")
    tmpf.updatemeta()

    # Save out.
    output_name = f"output/{target_mechanism}_{sector}_{grid_name}_{yyyymmdd}.nc"
    tmpf.save(output_name, format="NETCDF3_CLASSIC")


def split_file_extension(filebasename):
    filename, file_extension = os.path.splitext(filebasename)
    return filename, file_extension


# 基于MEIC清单的source文件构建
def create_source(label, year, mm, development_list, emission_factor_dir, emission_data_dir, out_path):
    # import pandas as pd
    import glob
    import tqdm

    for development in development_list:
        emission_factor_file = f'{emission_factor_dir}/EF_{development}.csv'
        if os.path.exists(f"{out_path}/source-{label}-{development}-{year}-{mm}.csv"):
            continue

        # 读取排放因子文件
        ef_data = pd.read_csv(emission_factor_file)

        result = pd.DataFrame(columns=["LON", "LAT"])
        result['LON'] = ef_data['LON']
        result['LAT'] = ef_data['LAT']

        files = glob.glob(f'{emission_data_dir}/{label}_{year}_{mm}__{development}__*.csv')

        for file in tqdm.tqdm(files, desc=f'Create source file of {development}'):
            specie = encode_title(os.path.basename(file))["pollutant"]
            data = pd.read_csv(file)
            values = []
            for i in range(ef_data.shape[0]):
                temp_area = ef_data['AREA'].values[i]
                temp_ef = ef_data['EF'].values[i]
                temp_big_emis = data[data['NAME'].isin([temp_area])]['SUM'].values
                temp_small_emis = temp_ef * temp_big_emis
                try:
                    values.append(temp_small_emis[0])
                except IndexError:
                    values.append(0.0)
            result[specie] = values

        result.to_csv(f"{out_path}/source-{label}-{development}-{year}-{mm}.csv", index=False)


def encode_title(file_name):
    import re
    # Get the species name from file name.
    condition = f"(.*?)_(.*?)_(.*?)__(.*?)__(.*?).csv"
    encode_name = re.findall(condition, file_name)[0]
    label = encode_name[0]
    year = encode_name[1]
    month = encode_name[2]
    sector = encode_name[3]
    pollutant = encode_name[4]
    dict = {"label": label,
            "year": year,
            "month": month,
            "sector": sector,
            "pollutant": pollutant}
    return dict


def encode_title_tiff(file_name):
    import re
    # Get the species name from file name.
    condition = f"(.*?)_(.*?)_(.*?)__(.*?)__(.*?).tiff"
    encode_name = re.findall(condition, file_name)[0]
    label = encode_name[0]
    year = encode_name[1]
    month = encode_name[2]
    sector = encode_name[3]
    pollutant = encode_name[4]
    dict = {"label": label,
            "year": year,
            "month": month,
            "sector": sector,
            "pollutant": pollutant}
    return dict


def read_tiff(file):
    import rioxarray as rxr
    import numpy as np
    """

    :param file: The file path of GeoTIFF.
    :return: value, longitude, latitude.
    """
    dataset = rxr.open_rasterio(file)
    longitude = dataset.coords["x"].values
    latitude = dataset.coords["y"].values
    lons, lats = np.meshgrid(longitude, latitude)
    value = dataset[0, ...].values
    return value, lons, lats


def create_source_table(input_dir, mm, sector):
    import glob
    # import pandas as pd
    import re
    """

    :param input_dir: the path of input directory which store the GeoTIFF files.
    :param mm: the month of emission file date.
    :param sector: the sector of emission file.
    :return: DataFrame, a table include latitude, longitude and species values.
    """
    # Search the files in the input directory.
    files = glob.glob(f"{input_dir}/*_{mm}__{sector}__*.tiff")

    # Build a DataFrame to store the inventory information.
    df = pd.DataFrame(columns=["lat", "lon"])
    # --- Start loop of the sector files.
    for file in files:
        # Read the GeoTIFF and return the value and geographic information.
        value, lons, lats = read_tiff(file)

        # Get the species name from file name.
        basename = os.path.basename(file)
        condition = f"(.*?)_(.*?)_{mm}__{sector}__(.*?).tiff"
        encode_name = re.findall(condition, basename)[0]
        # label = encode_name[0]
        # year = encode_name[1]
        pollutant = encode_name[2]
        # Put the pollutant to pd.DataFrame.
        df[pollutant] = value.flatten()
        df["lat"] = lats.flatten()
        df["lon"] = lons.flatten()
    return df


def source2cmaq(
    emission_date,
    grid_desc,
    grid_name,
    sector,
    input_dir,
    inventory_mechanism,
    target_mechanism,
    output_dir,
):
    """

    :param emission_date: set the date for CMAQ emission file.
    :param grid_desc: the path of GRIDDESC file.
    :param grid_name: set the grid name.
    :param sector: the sector of original emission inventory.
    :param input_dir: the path of input directory which store the GeoTIFF files.
    :param inventory_mechanism: set chemical mechanism of inventory.
    :param target_mechanism: set chemical mechanism of CMAQ emission file.
    :param output_dir: set the output directory.
    :return:
    """
    # import pandas as pd
    import datetime
    import PseudoNetCDF as pnc
    import numpy as np

    # Convert the emission date to other format.
    datetime_emission = pd.to_datetime(emission_date)
    yyyymmdd = datetime.datetime.strftime(datetime_emission, "%Y%m%d")
    # yyyy = datetime.datetime.strftime(datetime_emission, "%Y")
    mm = datetime.datetime.strftime(datetime_emission, "%m")
    # dd = datetime.datetime.strftime(datetime_emission, "%d")
    yyyyjjj = datetime.datetime.strftime(datetime_emission, "%Y%j")
    w = datetime.datetime.strftime(datetime_emission, "%w")

    # Create template file.
    gf = pnc.pncopen(
        grid_desc,
        GDNAM=grid_name,
        format="griddesc",
        SDATE=int(yyyyjjj),
        TSTEP=10000,
        withcf=False,
    )
    gf.updatetflag(overwrite=True)
    tmpf = gf.sliceDimensions(TSTEP=[0] * 25)
    max_col_index = getattr(tmpf, "NCOLS") - 1
    max_row_index = getattr(tmpf, "NROWS") - 1

    # Create the source file and read it.
    data = create_source_table(input_dir, mm, sector)

    # Add I and J coordinate and calculate the total emission.
    data["I"], data["J"] = tmpf.ll2ij(data.lon.values, data.lat.values)
    celltotal = data.groupby(["I", "J"], as_index=False).sum()
    celltotal = celltotal[
        (celltotal["I"] >= 0)
        & (celltotal["J"] >= 0)
        & (celltotal["I"] <= max_col_index)
        & (celltotal["J"] <= max_row_index)
    ]
    celltotal = celltotal.drop(columns=["lon", "lat"], axis=1)

    # Read species file.
    species_file = (
        f"species/{inventory_mechanism}_{target_mechanism}_speciate_{sector}.csv"
    )
    species_info = pd.read_csv(species_file)
    fname_list = species_info.pollutant.values
    var_list = species_info.emission_species.values
    factor_list = species_info.split_factor.values
    divisor_list = species_info.divisor.values
    origin_units = species_info.inv_unit.values
    target_units = species_info.emi_unit.values

    # Read the temporal file.
    # _monthly_factor = pd.read_csv("temporal/monthly.csv")
    _weekly_factor = pd.read_csv("temporal/weekly.csv")
    _hourly_factor = pd.read_csv("temporal/hourly.csv")
    # monthly_factor = _monthly_factor[sector].values
    weekly_factor = _weekly_factor[sector].values
    hourly_factor = _hourly_factor[sector].values

    # Loop the species and create the variable to IOAPI file.
    items = zip(
        fname_list, var_list, factor_list, divisor_list, origin_units, target_units
    )
    for fname, var, split_factor, divisor, origin_unit, target_unit in items:
        try:
            # Extract the current pollutant.
            df = celltotal[["I", "J", fname]]

            # Convert monthly emission to weekly emission.
            weekly_values = df[fname].values * 0.25

            # Convert weekly emission to daily emission.
            daily_values = weekly_values * weekly_factor[int(w)]

            # Convert daily emission to hourly emission.
            df_list = []
            for hour_i in range(24):
                _df = pd.DataFrame(columns=["J", "I", "hour", "values"])
                _df["J"] = df.J.values
                _df["I"] = df.I.values
                _df["hour"] = np.zeros(df.shape[0]) + hour_i
                _df["values"] = daily_values * hourly_factor[hour_i]
                df_list.append(_df)
            result = pd.concat(df_list)

            # Convert original units to target units and input the split_factor.
            if origin_unit == "Mmol" and target_unit == "mol/s":
                result["values"] = result["values"] * 1000000.0 / 3600.0 * split_factor
            elif origin_unit == "Mg" and target_unit == "g/s":
                result["values"] = result["values"] * 1000000.0 / 3600.0 * split_factor
            elif origin_unit == "Mg" and target_unit == "mol/s":
                result["values"] = (
                    result["values"] * 1000000.0 / 3600.0 / divisor * split_factor
                )

            # Convert the I, J, hour to int.
            result[["hour", "J", "I"]] = result[["hour", "J", "I"]].astype("int")
            h = result.hour
            i = result.I
            j = result.J

            # Create the variable of emission.
            evar = tmpf.createVariable(var, "f", ("TSTEP", "LAY", "ROW", "COL"))
            if target_unit == "mol/s":
                evar.setncatts(dict(units="moles/s", long_name=var, var_desc=var))
            elif target_unit == "g/s":
                evar.setncatts(dict(units="g/s", long_name=var, var_desc=var))
            evar[h, h * 0, j, i] = result["values"].values

        except KeyError:
            # If don not have this pollutant in GeoTIFF, skip it.
            print(f"Warning: Do not have the pollutant named {fname}.")
            continue
    # Get rid of initial DUMMY variable
    del tmpf.variables["DUMMY"]

    # Update TFLAG to be consistent with variables
    tmpf.updatetflag(tstep=10000, overwrite=True)

    # Remove VAR-LIST so that it can be inferred
    delattr(tmpf, "VAR-LIST")
    tmpf.updatemeta()

    # Save out.
    # output_name = f"{output_dir}/{grid_name}_{yyyymmdd}_{target_mechanism}_{sector}.nc" # 1.4
    output_name = f"{output_dir}/{target_mechanism}_{sector}_{grid_name}_{yyyymmdd}.nc" # 1.5
    tmpf.save(output_name, format="NETCDF3_CLASSIC")
    tmpf.close()
    # print(f"Finish: {output_name}")


def read_nml(nml_path):
    import f90nml
    example = f90nml.read(nml_path)
    griddesc_file = example["global"]["griddesc_file"]
    griddesc_name = example["global"]["griddesc_name"]
    big_grid_file = example["global"]["big_grid_file"]
    inventory_year = example["global"]["inventory_year"]
    sectors = example["global"]["sectors"]
    geotiff_dir = example["global"]["geotiff_dir"]
    allocation_raster = example["global"]["allocator"]
    inventory_label = example["global"]["inventory_label"]
    inventory_mechanism = example["global"]["inventory_mechanism"]
    target_mechanism = example["global"]["target_mechanism"]
    start_date = example["global"]["start_date"]
    end_date = example["global"]["end_date"]
    cores = example["global"]["cores"]
    return griddesc_file, griddesc_name,\
        big_grid_file, inventory_year,\
        sectors, geotiff_dir, allocation_raster, inventory_label, inventory_mechanism, target_mechanism,\
        start_date, end_date, cores


def main_f2c():
    # --------------------------------------------------------------------------------------------------------
    if user_control() is True:
        print("### This system is developed by Haofan Wang.            ###")
        print("### Email: wanghf58@mail2.sysu.edu.cn                   ###")
    else:
        print("### This system is developed by Haofan Wang.            ###")
        print("### You can contact me for any suggestions.             ###")
        print("### Email: wanghf58@mail2.sysu.edu.cn                   ###")
        print("### *************************************************** ###")
        print("### The current version has expired.                    ###")
        print("### Please contact me to request the latest version.    ###")
        print("### *************************************************** ###")
        return
    # --------------------------------------------------------------------------------------------------------
    import f90nml
    import multiprocessing
    # --------------------------------------------------------------------------------------------------------
    example = f90nml.read("namelist.input")
    gridFile = example["global"]["griddesc_file"]
    gridName = example["global"]["griddesc_name"]

    # The path of input directory which store the GeoTIFF files.
    input_directory = example["global"]["geotiff_dir"]

    # Set the sectors of these emission inventory.
    sectors = example["global"]["sectors"]
    if type(sectors) != type(["list"]):
        sectors = [sectors]

    # Set the date for CMAQ emission file.
    start_date = pd.to_datetime(example["global"]["start_date"])
    end_date = pd.to_datetime(example["global"]["end_date"])

    # Set chemical mechanism. This parameter is set for species file.
    inventory_mechanism = example["global"]["inventory_mechanism"]
    target_mechanism = example["global"]["target_mechanism"]

    # Set the output directory.
    path = os.getcwd()
    output_directory = f"{path}/output"

    # Set the parallel cores.
    cores = example["global"]["cores"]

    # Make output directory.
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Obtain the available core number.
    num_cores = multiprocessing.cpu_count()
    print("The total core: ", num_cores)
    print("Your set is: ", cores)
    if cores > num_cores:
        print("Please ensure that the number of cores used "
              "does not exceed the maximum number of cores on your computer.")
        exit()

    # Create a threading pool that use the all cores.
    pool = multiprocessing.Pool(cores)

    # Build a argument pool.
    # import pandas as pd
    emission_dates = [str(date) for date in pd.period_range(pd.to_datetime(start_date), pd.to_datetime(end_date))]
    arg_pool = []
    for emisfile_date in emission_dates:
        for sector in sectors:
            arg = (emisfile_date, gridFile, gridName, sector, input_directory,
                   inventory_mechanism, target_mechanism, output_directory)
            arg_pool.append(arg)

    # Start cores.
    results = pool.starmap(source2cmaq, arg_pool)

    # Close the thread pool.
    pool.close()
    pool.join()

    print("Done")


def read_allocator(nml_path):
    import f90nml
    example = f90nml.read(nml_path)
    allocator_types = example["global"]["allocator_type"]
    return allocator_types


def read_line(nml_path):
    import f90nml
    example = f90nml.read(nml_path)
    line_files = example["line"]["line_files"]
    line_factors = example["line"]["line_factors"]
    return line_files, line_factors


def main_createCMAQ():
    # --------------------------------------------------------------------------------------------------------
    if user_control() is True:
        print("### This system is developed by Haofan Wang.            ###")
        print("### Email: wanghf58@mail2.sysu.edu.cn                   ###")
    else:
        print("### This system is developed by Haofan Wang.            ###")
        print("### You can contact me for any suggestions.             ###")
        print("### Email: wanghf58@mail2.sysu.edu.cn                   ###")
        print("### *************************************************** ###")
        print("### The current version has expired.                    ###")
        print("### Please contact me to request the latest version.    ###")
        print("### *************************************************** ###")
        return
    # --------------------------------------------------------------------------------------------------------
    import multiprocessing
    # --------------------------------------------------------------------------------------------------------
    griddesc_file, griddesc_name, big_grid_file, inventory_year, sectors, geotiff_dir, allocation_raster, \
        inventory_label, inventory_mechanism, target_mechanism, start_date, end_date, cores = read_nml("namelist.input")

    if type(sectors) != type(["list"]):
        _sectors = []
        _sectors.append(sectors)
        sectors = _sectors

    # Obtain the available core number.
    num_cores = multiprocessing.cpu_count()
    print("The total core: ", num_cores)
    print("Your set is: ", cores)
    if cores > num_cores:
        print("Please ensure that the number of cores used "
              "does not exceed the maximum number of cores on your computer.")
        exit()

    # Create a threading pool that use the all cores.
    pool = multiprocessing.Pool(cores)

    # Build a argument pool.
    emission_dates = [str(date) for date in pd.period_range(pd.to_datetime(start_date), pd.to_datetime(end_date))]
    arg_pool = []
    for emisfile_date in emission_dates:
        for sector in sectors:
            arg = (
            emisfile_date, griddesc_file, griddesc_name, inventory_label, sector, inventory_year, inventory_mechanism,
            target_mechanism)

            arg_pool.append(arg)

    # Start cores.
    results = pool.starmap(create_emission_file, arg_pool)

    # Close the thread pool.
    pool.close()
    pool.join()

    print("Done")
