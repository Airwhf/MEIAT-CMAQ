import os
import PseudoNetCDF as pnc
import geopandas as gpd
import pandas as pd
import numpy as np
import glob
import time
import glob
import tqdm
import datetime
import pyioapi
from shapely.geometry import Polygon
import pyproj
import re


import arcpy
from arcpy.sa import ZonalStatisticsAsTable
import arcgisscripting

# Use half of the cores on the machine
arcpy.env.parallelProcessingFactor = "50%"
arcpy.env.overwriteOutput = True


os.environ["IOAPI_ISPH"] = "6370000."


def time_format():
    return f'{datetime.datetime.now()}|> '


def draw_modle_grid(griddesc_file, output_dir):
    
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
    outf = f'{output_dir}/shapefile-grid.shp'
    gdf_fishgrid.to_file(outf,
                         driver='ESRI Shapefile',
                         encoding='utf-8')


def create_gridinfo(small_grid, big_grid, out_path, max_id):
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
    in_features = [small_grid, big_grid]
    arcpy.analysis.Intersect(in_features, out_feature_class, "ALL")
    out_name = 'cmaq_grid.csv'
    arcpy.conversion.TableToTable(small_grid, out_path, out_name)

    # 获取经纬度
    df = pd.read_csv(f'{out_path}/{out_name}')
    df_lon = df['LON'].values
    df_lat = df['LAT'].values

    # max_id = df['ID'].values.max()
    arcpy.CalculateGeometryAttributes_management(out_feature_class, [['square', 'AREA']], area_unit='SQUARE_KILOMETERS')
    out_name = 'cmaq_intersect.csv'
    arcpy.conversion.TableToTable(out_feature_class, out_path, out_name)

    # 此代码块则为删除面积占比较小的属性条
    df = pd.read_csv(f'{out_path}/{out_name}')
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

    file = f'{out_path}/schema.ini'
    os.remove(file)


def road_allocation(road_class_list, road_dir, small_grid, big_grid, grid_info, out_path):
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

        # 计算大网格中的道路总长
        # Clip
        clipped_big_grid = f'{out_path}/Big_grid_cliped.shp'
        arcpy.Clip_analysis(big_grid, small_grid, clipped_big_grid)
        out_feature_class = f'{out_path}/Big_grid_road.shp'
        in_features = [road_file, clipped_big_grid]
        arcpy.analysis.Intersect(in_features, out_feature_class, "ALL")

        arcpy.CalculateGeometryAttributes_management(out_feature_class, [["Length_m", "LENGTH_GEODESIC"],], "METERS")
        out_statistic_table = f'{out_feature_class[0:-4]}.dbf'
        out_name = 'Big_grid_road.csv'
        arcpy.conversion.TableToTable(out_statistic_table, out_path, out_name)
        temp_big_grid_sst = pd.read_csv(f'{out_path}/{out_name}')

        name_list = np.unique(temp_big_grid_sst['NAME'])
        length_list = []
        for temp_area in name_list:
                temp_length = temp_big_grid_sst[temp_big_grid_sst['NAME'].isin([temp_area])]['Length_m'].values.sum()
                length_list.append(temp_length)
        big_grid_sst = pd.DataFrame(columns=['NAME', 'LENGTH'])
        big_grid_sst['NAME'] = name_list
        big_grid_sst['LENGTH'] = length_list

        # 计算小网格中的道路总长
        in_features = [road_file, small_grid]
        out_feature_class = f'{out_path}/Small_grid_road.shp'
        arcpy.analysis.Intersect(in_features, out_feature_class, "ALL")

        arcpy.CalculateGeometryAttributes_management(out_feature_class, [["Length_m", "LENGTH_GEODESIC"], ], "METERS")
        out_statistic_table = f'{out_feature_class[0:-4]}.dbf'
        out_name = 'Small_grid_road.csv'
        arcpy.conversion.TableToTable(out_statistic_table, out_path, out_name)

        temp_small_grid_sst = pd.read_csv(f'{out_path}/{out_name}')
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

    file = f'{out_path}/schema.ini'
    os.remove(file)


def raster_allocation(raster_file, small_grid, big_grid, grid_info, out_path, result_csv_path_name):
    try:
        os.remove(f'{out_path}/Big_grid_zonalstattblout.csv')
        os.remove(f'{out_path}/Small_grid_zonalstattblout.csv')
    except:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


    # Clip
    clipped_big_grid = f'{out_path}\Big_grid_cliped.shp'
    arcpy.Clip_analysis(big_grid, small_grid, clipped_big_grid)
    # statistic
    out_statistic_table = f'{out_path}\Big_grid_zonalstattblout.dbf'
    outZSaT = ZonalStatisticsAsTable(clipped_big_grid, "NAME", raster_file, out_statistic_table, statistics_type="SUM")
    out_name = 'Big_grid_zonalstattblout.csv'
    arcpy.conversion.TableToTable(out_statistic_table, out_path, out_name)

    # statistic
    out_statistic_table = f'{out_path}\Small_grid_zonalstattblout.dbf'
    outZSaT = ZonalStatisticsAsTable(small_grid, "ID", raster_file, out_statistic_table, statistics_type="SUM")
    out_name = 'Small_grid_zonalstattblout.csv'
    arcpy.conversion.TableToTable(out_statistic_table, out_path, out_name)

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

    file = f'{out_path}/schema.ini'
    os.remove(file)


def road_deal(ef_files, ef_factors, output_name):
    result_ef = pd.read_csv(ef_files[0])['EF'] * 0
    for ef_file, ef_factor in zip(ef_files, ef_factors):
        file_0 = pd.read_csv(ef_file)['EF']
        result_ef += file_0 * ef_factor
    df = pd.read_csv(ef_files[0])
    df['EF'] = result_ef
    df.to_csv(output_name, index=False)


def zoning_statistics(small_grid, big_grid, raster_dir, out_path, mm):
    if os.path.exists(out_path) is False:
        os.mkdir(out_path)

    in_features = big_grid
    clip_features = small_grid
    out_feature_class = f'{out_path}/Clipped.shp'
    arcpy.analysis.Clip(in_features, clip_features, out_feature_class)

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
            outZSaT = ZonalStatisticsAsTable(out_feature_class, "NAME", file, f"{out_path}/{out_name}.dbf", statistics_type="SUM")
            arcpy.conversion.TableToTable(outZSaT, out_path, f'{out_name}.csv')
            mid_out_list.append(f'{out_path}/{out_name}.csv')
        except arcgisscripting.ExecuteError:
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


def split_file_extension(filebasename):
    filename, file_extension = os.path.splitext(filebasename)
    return filename, file_extension


def encode_title(file_name):
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


def create_source(label, year, mm, development_list, emission_factor_dir, emission_data_dir, out_path):
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


def main_coarse2fine(griddesc_file, griddesc_name, big_grid, allocator_types, allocators, sectors, geotiff_dir, start_date, end_date, 
                     inventory_label, inventory_year,
                     line_files=None, 
                     line_factors=None,
                     control_create_grid=True, 
                     control_grid_info=True, 
                     control_create_factor=True, control_coarse_emis=True, control_create_source=True):
    # --------------------------------------------------------------------------------------------------------
    path = os.getcwd()
    # --------------------------------------------------------------------------------------------------------
    output_dir = f"{path}/model_emission_{griddesc_name}"
    # if os.path.exists(output_dir) is False:
    #     os.mkdir(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # --------------------------------------------------------------------------------------------------------
    # example = f90nml.read("namelist.input")
    # griddesc_file = example["global"]["griddesc_file"]
    # griddesc_name = example["global"]["griddesc_name"]

    # --------------------------------------------------------------------------------------------------------
    # control_create_grid = example["control"]["create_grid"]
    print(f"--------------Fine grid shapefile|> {output_dir}/shapefile-grid.shp--------------")
    if control_create_grid:
        print(f'{time_format()}The control of create grid is {control_create_grid} and processor start creating fine grid.')
        draw_modle_grid(griddesc_file, output_dir)
        gf = pnc.pncopen(griddesc_file, GDNAM=griddesc_name, format="griddesc", SDATE=2023001, TSTEP=10000, withcf=False)
        gpdf = gpd.read_file(f"{output_dir}/shapefile-grid.shp")
        lon, lat = gf.ij2ll(gpdf["colnum"].values, gpdf["rownum"].values)
        gpdf["LON"] = lon
        gpdf["LAT"] = lat
        gpdf.to_file(f'{output_dir}/shapefile-grid.shp', driver='ESRI Shapefile', encoding='utf-8')
        gpdf[["ID", "colnum", "rownum", "LON", "LAT"]].to_csv(f"{output_dir}/shapefile-grid.csv")
        print(f'{time_format()}Finish creating fine grid shapefile.')
    # else:
    #     print(f"{time_format()}The control of create grid is {control_create_grid}.")
    #     if os.path.exists(f"{output_dir}/shapefile-grid.shp"):
    #         print(f"{time_format()}There is fine grid shapefile and processor will continue.")
    #     else:
    #         print(f"{time_format()}There is not fine grid shapefile and processor will exit.")
    #         exit()

    # --------------------------------------------------------------------------------------------------------
    small_grid = f"{output_dir}/shapefile-grid.shp"
    # big_grid = example["global"]["big_grid_file"]
    # control_grid_info = example["control"]["grid_info"]
    grid_info_out_path = output_dir
    print(f"-----------------Grid information|> {grid_info_out_path}/grid_info.csv--------------")
    if control_grid_info:
        print(f'{time_format()}The control of grid information is {control_grid_info} and processor start for grid information.')
        os.makedirs(grid_info_out_path, exist_ok=True)
        max_id = pd.read_csv(f"{output_dir}/shapefile-grid.csv")["ID"].values.max()
        create_gridinfo(small_grid, big_grid, grid_info_out_path, max_id)
        grid_info_path = f'{grid_info_out_path}/grid_info.csv'
        print(f'{time_format()}Finish creating grid information.')
    # else:
    #     print(f"{time_format()}The control of grid information is {control_grid_info}.")
    #     if os.path.exists(f'{grid_info_out_path}/grid_info.csv'):
    #         print(f"{time_format()}There is grid information and processor will continue.")
    #     else:
    #         print(f"{time_format()}There is not grid information and processor will exit.")
    #         exit()

    # --------------------------------------------------------------------------------------------------------
    ef_out_path = f'{output_dir}/factor'
    grid_info_path = f'{grid_info_out_path}/grid_info.csv'
    os.makedirs(ef_out_path, exist_ok=True)
    print(f"----------------Allocation factor|> {ef_out_path}--------------")
    # 读取分配因子类型 分配因子路径 分配部门
    # allocator_types = example["global"]["allocator_type"]
    # if type(allocator_types) != type(["list"]):
    #     allocator_types = [allocator_types]
    # allocators = example["global"]["allocator"]
    # if type(allocators) != type(["list"]):
    #     allocators = [allocators]
    # sectors = example["global"]["sectors"]
    # if type(sectors) != type(["list"]):
    #     sectors = [sectors]

    if control_create_factor:
        print(f'{time_format()}The control of allocation factor is {control_create_factor} and processor start for allocation factor.')
        for allocator_type, allocator, sector in zip(allocator_types, allocators, sectors):
            # # 判断数据是否已经存在，如果存在就直接跳过。
            # if os.path.exists(f'{ef_out_path}/EF_{sector}.csv'):
            #     print(f"{time_format()}There is {ef_out_path}/EF_{sector}.csv and processor will skip this loop.")
            #     continue
            print(f"{time_format()}There is the process for {sector} and the allocator type is {allocator_type}.")
            if allocator_type == "line":
                road_dir = f"{path}/allocator"
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
    # control_coarse_emis = example["control"]["coarse_emission"]
    print(f"----------------Coarse Emission|> f'{output_dir}/zoning_statistics'--------------")
    if control_coarse_emis:
        print(f'{time_format()}The control of coarse emission is {control_coarse_emis} and processor start for coarse emission.')
        meic_zoning_out = f'{output_dir}/zoning_statistics'
        os.makedirs(meic_zoning_out, exist_ok=True)
        # geotiff_dir = example["global"]["geotiff_dir"]
        # start_date = pd.to_datetime(example["global"]["start_date"])
        # end_date = pd.to_datetime(example["global"]["end_date"])
        date_list = pd.date_range(start_date, end_date)
        mms = np.unique(np.array([temp_date.strftime("%m") for temp_date in date_list]))
        for mm in mms:
            zoning_statistics(small_grid, big_grid, geotiff_dir, meic_zoning_out, mm)
    else:
        print(f"{time_format()}The control of coarse emission is {control_coarse_emis}.")

    # --------------------------------------------------------------------------------------------------------
    meic_zoning_out = f'{output_dir}/zoning_statistics'
    # control_create_source = example["control"]["create_source"]
    source_out_dir = f'{output_dir}/source'
    if os.path.exists(source_out_dir) is False:
        os.mkdir(source_out_dir)
    print(f"----------------Coarse Emission|> f'{output_dir}/source'--------------")
    if control_create_source:
        date_list = pd.date_range(start_date, end_date)
        mms = np.unique(np.array([temp_date.strftime("%m") for temp_date in date_list]))
        for mm in mms:
            print(f"Processing for month {mm}.")
            # inventory_label = example["global"]["inventory_label"]
            # inventory_year = example["global"]["inventory_year"]
            create_source(inventory_label, inventory_year, mm, sectors, ef_out_path, meic_zoning_out, source_out_dir)
            print(f'{time_format()}The control of create source is {control_create_source} and processor start for coarse emission.')
        else:
            print(
                f'{time_format()}The control of create source is {control_create_source}.')

    # --------------------------------------------------------------------------------------------------------
    print('# ------------------------------------' + 'End' + '------------------------------------ #')
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(f"The program end time ：{current_time}")
    print('# ------------------------------------' + '---' + '------------------------------------ #')


def create_emission_file(
        grid_dir,
        emission_date,
        grid_desc,
        grid_name,
        label,
        sector,
        inventory_year,
        inventory_mechanism,
        target_mechanism):
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
    source_file = f"{grid_dir}/source/source-{label}-{sector}-{inventory_year}-{mm}.csv"
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
    output_name = f"{grid_dir}/{target_mechanism}_{sector}_{grid_name}_{yyyymmdd}.nc"
    tmpf.save(output_name, format="NETCDF3_CLASSIC")


if __name__ == '__main__':

    # ========================================================================================
    # Set GRIDDESC configuration.
    griddesc_file = 'input/GRIDDESC.PRD274x181'
    griddesc_name = 'PRD274x181'    
    
    # Set the coarse grid path.
    big_grid = 'shapefile/MEIC-0P25.shp'
    
    # Set allocator.
    allocator_types = ['raster', 'raster', 'raster', 'raster', 'line']
    allocators = ['landscan-global-2017_nodata.tif', 'power.tif', 'industry.tif', 'agriculture.tif', 'line']
    sectors = ['residential', 'power', 'industry', 'agriculture', 'transportation']
    
    line_files = ["motorway.shp", "primary.shp", "residential.shp", "secondary.shp"]
    line_factors = [0.435798, 0.326848, 0.081712, 0.155642]
    
    # Set the inventory with Geotiff format.
    geotiff_dir = r'F:\data\Emission\MEICv1.3\CB05-2017'  
    
    # Set the inventory.
    inventory_label = 'MEIC'
    inventory_year = 2017  
    
    # Set the inventory period.
    start_date = '2017-01-01'
    end_date = '2017-01-02'
    
    # Species allocation.
    inventory_mechanism = 'MEIC-CB05'
    target_mechanism = 'CB06'
    # ========================================================================================
    # Spatial allocation.
    # ========================================================================================
    start_time = time.time()
    
    main_coarse2fine(griddesc_file, griddesc_name, big_grid, allocator_types, allocators, sectors, geotiff_dir, start_date, end_date, 
                     inventory_label, inventory_year, line_files=line_files, line_factors=line_factors)
    
    # ========================================================================================
    # Create CMAQ emission files (temporal and species allocation).
    # ========================================================================================
    source_dir = f'model_emission_{griddesc_name}'
    periods = pd.period_range(pd.to_datetime(start_date), pd.to_datetime(end_date), freq='D')
    for sector in sectors:
        for emission_date in periods:
            create_emission_file(source_dir, str(emission_date), griddesc_file, griddesc_name, inventory_label, sector, inventory_year,
                                 inventory_mechanism, target_mechanism)
            print(f"Finish: {str(emission_date)} {sector}")
            
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")
