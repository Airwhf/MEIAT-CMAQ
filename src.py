# import datetime
# import glob
# import multiprocessing
import os
# import os.path
# import re
import time
# import shutil
#
# import PseudoNetCDF as pnc
# import arcgisscripting
# import arcpy
# import f90nml
# import geopandas as gpd
# import numpy as np
# import pandas as pd
# import pyioapi
# import pyproj
# import rioxarray as rxr
# import tqdm
# from arcpy.sa import *
# from shapely.geometry import Polygon, Point
# from shapely.ops import cascaded_union
# from shapely.prepared import prep
#
# import shapefile as shp

# import arcgisscripting
# import arcpy
# from arcpy.sa import *
# # Use half of the cores on the machine
# arcpy.env.parallelProcessingFactor = "50%"
# arcpy.env.overwriteOutput = True
import pandas as pd


def user_control():
    import datetime
    specified_time = datetime.datetime(2500, 6, 30, 23, 59)
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 检查当前时间是否已经超过指定时间
    if current_time > specified_time:
        return False
    else:
        return True


def time_format():
    import datetime
    return f'{datetime.datetime.now()}|> '


def main_mosaic(
        upper_raster_dir,
        bottom_raster_dir,
        output_dir,
        upper_raster_pollutants,
        bottom_raster_pollutants,
        output_pollutants,
        upper_label,
        bottom_label,
        output_label,
        upper_raster_template,
        bottom_raster_template,
        upper_resolution,
        bottom_resolution,
        sectors,
        upper_year,
        bottom_year,
        output_year,
):
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

    import rasterio
    import arcpy
    import shutil

    arcpy.env.parallelProcessingFactor = "50%"
    arcpy.env.overwriteOutput = True

    factor = bottom_resolution ** 2 / upper_resolution ** 2

    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)

    for month in range(1, 13):
        month = r"%.2d" % month
        for sector in sectors:
            for upper_raster_pollutant, bottom_raster_pollutant, output_pollutant in zip(upper_raster_pollutants,
                                                                                         bottom_raster_pollutants,
                                                                                         output_pollutants):
                upper_raster_file = f"{upper_raster_dir}/{upper_label}_{upper_year}_{month}__{sector}__{upper_raster_pollutant}.tiff"
                bottom_raster_file = f"{bottom_raster_dir}/{bottom_label}_{bottom_year}_{month}__{sector}__{bottom_raster_pollutant}.tiff"

                upper_raster_file_test = os.path.exists(upper_raster_file)
                bottom_raster_file_test = os.path.exists(bottom_raster_file)

                if upper_raster_file_test is False:
                    with rasterio.open(upper_raster_template) as src:
                        raster_data = src.read(1)
                        output_meta = src.meta.copy()
                    values = raster_data * 0
                    with rasterio.open(upper_raster_file, "w", **output_meta) as dest:
                        # 将相加后的数据写入新的栅格文件
                        dest.write(values, 1)
                if bottom_raster_file_test is False:
                    with rasterio.open(bottom_raster_template) as src:
                        raster_data = src.read(1)
                        output_meta = src.meta.copy()
                    values = raster_data * 0
                    with rasterio.open(bottom_raster_file, "w", **output_meta) as dest:
                        # 将相加后的数据写入新的栅格文件
                        dest.write(values, 1)

                with rasterio.open(bottom_raster_template) as src:
                    raster_data = src.read(1)
                    output_meta = src.meta.copy()
                with rasterio.open(bottom_raster_file, "w", **output_meta) as dest:
                    # 将相加后的数据写入新的栅格文件
                    dest.write(raster_data / factor, 1)

                output_name = f"{output_dir}/{output_label}_{output_year}_{month}__{sector}__{output_pollutant}.tif"
                if os.path.exists(output_name):
                    os.remove(output_name)
                shutil.copy(bottom_raster_file, output_name)

                # 使用arcpy.sa.MosaicToNewRaster()函数将两个输入栅格镶嵌到一个新的栅格文件中
                arcpy.Mosaic_management([output_name, upper_raster_file],
                                        output_name,
                                        mosaic_type="LAST",
                                        nodata_value=0, )
                # 删除多余文件
                if os.path.exists(output_name[0:-4] + ".tfw"):
                    os.remove(output_name[0:-4] + ".tfw")
                if os.path.exists(output_name + ".aux.xml"):
                    os.remove(output_name + ".aux.xml")
                if os.path.exists(output_name + ".xml"):
                    os.remove(output_name + ".xml")
                if os.path.exists(output_name + ".ovr"):
                    os.remove(output_name + ".ovr")
                shutil.move(output_name, output_name + "f")
                print(f"Finish and output {output_name}f.")


def main_vertical_allocation(files, sectors):
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
    path = os.getcwd()
    output_dir = fr"{path}/output/vertical"
    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)

    # Set the parallel cores.
    example = f90nml.read("namelist.input")
    cores = example["global"]["cores"]

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
    arg_pool = []
    for file in files:
        for sector in sectors:
            arg = (file, output_dir, sector)
            arg_pool.append(arg)

    # Start cores.
    results = pool.starmap(vertical_allocation, arg_pool)

    # Close the thread pool.
    pool.close()
    pool.join()

    print("Done")

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


def main_coarse2fine():
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
    import PseudoNetCDF as pnc
    import geopandas as gpd
    # import pandas as pd
    import numpy as np
    # --------------------------------------------------------------------------------------------------------
    path = os.getcwd()
    # --------------------------------------------------------------------------------------------------------
    output_dir = f"{path}/output"
    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)

    # --------------------------------------------------------------------------------------------------------
    example = f90nml.read("namelist.input")
    griddesc_file = example["global"]["griddesc_file"]
    griddesc_name = example["global"]["griddesc_name"]

    # --------------------------------------------------------------------------------------------------------
    control_create_grid = example["control"]["create_grid"]
    print(f"--------------Fine grid shapefile|> {output_dir}/shapefile-grid.shp--------------")
    if int(control_create_grid) == 1:
        print(
            f'{time_format()}The control of create grid is {control_create_grid} and processor start creating fine grid.')
        draw_modle_grid(griddesc_file)
        gf = pnc.pncopen(griddesc_file, GDNAM=griddesc_name, format="griddesc", SDATE=2023001, TSTEP=10000,
                         withcf=False)
        gpdf = gpd.read_file(f"{output_dir}/shapefile-grid.shp")
        lon, lat = gf.ij2ll(gpdf["colnum"].values, gpdf["rownum"].values)
        gpdf["LON"] = lon
        gpdf["LAT"] = lat
        gpdf.to_file(f'{output_dir}/shapefile-grid.shp', driver='ESRI Shapefile', encoding='utf-8')
        gpdf[["ID", "colnum", "rownum", "LON", "LAT"]].to_csv(f"{output_dir}/shapefile-grid.csv")
        print(f'{time_format()}Finish creating fine grid shapefile.')
    else:
        print(f"{time_format()}The control of create grid is {control_create_grid}.")
        if os.path.exists(f"{output_dir}/shapefile-grid.shp"):
            print(f"{time_format()}There is fine grid shapefile and processor will continue.")
        else:
            print(f"{time_format()}There is not fine grid shapefile and processor will exit.")
            exit()

    # --------------------------------------------------------------------------------------------------------
    small_grid = f"{output_dir}/shapefile-grid.shp"
    big_grid = example["global"]["big_grid_file"]
    control_grid_info = example["control"]["grid_info"]
    grid_info_out_path = output_dir
    print(f"-----------------Grid information|> {grid_info_out_path}/grid_info.csv--------------")
    if int(control_grid_info) == 1:
        print(
            f'{time_format()}The control of grid information is {control_grid_info} and processor start for grid information.')
        if os.path.exists(grid_info_out_path) is False:
            os.makedirs(grid_info_out_path)
        max_id = pd.read_csv(f"{output_dir}/shapefile-grid.csv")["ID"].values.max()
        create_gridinfo(small_grid, big_grid, grid_info_out_path, max_id)
        grid_info_path = f'{grid_info_out_path}/grid_info.csv'
        print(f'{time_format()}Finish creating grid information.')
    else:
        print(f"{time_format()}The control of grid information is {control_grid_info}.")
        if os.path.exists(f'{grid_info_out_path}/grid_info.csv'):
            print(f"{time_format()}There is grid information and processor will continue.")
        else:
            print(f"{time_format()}There is not grid information and processor will exit.")
            exit()

    # --------------------------------------------------------------------------------------------------------
    ef_out_path = f'{output_dir}/factor'
    grid_info_path = f'{grid_info_out_path}/grid_info.csv'
    if os.path.exists(ef_out_path) is False:
        os.mkdir(ef_out_path)
    control_create_factor = example["control"]["create_factor"]
    print(f"----------------Allocation factor|> {ef_out_path}--------------")
    # 读取分配因子类型 分配因子路径 分配部门
    allocator_types = example["global"]["allocator_type"]
    if type(allocator_types) != type(["list"]):
        allocator_types = [allocator_types]
    allocators = example["global"]["allocator"]
    if type(allocators) != type(["list"]):
        allocators = [allocators]
    sectors = example["global"]["sectors"]
    if type(sectors) != type(["list"]):
        sectors = [sectors]

    if int(control_create_factor) == 1:
        print(
            f'{time_format()}The control of allocation factor is {control_create_factor} and processor start for allocation factor.')
        for allocator_type, allocator, sector in zip(allocator_types, allocators, sectors):
            # 判断数据是否已经存在，如果存在就直接跳过。
            if os.path.exists(f'{ef_out_path}/EF_{sector}.csv'):
                print(f"{time_format()}There is {ef_out_path}/EF_{sector}.csv and processor will skip this loop.")
                continue
            print(f"{time_format()}There is the process for {sector} and the allocator type is {allocator_type}.")
            if allocator_type == "line":
                road_dir = f"{path}/allocator"
                line_files = example["line"]["line_files"]
                line_factors = example["line"]["line_factors"]
                print(f"{time_format()}Allocator        | {line_files}.")
                print(f"{time_format()}Allocator factor | {line_factors}.")
                road_allocation(line_files, road_dir, small_grid, big_grid, grid_info_path, ef_out_path)
                output_name = f'{ef_out_path}/EF_{sector}.csv'
                ef_files = [f"{output_dir}/factor/EF_{line_file}.csv" for line_file in line_files]
                road_deal(ef_files, line_factors, output_name)
            elif allocator_type == "raster":
                result_csv_path_name = f'EF_{sector}'
                raster_file = f"{path}/allocator/{allocator}"
                print(f"{time_format()}Allocator        | {raster_file}.")
                raster_allocation(raster_file, small_grid, big_grid, grid_info_path, ef_out_path, result_csv_path_name)
            else:
                print(f"{time_format()}Allocator type is not support.| {allocator_type}.")
    else:
        print(f"{time_format()}The control of allocation is {control_create_factor}.")
        for sector in sectors:
            if os.path.exists(f'{ef_out_path}/EF_{sector}.csv'):
                print(f"{time_format()}There is allocation factor and processor will continue.")
            else:
                print(f"{time_format()}There is not allocation factor and processor will exit.")
                exit()
    # --------------------------------------------------------------------------------------------------------
    control_coarse_emis = example["control"]["coarse_emission"]
    print(f"----------------Coarse Emission|> f'{output_dir}/zoning_statistics'--------------")
    if int(control_coarse_emis) == 1:
        print(
            f'{time_format()}The control of coarse emission is {control_coarse_emis} and processor start for coarse emission.')
        meic_zoning_out = f'{output_dir}/zoning_statistics'
        if os.path.exists(meic_zoning_out) is False:
            os.mkdir(meic_zoning_out)
        geotiff_dir = example["global"]["geotiff_dir"]
        start_date = pd.to_datetime(example["global"]["start_date"])
        end_date = pd.to_datetime(example["global"]["end_date"])
        date_list = pd.date_range(start_date, end_date)
        mms = np.unique(np.array([temp_date.strftime("%m") for temp_date in date_list]))
        for mm in mms:
            zoning_statistics(small_grid, big_grid, geotiff_dir, meic_zoning_out, mm)
    else:
        print(f"{time_format()}The control of coarse emission is {control_coarse_emis}.")

    # --------------------------------------------------------------------------------------------------------
    meic_zoning_out = f'{output_dir}/zoning_statistics'
    control_create_source = example["control"]["create_source"]
    source_out_dir = f'{output_dir}/source'
    if os.path.exists(source_out_dir) is False:
        os.mkdir(source_out_dir)
    print(f"----------------Coarse Emission|> f'{output_dir}/source'--------------")
    if int(control_create_source) == 1:
        start_date = pd.to_datetime(example["global"]["start_date"])
        end_date = pd.to_datetime(example["global"]["end_date"])
        date_list = pd.date_range(start_date, end_date)
        mms = np.unique(np.array([temp_date.strftime("%m") for temp_date in date_list]))
        for mm in mms:
            print(f"Processing for month {mm}.")
            inventory_label = example["global"]["inventory_label"]
            inventory_year = example["global"]["inventory_year"]
            create_source(inventory_label, inventory_year, mm, sectors, ef_out_path, meic_zoning_out, source_out_dir)
            print(
                f'{time_format()}The control of create source is {control_create_source} and processor start for coarse emission.')
        else:
            print(
                f'{time_format()}The control of create source is {control_create_source}.')

    # --------------------------------------------------------------------------------------------------------
    print('# ------------------------------------' + 'End' + '------------------------------------ #')
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(f"The program end time ：{current_time}")
    print('# ------------------------------------' + '---' + '------------------------------------ #')


def main_create_CMAQ_mask(gadmpath, field, output_name):
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
    import shapefile as shp
    import numpy as np
    import PseudoNetCDF as pnc
    from shapely.geometry import Polygon, Point
    from shapely.ops import cascaded_union
    from shapely.prepared import prep
    # --------------------------------------------------------------------------------------------------------

    # Set the parallel cores.
    example = f90nml.read("namelist.input")
    grid_file = example["global"]["griddesc_file"]
    grid_name = example["global"]["griddesc_name"]

    # Open the shapefile.
    shpf = shp.Reader(gadmpath)

    # Find where is the field.
    fldnames = [n for n, t, l, d in shpf.fields][1:]
    try:
        pos = np.where(np.array(fldnames) == field)[0][0]
    except IndexError:
        exit("ERROR: No such field in the shapefile.")

    # All field attributes.
    _ = [rec[pos] for ri, rec in enumerate(shpf.iterRecords())]
    _ = np.unique(np.array(_))

    # Open the GRIDDESC.
    gf = pnc.pncopen(grid_file, format='griddesc', GDNAM=grid_name)
    outf = gf.eval("DUMMY = DUMMY[:] * 0")

    for city_name in _:
        # Integrate the all sub-shapefile.
        recordnums = [ri for ri, rec in enumerate(shpf.iterRecords()) if rec[pos] == city_name]
        shapes = [shpf.shape(rn) for rn in recordnums]
        polygons = [Polygon(s.points).buffer(0) for s in shapes]
        ppolygons = [prep(p) for p in polygons]
        uberpoly = cascaded_union(polygons)
        puberpoly = prep(uberpoly)

        evar = outf.createVariable(city_name, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))

        Ipl1, Jpl1 = np.meshgrid(np.arange(gf.NCOLS + 1), np.arange(gf.NROWS + 1))
        LONp1, LATp1 = gf.ij2ll(Ipl1, Jpl1)
        Xp1, Yp1 = gf.ll2xy(LONp1, LATp1)
        LOND, LATD = gf.xy2ll(Xp1 - gf.XCELL / 2, Yp1 - gf.YCELL / 2)
        LON = LONp1[:-1, :-1]
        LAT = LATp1[:-1, :-1]

        gf.SDATE = 2019001
        MINE = outf.variables[city_name]
        MINE.units = 'fraction'
        MINE.long_name = city_name
        MINE.var_desc = '0 means not mine, 1 means all mine, inbetween is partial'

        fractional = True
        for j, i in np.ndindex(gf.NROWS, gf.NCOLS):
            if fractional:
                gpoly = Polygon([
                    [LOND[j + 0, i + 0], LATD[j + 0, i + 0]],
                    [LOND[j + 0, i + 1], LATD[j + 0, i + 1]],
                    [LOND[j + 1, i + 1], LATD[j + 1, i + 1]],
                    [LOND[j + 1, i + 0], LATD[j + 1, i + 0]],
                    [LOND[j + 0, i + 0], LATD[j + 0, i + 0]],
                ])
                if puberpoly.intersects(gpoly):
                    intx = gpoly.intersection(uberpoly)
                    farea = intx.area / gpoly.area
                    MINE[0, 0, j, i] = farea
            else:
                gp = Point(LON[j, i], LAT[j, i])
                if puberpoly.contains(gp):
                    if uberpoly.contains(gp):
                        MINE[0, 0, j, i] = 1

    # # Get rid of initial DUMMY variable
    del outf.variables['DUMMY']
    # Remove VAR-LIST so that it can be inferred
    delattr(outf, 'VAR-LIST')
    outf.updatemeta()

    outf.variables['TFLAG'][:] = 0
    outf.SDATE = -635
    savedf = outf.save(output_name, verbose=0, complevel=1)
    savedf.close()


def main_rename_original_pollutant(tbl_name, input_dir, output_dir):
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
    import glob
    import tqdm
    import numpy as np
    import shutil
    # --------------------------------------------------------------------------------------------------------

    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)

    files = glob.glob(f"{input_dir}/*.tiff")

    for file in tqdm.tqdm(files):
        sub_name = encode_title_tiff(os.path.basename(file))
        label = sub_name["label"]
        year = sub_name["year"]
        month = sub_name["month"]
        sector = sub_name["sector"]
        pollutant = sub_name["pollutant"]

        try:
            pos = np.where(np.array(tbl_name["org"]) == pollutant)[0][0]
        except IndexError:
            shutil.copy(file, f"{output_dir}/{os.path.basename(file)}")
            continue

        new_name = tbl_name["new"][pos]

        new_file_name = f"{label}_{year}_{month}__{sector}__{new_name}.tiff"
        output_path = f"{output_dir}/{new_file_name}"
        shutil.copy(file, output_path)


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
    output_name = f"output/{target_mechanism}_{sector}_{grid_name}_{yyyymmdd}.nc"
    tmpf.save(output_name, format="NETCDF3_CLASSIC")


def create_gridinfo(small_grid, big_grid, out_path, max_id):
    # --------------------------------------------------------------------------------------------------------
    import geopandas as gpd
    import numpy as np
    import glob
    # --------------------------------------------------------------------------------------------------------
    # 删除文件夹下的输出文件
    try:
        os.remove(f'{out_path}/cmaq_grid.csv')
        os.remove(f'{out_path}/cmaq_intersect.csv')
        # current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # print(f'{current_time}: 输出目录已完成清理，开始进行网格信息核算。')
    except:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # print(f'{current_time} 输出目录已完成清理，开始进行网格信息核算。')

    out_feature_class = f'{out_path}\cmaq_intersect.shp'
    gdf_smallgrid = gpd.read_file(small_grid).to_crs(epsg=4326)
    gdf_biggrid = gpd.read_file(big_grid).to_crs(gdf_smallgrid.crs)
    intersect_out = gpd.overlay(gdf_smallgrid, gdf_biggrid,how='intersection')
    intersect_out.to_file(out_feature_class)
    gdf = gpd.read_file(small_grid)
    out_name = 'cmaq_grid.csv'
    gdf.to_csv(f'{out_path}/{out_name}', index=False)

    # 获取经纬度
    df = pd.read_csv(f'{out_path}/{out_name}')
    df_lon = df['LON'].values
    df_lat = df['LAT'].values

    # max_id = df['ID'].values.max()
    gdf = gpd.read_file(out_feature_class)
    gdf = gdf.to_crs(epsg=4547)
    gdf['square'] = gdf.geometry.area / 1e6
    gdf.to_csv(f'{out_path}/cmaq_intersect.csv', index=False)

    # 此代码块则为删除面积占比较小的属性条
    df = pd.read_csv(f'{out_path}/cmaq_intersect.csv')
    df_ids = df['ID'].values
    df_area = df['square'].values

    del_list = []
    # Delete the min value.
    for temp_id in range(int(max_id)+1):
        if df_ids.__contains__(temp_id):
            pos_in_df = np.where(df_ids == temp_id)[0]
            temp_area = df_area[pos_in_df]
            pos_in_temp = np.where(temp_area != temp_area.max())[0]
            if len(pos_in_temp) != 0:
                pos = pos_in_df[pos_in_temp]
                for temp_pos in pos:
                    del_list.append(temp_pos)
        else:
            unknown_gird = pd.DataFrame({'ID': temp_id,
                                         'NAME': 'unknown',
                                         'LON': df_lon[temp_id-1],
                                         'LAT': df_lat[temp_id-1]},
                                        index=[0])
            df = df.append(unknown_gird, ignore_index=True)

    df = df.drop(del_list)
    df = df.drop_duplicates(['ID'])
    df.sort_values("ID", inplace=True)
    df.to_csv(f'{out_path}/grid_info.csv', index=False)

    # 删除临时文件

    file_list = glob.glob(f'{out_path}/cmaq_intersect.*')
    for file in file_list:
        os.remove(file)

    file_list = glob.glob(f'{out_path}/cmaq_grid.*')
    for file in file_list:
        os.remove(file)


# -------------------------------------------------------------------
# 空间分配因子计算-道路分配
# -------------------------------------------------------------------
def road_allocation(road_class_list, road_dir, small_grid, big_grid, grid_info, out_path):
    # -------------------------------------------------------------------
    import numpy as np
    import geopandas as gpd
    from shapely.geometry import box
    import glob
    # -------------------------------------------------------------------
    # out_path = r'E:\chengdu\分配因子'  # 设置输出目录路径

    # -------------------------------------------------------------------
    # 空间分配因子计算-道路分配
    # -------------------------------------------------------------------
    for road_class in road_class_list:

        road_file = fr'{road_dir}\{road_class}'  # 设置用于分配的线数据路径
        # print(f'-> 当前处理数据 【 {road_file} 】')
        out_csv_shp_name = f'EF_{road_class}'  # 设置输出的文件名称

        try:
            os.remove(f'{out_path}/Big_grid_road.csv')
            os.remove(f'{out_path}/Small_grid_road.csv')
        except:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        gdf_road = gpd.read_file(road_file)

        # 获取smallgrid的边界box
        gdf_clip_grid = gpd.read_file(small_grid).to_crs(gdf_road.crs)
        clip_bounds = gdf_clip_grid.total_bounds  # 获取grid的边界，用于获得裁剪roadshp的box
        clip_box = box(clip_bounds[0], clip_bounds[1], clip_bounds[2], clip_bounds[3])
        box_gdf = gpd.GeoDataFrame(geometry=[clip_box], crs=gdf_clip_grid.crs)  # 将box转化为gdf

        # 计算大网格中的道路总长
        # Clip
        clipped_big_grid = f'{out_path}/Big_grid_cliped.shp'
        clip_out = gpd.overlay(box_gdf, gpd.read_file(big_grid).to_crs(gdf_road.crs), how='intersection')
        clip_out.to_file(clipped_big_grid)

        out_feature_class = f'{out_path}/Big_grid_road.shp'
        clip_big_grid = gpd.read_file(clipped_big_grid).to_crs(gdf_road.crs)
        gdf_road_clip = gpd.overlay(gdf_road, box_gdf,how='intersection') # 先用gird边界的box进行裁剪，再进行裁剪，以提高运行速度，通常进行空间分配的fine domian都较小
        intersect_out = gpd.overlay(gdf_road_clip, clip_big_grid, how='intersection')
        intersect_out.to_file(out_feature_class)

        gdf = gpd.read_file(out_feature_class)
        gdf = gdf.to_crs(epsg=4547)  #4547
        gdf = gdf.explode()
        gdf['Length_m'] = gdf.geometry.length
        result = gdf.groupby('NAME', as_index=False)['Length_m'].sum()
        MULTILINESTRING_combine = pd.merge(result, gdf[['NAME']].drop_duplicates(), on='NAME')
        MULTILINESTRING_combine.to_csv(f'{out_path}/Big_grid_road.csv', index=False)

        temp_big_grid_sst = pd.read_csv(f'{out_path}/Big_grid_road.csv')
        name_list = np.unique(temp_big_grid_sst['NAME'])
        length_list = []
        for temp_area in name_list:
                temp_length = temp_big_grid_sst[temp_big_grid_sst['NAME'].isin([temp_area])]['Length_m'].values.sum()
                length_list.append(temp_length)
        big_grid_sst = pd.DataFrame(columns=['NAME', 'LENGTH'])
        big_grid_sst['NAME'] = name_list
        big_grid_sst['LENGTH'] = length_list

        # 计算小网格中的道路总长
        out_feature_class = f'{out_path}/Small_grid_road.shp'
        clip_small_out = gpd.overlay(gdf_road_clip, gpd.read_file(small_grid).to_crs(gdf_road.crs),
                                     how='intersection')
        clip_small_out.to_file(out_feature_class)

        gdf = gpd.read_file(out_feature_class)
        gdf = gdf.to_crs(epsg=4547)  #
        gdf['Length_m'] = gdf.geometry.length
        gdf.to_csv(f'{out_path}/Small_grid_road.csv', index=False)

        temp_small_grid_sst = pd.read_csv(f'{out_path}/Small_grid_road.csv')
        id_list = np.unique(temp_small_grid_sst['ID'])
        length_list = []
        for temp_id in id_list:
            temp_length = temp_small_grid_sst[temp_small_grid_sst['ID'].isin([temp_id])]['Length_m'].values.sum()
            length_list.append(temp_length)
        small_grid_sst = pd.DataFrame(columns=['ID', 'LENGTH'])
        small_grid_sst['ID'] = id_list
        small_grid_sst['LENGTH'] = length_list

        df = pd.read_csv(grid_info)
        result = pd.DataFrame(columns=['ID', 'LON', 'LAT', 'AREA', 'EF'])
        ef_list = []
        id_list = []
        area_list = []
        lon_list = []
        lat_list = []
        for temp_id, temp_area, temp_lon, temp_lat in zip(df['ID'].values, df['NAME'].values, df['LON'].values,
                                                          df['LAT'].values):

            if temp_area == 'unknown':
                temp_ef = 0.0

                ef_list.append(temp_ef)
                id_list.append(temp_id)
                area_list.append(temp_area)
                lon_list.append(temp_lon)
                lat_list.append(temp_lat)
                continue

            #     print(temp_area)
            if small_grid_sst['ID'].values.__contains__(temp_id):
                temp_length = small_grid_sst[small_grid_sst['ID'].isin([temp_id])]['LENGTH'].values[0]
                try:
                    temp_total_length = big_grid_sst[big_grid_sst['NAME'].isin([temp_area])]['LENGTH'].values[0]
                    temp_ef = temp_length / temp_total_length
                except:
                    temp_ef = 0.0
            else:
                temp_ef = 0.0

            ef_list.append(temp_ef)
            id_list.append(temp_id)
            area_list.append(temp_area)
            lon_list.append(temp_lon)
            lat_list.append(temp_lat)

        result['ID'] = id_list
        result['LON'] = lon_list
        result['LAT'] = lat_list
        result['AREA'] = area_list
        result['EF'] = ef_list

        out_name = f'{out_csv_shp_name}.csv'
        result_csv_path = f'{out_path}/{out_name}'
        result.to_csv(result_csv_path, index=False)

    # 删除临时文件
    file_list = glob.glob(f'{out_path}/Big_grid_cliped.*')
    for file in file_list:
        os.remove(file)

    file_list = glob.glob(f'{out_path}/Big_grid_road.*')
    for file in file_list:
        os.remove(file)

    file_list = glob.glob(f'{out_path}/Small_grid_road.*')
    for file in file_list:
        os.remove(file)


def road_deal(ef_files, ef_factors, output_name):
    # -------------------------------------------------------------------
    # import pandas as pd
    # -------------------------------------------------------------------
    result_ef = pd.read_csv(ef_files[0])['EF'] * 0
    for ef_file, ef_factor in zip(ef_files, ef_factors):
        file_0 = pd.read_csv(ef_file)['EF']
        result_ef += file_0 * ef_factor
    df = pd.read_csv(ef_files[0])
    df['EF'] = result_ef
    df.to_csv(output_name, index=False)

def raster_allocation(raster_file, small_grid, big_grid, grid_info, out_path, result_csv_path_name):
    # -------------------------------------------------------------------
    # import pandas as pd
    import glob
    import geopandas as gpd
    import rasterstats
    from shapely.geometry import box
    # -------------------------------------------------------------------
    try:
        os.remove(f'{out_path}/Big_grid_zonalstattblout.csv')
        os.remove(f'{out_path}/Small_grid_zonalstattblout.csv')
    except:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 获取smallgrid的box边界用于clip
    gdf_clip_grid = gpd.read_file(small_grid).to_crs(epsg=4326)
    clip_bounds = gdf_clip_grid.total_bounds  # 获取grid的边界，用于获得裁剪roadshp的box
    clip_box = box(clip_bounds[0], clip_bounds[1], clip_bounds[2], clip_bounds[3])
    box_gdf = gpd.GeoDataFrame(geometry=[clip_box], crs=gdf_clip_grid.crs)  # 将box转化为gdf

    clipped_big_grid = f'{out_path}/Big_grid_cliped.shp'
    clip_out = gpd.overlay(box_gdf, gpd.read_file(big_grid).to_crs(epsg=4326), how='intersection')
    clip_out.to_file(clipped_big_grid)

    outZSaT = rasterstats.zonal_stats(clipped_big_grid, raster_file, stats="sum", geojson_out=True, nodata=-999)
    result = gpd.GeoDataFrame.from_features(outZSaT)
    result = result.rename(columns={'sum': 'SUM'})
    out_name = 'Big_grid_zonalstattblout.csv'
    result.to_csv(f'{out_path}/{out_name}', index=False)

    gdf_small_grid = gpd.read_file(small_grid).to_crs(epsg=4326)
    outZSaT = rasterstats.zonal_stats(gdf_small_grid, raster_file, stats="sum", geojson_out=True, nodata=-999)
    result = gpd.GeoDataFrame.from_features(outZSaT)
    result = result.rename(columns={'sum': 'SUM'})
    out_name = 'Small_grid_zonalstattblout.csv'
    result.to_csv(f'{out_path}/{out_name}', index=False)

    df = pd.read_csv(grid_info)
    big_grid_zstt = pd.read_csv(f'{out_path}\Big_grid_zonalstattblout.csv')
    small_grid_zstt = pd.read_csv(f'{out_path}\Small_grid_zonalstattblout.csv')
    ef_list = []
    id_list = []
    area_list = []
    lon_list = []
    lat_list = []
    for temp_id, temp_area, temp_lon, temp_lat in zip(df['ID'].values, df['NAME'].values, df['LON'].values,
                                                      df['LAT'].values):
        if temp_area == 'unknown':
            temp_ef = 0.0

            ef_list.append(temp_ef)
            id_list.append(temp_id)
            area_list.append(temp_area)
            lon_list.append(temp_lon)
            lat_list.append(temp_lat)
            continue

        try:
            temp_big_grid_length = big_grid_zstt[big_grid_zstt['NAME'].isin([temp_area])]['SUM'].values[0]
        except:
            temp_big_grid_length = 0.0

        if temp_big_grid_length == 0.0:
            temp_ef = 0.0

            ef_list.append(temp_ef)
            id_list.append(temp_id)
            area_list.append(temp_area)
            lon_list.append(temp_lon)
            lat_list.append(temp_lat)
            continue
        try:
            temp_small_grid_length = small_grid_zstt[small_grid_zstt['ID'].isin([temp_id])]['SUM'].values[0]
            # temp_big_grid_length = big_grid_zstt[big_grid_zstt['NAME'].isin([temp_area])]['SUM'].values[0]
            temp_ef = temp_small_grid_length / temp_big_grid_length
        except:
            temp_ef = 0.0

        ef_list.append(temp_ef)
        id_list.append(temp_id)
        area_list.append(temp_area)
        lon_list.append(temp_lon)
        lat_list.append(temp_lat)

    result = pd.DataFrame(columns=['ID', 'LON', 'LAT', 'AREA', 'EF'])
    result['ID'] = id_list
    result['LON'] = lon_list
    result['LAT'] = lat_list
    result['AREA'] = area_list
    result['EF'] = ef_list

    result_csv_path = f'{out_path}/{result_csv_path_name}.csv'
    result.to_csv(result_csv_path, index=False)

    file_list = glob.glob(f'{out_path}/Big_grid_cliped.*')
    for file in file_list:
        os.remove(file)

    file_list = glob.glob(f'{out_path}/Big_grid_zonalstattblout.*')
    for file in file_list:
        os.remove(file)

    file_list = glob.glob(f'{out_path}/Small_grid_zonalstattblout.*')
    for file in file_list:
        os.remove(file)


def split_file_extension(filebasename):
    filename, file_extension = os.path.splitext(filebasename)
    return filename, file_extension


def zoning_statistics(small_grid, big_grid, raster_dir, out_path, mm):

    import glob
    import geopandas as gpd
    import rasterstats
    from shapely.geometry import box
    import tqdm
    # Use half of the cores on the machine

    if os.path.exists(out_path) is False:
        os.mkdir(out_path)

    # 获取smallgrid的边界box
    gdf_clip_grid = gpd.read_file(small_grid).to_crs(epsg=4326)
    clip_bounds = gdf_clip_grid.total_bounds  # 获取grid的边界，用于获得裁剪roadshp的box
    clip_box = box(clip_bounds[0], clip_bounds[1], clip_bounds[2], clip_bounds[3])
    box_gdf = gpd.GeoDataFrame(geometry=[clip_box], crs=gdf_clip_grid.crs)  # 将box转化为gdf

    out_feature_class = f'{out_path}/Clipped.shp'
    clip_out = gpd.overlay(box_gdf, gpd.read_file(big_grid).to_crs(epsg=4326), how='intersection')
    clip_out.to_file(out_feature_class)

    file_list = glob.glob(f'{raster_dir}/*_*_{mm}__*__*.tiff')
    if len(file_list) == 0:
        exit(f"ERROR: There is no file in the directory: {raster_dir}")

    mid_out_list = []
    for file in tqdm.tqdm(file_list, desc=f"{time_format()}Processing for month {mm}"):
        # out_name = os.path.basename(file).split(".")[0]
        sub_name = os.path.basename(file)
        out_name, file_extension = split_file_extension(sub_name)

        # 判断文件是否存在，如果存在则直接跳过。
        if os.path.exists(f'{out_path}/{out_name}.csv'):
            continue
        try:
            outZSaT = rasterstats.zonal_stats(out_feature_class, file, stats="sum", geojson_out=True, nodata=-999)
            result = gpd.GeoDataFrame.from_features(outZSaT)
            result = result[result['sum'].notnull()] # 删除没有算出EF的部分
            result = result.rename(columns={'sum': 'SUM'})
            result.to_csv(f'{out_path}/{out_name}.csv', index=False)
            mid_out_list.append(f'{out_path}/{out_name}.csv')
        except :
            exit(f"ERROR: Please double check the file : {file}")

    # 删除多余文件
    file_list = glob.glob(f'{out_path}/*.cpg')
    for file in file_list:
        os.remove(file)

    file_list = glob.glob(f'{out_path}/*.xml')
    for file in file_list:
        os.remove(file)

    file_list = glob.glob(f'{out_path}/*.dbf')
    for file in file_list:
        os.remove(file)

    file_list = glob.glob(f'{out_path}/Clipped.*')
    for file in file_list:
        os.remove(file)


def draw_modle_grid(griddesc_file):
    import pyioapi
    import geopandas as gpd
    from shapely.geometry import Polygon
    import pyproj
    # import pandas as pd
    # 读入GRIDDESC文件
    griddesc = pyioapi.GRIDDESC(griddesc_file)
    # 获取网格参数
    grid = griddesc.get_grid(list(griddesc.grids)[0])
    # 获取坐标系参数
    coord = griddesc.get_coord(list(griddesc.coords)[0])
    # 根据网格和坐标系名设置输出名
    outshp_name = list(griddesc.coords)[0] + "_" + list(griddesc.grids)[0]

    # 初始化起始格网四角范围
    ringXleftOrigin = grid.XORIG
    ringXrightOrigin = ringXleftOrigin + grid.XCELL
    ringYbottomOrigin = grid.YORIG
    ringYtopOrigin = ringYbottomOrigin + grid.YCELL

    # 遍历列，每一列写入格网
    col = 1
    idd_num = 1
    grids_list = []  # 用于存储生成的各个网格
    while col <= grid.NCOLS:
        # 初始化，每一列写入完成都把上下范围初始化
        ringYtop = ringYtopOrigin
        ringYbottom = ringYbottomOrigin
        # 遍历行，对这一列每一行格子创建和写入
        row = 1
        while row <= grid.NROWS:
            # 创建左下角第一个格子
            ring = Polygon([(ringXleftOrigin, ringYbottom),
                            (ringXleftOrigin, ringYtop),
                            (ringXrightOrigin, ringYtop),
                            (ringXrightOrigin, ringYbottom)])
            # 写入几何多边形
            geo_df = gpd.GeoDataFrame(data=[[str(idd_num-1), row-1, col-1]],
                                      geometry=[ring],
                                      columns=['ID', 'rownum', 'colnum'])
            grids_list.append(geo_df)

            # 下一多边形，更新上下范围
            row += 1
            ringYtop = ringYtop + grid.YCELL
            ringYbottom = ringYbottom + grid.YCELL

            idd_num += 1
        # 一列写入完成后，下一列，更新左右范围
        col += 1
        ringXleftOrigin = ringXleftOrigin + grid.XCELL
        ringXrightOrigin = ringXrightOrigin + grid.XCELL
    # 合并列表中的网格
    gdf_fishgrid = pd.concat(grids_list)

    # 使用GRIDDESC的参数设置网格投影
    wrf_proj = pyproj.Proj('+proj=lcc ' + '+lon_0=' + str(coord.XCENT) + ' lat_0=' + str(coord.YCENT)
                           + ' +lat_1=' + str(coord.P_ALP) + ' +lat_2=' + str(coord.P_BET))
    # 设置网格投影
    gdf_fishgrid.crs = wrf_proj.crs
    # 输出模型网格shp文件
    gdf_fishgrid.to_file('output/shapefile-grid.shp',
                         driver='ESRI Shapefile',
                         encoding='utf-8')


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
