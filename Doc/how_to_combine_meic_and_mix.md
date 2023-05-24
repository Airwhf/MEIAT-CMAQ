# 如何同时使用MEIC和MIX清单？

**作者：王浩帆**

MEIC清单仅为中国境内的排放清单，但是在模拟全国污染场的案例中，中国周边国家的排放是不容忽视的，因此需要通过MIX清单来对MEIC进行一个补充。

不论是模拟网格分辨率大于等于清单网格分辨率，还是模拟网格分辨率小于清单网格分辨率的情况，同时使用MEIC和MIX清单的关键步骤都是如何将MEIC清单镶嵌到MIX中，
作为一系列新的GeoTIFF文件来作为[coarse_emission_2_fine_emission.py](../coarse_emission_2_fine_emission.py)和
[fine_emission_2_coarse_emission.py](../fine_emission_2_coarse_emission.py)的输入。

**因此本部分将重点讲解如何使用工具来完成两个系列GeoTIFF的镶嵌工作。**

1. 将MIX清单和MEIC清单都转换为GeoTiff格式。
* 使用[mix_2_GeoTiff.py](../PREP/mix_2_GeoTiff.py)将MIX清单转换为GeoTiff格式。
* 使用[meic_2_GeoTiff.py](../PREP/meic_2_GeoTiff.py)将MEIC清单转换为GeoTiff格式。
由于MIX清单中没有PMC，因此需要通过[calculate-pmc.py](../calculate-pmc.py)将其计算出来。

2. 配置[combine.py](../UTIL/combine/combine.py)中的输入参数。

* upper_raster_dir：上层GeoTiff所在目录路径。
* bottom_raster_dir：下层GeoTiff所在目录路径。
* output_dir：输出GeoTiff目录路径。


* upper_raster_pollutants：上层GeoTiff需要合并的污染物名称。
* bottom_raster_pollutants：下层GeoTiff所对应的污染物名称。
* output_pollutants：一一对应到的输出污染物的名称。


* upper_label：上层GeoTiff标签。
* bottom_label：下层GeoTiff标签。
* output_label：输出GeoTiff标签。


* upper_raster_template：任意一个上层GeoTiff文件路径。
* bottom_raster_template：任意一个下层GeoTiff文件路径。


* upper_resolution：上层GeoTiff的分辨率。
* bottom_resolution：下层GeoTiff的分辨率。


* sectors：需要合并的部门。


* upper_year：上层GeoTiff的年份。
* bottom_year：下层GeoTiff的年份。
* output_year：定义输出GeoTiff的年份。


3. 运行[combine.py](../UTIL/combine/combine.py)

在终端中输入：
```shell
python ./combine.py
```
便可以开始运行程序，程序结束后将在`output_dir`中产生合并后的系列GeoTiff。

4. 进行空间分配、物种分配和时间分配。

此步骤和[第一个教程](1-adopt_meic_for_prd_emission_file.md)或第二个教程中的步骤完全相同，不再赘述。

