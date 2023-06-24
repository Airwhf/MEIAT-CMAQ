# How to use both MEIC and MIX inventory simultaneously.

------------------------

**Translator: Ao Shen**

**Author: Haofan Wang**

------------------------

The MEIC inventory only covers emissions within the territory of China. The emissions from neighboring countries cannot be ignored while simulating a nationwide pollution scenario. Therefore, it is necessary to supplement the MEIC inventory with the MIX inventory.

Regardless of the relationship between the simulation grid resolution and the inventory grid resolution, the key steps to using both MEIC and MIX inventory are integrate the MEIC inventory into the MIX inventory and generate a series of new GeoTIFF files as inputs for the [coarse_emission_2_fine_emission.py](../coarse_emission_2_fine_emission.py) and [fine_emission_2_coarse_emission.py](../fine_emission_2_coarse_emission.py) scripts.

**Therefore, this section will focus on explaining how to use tools to accomplish the merging of the two series of GeoTIFF files.**

1. Convert both the MIX inventory and MEIC inventory to GeoTiff format.
* Convert the MIX inventory to GeoTiff format using [mix_2_GeoTiff.py](../PREP/mix_2_GeoTiff.py).
* Convert the MEIC inventory to GeoTiff format using [meic_2_GeoTiff.py](../PREP/meic_2_GeoTiff.py).
Since the PMC is not available in the MIX inventory, it needs to be calculated using [calculate-pmc.py](../calculate-pmc.py).

2. Configure the input parameters in [combine.py](../UTIL/combine/combine.py).

* upper_raster_dir：The directory path of the upper-level GeoTiff.
* bottom_raster_dir：The directory path of the under-level GeoTiff.
* output_dir：The directory path of the output GeoTiff.


* upper_raster_pollutants：The pollutant names to be merged in the upper-level GeoTiff.
* bottom_raster_pollutants：The pollutant names to be merged in the under-level GeoTiff.
* output_pollutants：一一The corresponding names of the output pollutants.


* upper_label：Labels for the upper-level GeoTiff.
* bottom_label：Labels for the under-level GeoTiff.
* output_label：Labels for the output GeoTiff.


* upper_raster_template：Any file path of an upper-level GeoTiff.
* bottom_raster_template：Any file path of an under-level GeoTiff.


* upper_resolution：Resolution of the upper-level GeoTiff.
* bottom_resolution：Resolution of the under-level GeoTiff.


* sectors：Departments needed to be merged.


* upper_year：Year of the upper-level GeoTiff.
* bottom_year：Year of the under-level GeoTiff.
* output_year：Define the year of the output GeoTiff.


3. Run [combine.py](../UTIL/combine/combine.py).

Enter the following command in the terminal:

```shell
python ./combine.py
```
You can start running the program. When the program is finished, the combined series of GeoTiff will be produced in 'output_dir'.

4. Space allocation, species allocation and time allocation.

This step is identical to the steps in the first tutorial (1-adopt_meic_for_prd_emission_file.md) or the second tutorial, which will not be repeated here.

