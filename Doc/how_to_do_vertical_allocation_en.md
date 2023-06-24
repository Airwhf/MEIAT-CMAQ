Perform vertical allocation of emission files

--------------------

**Translator: Yinbao Jin**

--------------------

The vertical allocation process for the surface source emissions is done using vertical_allocation.py, which provides two vertical allocation schemes for the power and industry sectors, profile-industry.csv and profile-power.csv, respectively. Users can also customize vertical allocation coefficients based on the provided file formats. Since vertical_allocation.py can only recognize files named profile.csv, it is necessary to make a copy of the file with the name profile-power.csv for the allocation process.

The following steps illustrate the emission allocation for the power sector:

Copy profile-power.csv to profile.csv.
Open vertical_allocation.py and modify the following code:
files = glob.glob(r"output*power*.nc")
Run the following command in the terminal to start the process:
python .\vertical_allocation.py
The vertically allocated results can be found in the output/vertical directory.
