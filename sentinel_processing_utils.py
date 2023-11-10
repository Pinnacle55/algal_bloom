#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os, sys
from glob import glob
import argparse


# In[5]:


def generate_input_file_list(folder):
    '''
    Creates a txt file called "input_file_paths.txt" containing all the Sentinel Bands in the folder. 
    
    NOTE: The bands will be arranged 1-12, 8A due to sorting.
    
    Returns the path to the txt file.
    '''
    filepaths = glob(os.path.join(folder, "*B*.jp2"))
    
    file_path = os.path.join(folder, "input_file_paths.txt")
    
    with open(file_path, 'w') as file:
        for item in filepaths:
            file.write(str(item) + '\n')
        
        file.close()
        
    return file_path


# In[ ]:


# Call GDAL on command line
# -separate means that each file in the input file list will be made into a separate band
# -resolution user & -tr 10 10 together will upsample the image to 10m by 10m
# -r bilinear indicates the upsampling algorithm
command1 = 'gdalbuildvrt -separate -resolution user -tr 10 10 -r bilinear -input_file_list "{input_file_list}" sentinel.vrt'

# Crops to a given shapefile/geojson
# This SHOULD work regardless of the CRS of the OGR object
command2 = 'gdalwarp -cutline "{shapefile}" -crop_to_cutline sentinel.vrt sentinel_cropped.vrt'

# gdal_translate command to run depending on whather it was cropped
command3 = 'gdal_translate -of GTiff sentinel.vrt sentinel_stacked.tif'
command4 = 'gdal_translate -of GTiff sentinel_cropped.vrt sentinel_cropped_stacked.tif'


# In[ ]:


def process_sentinel_folder(folder, shapefile = None):
    input_file_list = generate_input_file_list(folder)
    
    os.system(command1.format(
            input_file_list = input_file_list
        ))
    
    if shapefile is not None:
        os.system(command2.format(
            shapefile = shapefile
        ))
        
        os.system(command4)
        
    else:
        os.system(command3)


# In[ ]:


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Stacks, crops (optional), and converts Sentinel-2 bands into a GeoTIFF. GeoTIFF will be saved in the location where this file was run. Note that the final raster will not be in reflectances; DN to reflectance conversion is different depending on when the data was collected. Data produced prior to October 26, 2021 is normalized by DN / 10000, while data after October 26, 2021 is normalized by (DN - 1000) / 10000.')

    # add positional argument (i.e., required argument)
    parser.add_argument('filepath',
                       help = 'Path to folder containing all Landsat bands and MTL file.')

    # optional flags - the name of the variable is the -- option
    parser.add_argument('-m', '--mask', help = 'Provide a shapefile that the images will be cropped to')
    
    # grab arguments from command line
    args = parser.parse_args()
    
    # calculate TOA
    process_sentinel_folder(args.filepath, 
                            shapefile = args.mask)

