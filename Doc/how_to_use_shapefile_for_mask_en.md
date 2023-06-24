How to use shapefile file to generate mask file in CMAQ?

----------------------------

**Translator: Yinbao Jin**

**Author: Wang Haofan**

----------------------------

1. Prepare the shapefile file
The shapefile file has the following main requirements:

•	The projection must be WGS1984 projection.
•	There must be no Chinese characters in the attribute table.
•	There must be a string field in the attribute table that is extracted by the program.
•	The string field must be in uppercase letters.
•	The specific format can be found in: Anyang-around.shp

2. Configure the file
In addition to the above-mentioned changes in the code, the GRIDDESC file is also required by the program, but this file will be retrieved from namelist.input.

# ------------------------------------------------------------
# Shapefile path.
shapefile_path = "shapefile file path"
# The field of each area.
field = "String field name"
# The output path.
output_name = "output file name"
# ------------------------------------------------------------
3. Run the program
In a terminal, type:

python . /Create_CMAQ_mask.py
It will run and output the file.
