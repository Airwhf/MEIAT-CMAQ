# 使用2017年的MEIC清单制作珠三角的排放文件

本教程通过一个制作珠江三角洲模拟域（空间分辨率：3km）的排放清单来讲解以下两个程序的运行流程。
1. [coarse_emission_2_fine_emission.py](../coarse_emission_2_fine_emission.py)
2. [Create-CMAQ-Emission-File.py](../Create-CMAQ-Emission-File.py)

本教程使用的原始排放清单为2017年MEIC清单（逐月、分部门、CB05机制），输出的排放文件为2017年7月1日至2017年7月2日的分部门排放文件（CB06，AERO7机制）。

## 第一步：准备`GRIDDESC`文件

`GRIDDESC`由CMAQ的前处理系统MCIP输出，主要需要注意以下两点：
* 保证每一个`GRIDDESC`中有且仅有一个网格信息。
* 保证GRIDDESC中的网格投影为Lambert投影（只要你的WRF设置为Lambert并正常运行MCIP，基本都不会有错）。
* 如本教程所示的`GRIDDESC`文件中，`PRD274x181`是网格名称（`griddesc_name`: 此参数将会被`namelist.input`用到）。

```shell
' '
'LamCon_40N_97W'
  2        25.000        40.000       110.000       110.000        28.500
' '
'PRD274x181'
'LamCon_40N_97W'     48000.000   -902500.000      3000.000      3000.000 271 178   1
' '
```

## 第二步：准备MEIC排放清单

下载地址：http://meicmodel.org/

由于MEIC存在版权保护，因此本程序中不提供数据，请用户自行下载。

下载到的MEIC通常会提供包括`*.asc`在内的一种或几种格式（如图），但本程序所有的网格化文件，都要求使用WGS1984投影的GeoTIFF文件。

![MEIC下载获取到的文件目录](original_meic_files.png =100x100)

因此需要通过[MEIC转GEOTIFF工具](../PREP/meic_2_GeoTiff.py)来对MEIC进行转换。在此程序中，输入的文件仅为`*.asc`格式。

通过以下方法配置好代码以后，在终端中运行`python ./PREP/meic_2_GeoTiff.py`即可。
```python
# ------------------------------------------
input_dir = "MEIC的asc格式文件所在目录路径"
output_dir = "输出文件所在目录路径"
# ------------------------------------------
```

运行成功以后，将会在输出路径下看到系列GeoTIFF格式文件。

## 第二步：配置`namelist.input`文件。






