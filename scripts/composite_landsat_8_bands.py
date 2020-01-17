'''
Created on 20 Oct 2019
Create Composite Rasters 
from Landsat Extracted Folder
@author: Cristina Alexa
'''

import arcpy
import os, re

# Input parameters
landsat_folder = arcpy.GetParameterAsText(0) 
output_file = arcpy.GetParameterAsText(1)
bands_string = arcpy.GetParameterAsText(2)

# Environment
arcpy.env.overwriteOutput = True
mxd = arcpy.mapping.MapDocument("CURRENT")
dataFrame = mxd.activeDataFrame

def main():

  # Create composite raster from bands in Landsat 8 folder
  composite_raster = create_composite_raster(landsat_folder, bands_string, output_file)

  # Return resulting raster(s) as output parameter
  if composite_raster:
    arcpy.SetParameter(2, composite_raster)
  else:
    arcpy.AddMessage('There are no raster files in the workspace.')

  arcpy.AddMessage('Done Processing')

def create_composite_raster(landsat_folder, bands_string, output_file):
  # Set the workspace
  arcpy.env.workspace = landsat_folder

  # Get the list of raster files in folder
  rasters = arcpy.ListRasters('*.TIF')
  if len(rasters) == 0:
    return

  # Get the list of file endings that match the user bands list
  bands_string = re.sub(r'[\n\t\s]*', '', bands_string)
  check_bands = ['B{0}.TIF'.format(i) for i in bands_string.split(',')]

  # Filter the raster files that match the user bands list
  rasters = [a for a in rasters if a[-6:] in check_bands]

  # Composite bands and save resulting raster to disk
  output_raster_name = os.path.join(landsat_folder, output_file or (rasters[1][0:-7] + '_composite.tif'))
  composite_raster = arcpy.CompositeBands_management(rasters, output_raster_name)
  arcpy.AddMessage('Successfully created ' + output_raster_name + '.')

  # Add resulting raster to display
  arcpy.AddMessage('Adding layer to map document')
  band_layer = arcpy.mapping.Layer(output_raster_name)
  arcpy.mapping.AddLayer(dataFrame, band_layer, "TOP")

  return composite_raster

if __name__ == '__main__':
  main()



