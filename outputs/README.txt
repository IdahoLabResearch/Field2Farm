Fields to Farms Conversion

This script is designed to convert agricultural fields into farms based on specified size categories. The process involves grouping neighboring fields into farms until the desired number of farms in each size category is achieved.

Requirements
•	Python 3.x
•	Required libraries: os, sys, geopandas, pandas, numpy, pert

Installation
1.	Ensure you have Python installed on your system.
2.	Install the required libraries using pip:
	
	pip install geopandas pandas numpy pertdist

Usage
1.	Clone the repository containing the script.
2.	Navigate to the directory containing the script.
3.	Execute the script using Python:
	
	python toFarms.py [{state_name}{FIPS_code}]  
	The script accepts an optional argument in the format [state_name][FIPS_code]. If provided, it specifies the state name and its corresponding three digit FIPS code.

Inputs
•	County Shapefile: The script requires a shapefile containing agricultural fields for a specific county. This file should be named as {state_name}{FIPS_code}_intersect.gpkg and placed in the inputs 		directory. This file is obtained from converting Cropland Data Layer to vector polygons. Several geometric enhancements are conducted to minimize artefacts created during raster to vector conversion. 	Further, the fields are intersected with Open Street Map road layer.
•	NASS Raster Value Attributes: The script uses a CSV file named raster_val_cultivable.csv, which contains a list of cultivable/cultivated NASS raster values. This file should be placed in the inputs 		directory.
•	Lookup Table: A CSV file named lookup_NASS.csv is used to specify the number of farms for each size category. Ensure this file is available in the inputs directory.


Outputs
•	Fields Geopackage: After processing, the script generates a geopackage file containing the classified fields. This file is named {state_name}{FIPS_code}_fields.gpkg and stored in the outputs 	directory.
•	Farms Geopackage: Additionally, the script produces another geopackage file containing the dissolved farms. This file is named {county_name}{FIPS_code}_farms.gpkg and also stored in the outputs 	directory.

Description
The script executes the following steps:
1.	Reads the necessary input files and loads required data.
2.	Processes each field in the county to create farms according to specified size categories.
3.	Ensures the desired number of farms is created in each size category.
4.	Outputs the classified fields and dissolved farms into geopackage files.

Contact
For any inquiries or issues, please contact Rajiv.Paudel@inl.gov. 

