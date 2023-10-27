import os
import pandas as pd
import datetime
import PseudoNetCDF as pnc
import numpy as np
import glob
import re
import rioxarray as rxr

os.environ["IOAPI_ISPH"] = "6370000."
# Ignore the warning information from pandas.
pd.options.mode.chained_assignment = None


def read_tiff(file, shapefactor=2):
    """

    :param file: The file path of GeoTIFF.
    :return: value, longitude, latitude.
    """
    dataset = rxr.open_rasterio(file)
    longitude = dataset.coords["x"].values
    latitude = dataset.coords["y"].values
    # lons, lats = np.meshgrid(longitude, latitude)
    value = dataset[0, ...].values
    # Update the shape factor on 27/10/2023 by Haofan.
    new_shape = (value.shape[0]*shapefactor, value.shape[1]*shapefactor)
    value = np.kron(value, np.ones((shapefactor, shapefactor), dtype=value.dtype)) * (1/shapefactor**2)
    longitude = np.linspace(longitude[0], longitude[-1], new_shape[1])
    latitude = np.linspace(latitude[0], latitude[-1], new_shape[0])
    lons, lats = np.meshgrid(longitude, latitude)
    return value, lons, lats


def create_source_table(input_dir, mm, sector, shapefactor=2):
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
        value, lons, lats = read_tiff(file, shapefactor=shapefactor)

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

def source2cmaq(emission_date, grid_desc, grid_name, sector, input_dir, inventory_mechanism, target_mechanism, output_dir, shapefactor=2):
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
    data = create_source_table(input_dir, mm, sector, shapefactor=shapefactor)

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
    print(f"Finish: {output_name}")