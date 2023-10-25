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


