'''
Created on 20 Oct 2019
Converts the scaled Digital Numbers (DN)
 representing multispectral image data 
 acquired by Landsat 8 Operational Land Imager (OLI)  
 to Top of Atmosphere (ToA) Reflectance
@author: Cristina Alexa
'''

import arcpy
import os, re, math
from arcpy.sa import * 

# Input parameters
landsat_folder = arcpy.GetParameterAsText(0) 
output_file = arcpy.GetParameterAsText(1)

# Environment
arcpy.env.overwriteOutput = True
mxd = arcpy.mapping.MapDocument("CURRENT")
dataFrame = mxd.activeDataFrame

def main():
  # Set the workspace
  arcpy.env.workspace = landsat_folder

  # Filter the files that match band5, band 7 and metadata
  rasters = arcpy.ListRasters()
  if len(rasters) == 0:
    arcpy.AddMessage('There are no raster files in the workspace.')
    return
  ( band_5, band_7, metadata ) = [a for a in rasters if a[-6:] in ('B5.TIF', 'B7.TIF', 'TL.txt')]

  # Get metadata file from folder and extract rescaling coefficients for bands 
  mtl_file = os.path.join(landsat_folder, metadata)
  rescaling_coefficients = { 'REFLECTANCE_MULT_BAND_5' : '', 'REFLECTANCE_MULT_BAND_7' : '', 'REFLECTANCE_ADD_BAND_5' : '', 'REFLECTANCE_ADD_BAND_7' : '', 'SUN_ELEVATION' : '' }
  rescaling_coefficients = extract_rescaling_coefficients(mtl_file, rescaling_coefficients)

  # Convert DN to reflectance values for each band
  band_5_corrected = correct_toa_reflectance(arcpy.Raster(band_5), rescaling_coefficients['REFLECTANCE_MULT_BAND_5'], rescaling_coefficients['REFLECTANCE_ADD_BAND_5'], rescaling_coefficients['SUN_ELEVATION'])
  band_7_corrected = correct_toa_reflectance(arcpy.Raster(band_7), rescaling_coefficients['REFLECTANCE_MULT_BAND_7'], rescaling_coefficients['REFLECTANCE_ADD_BAND_7'], rescaling_coefficients['SUN_ELEVATION'])

  # Calculate NBR and save resulting raster to disk
  nbr_raster = calculate_nbr(band_5_corrected, band_7_corrected)

  nbr_output_raster = os.path.join(landsat_folder, output_file or (band_5[0:-7] + "_nbr.tif"))
  nbr_raster.save(nbr_output_raster)
  arcpy.AddMessage('Successfully created ' + nbr_output_raster + '.')

  # Add final raster to display
  arcpy.AddMessage('Adding layers to map document')
  arcpy.mapping.AddLayer(dataFrame, arcpy.mapping.Layer(nbr_output_raster), "TOP")

  # Return resulting raster as output parameter
  arcpy.SetParameter(2, nbr_raster)

  arcpy.AddMessage('Done Processing')

def extract_rescaling_coefficients(mtl_file, rescaling_coefficients):
  # Extract rescaling coefficients from the MTL file
  with open(mtl_file) as MTL:
    lines = MTL.read().splitlines()
    for line in lines:
      if "=" in line:
        line = re.sub(r"[\n\t\s]*", "", line)
        name, var = line.split("=")
        if name in rescaling_coefficients.keys():
          rescaling_coefficients[name] = var

  arcpy.AddMessage('Rescaling coefficients: ')
  arcpy.AddMessage(rescaling_coefficients)

  return rescaling_coefficients

def correct_toa_reflectance(raster_band, reflectance_mult_band, reflectance_add_band, sun_elevation):
  # Reflective band DN’s can be converted to TOA reflectance using the rescaling coefficients in the MTL file

  # Remove zero values
  arcpy.CheckOutExtension('Spatial')
  band_file_without_zero = SetNull(raster_band, raster_band, 'value=0')

  band_corrected_without_sun_angle = correct_toa_without_sun_angle(band_file_without_zero, reflectance_mult_band, reflectance_add_band)

  band_corrected_final = correct_toa_for_sun_angle(band_corrected_without_sun_angle, sun_elevation)

  return band_corrected_final

def correct_toa_without_sun_angle(band_file_without_zero, reflectance_mult_band, reflectance_add_band):
  # https://www.usgs.gov/land-resources/nli/landsat/using-usgs-landsat-level-1-data-product
  # The published formula for TOA Reflectance is: ρλ′ = MρQcal + Aρ
  # ρλ' = TOA planetary reflectance without correction for solar angle.
  # Mρ = Band-specific multiplicative rescaling factor from the metadata (REFLECTANCE_MULT_BAND_x, where x is the band number)
  # Aρ = Band-specific additive rescaling factor from the metadata (REFLECTANCE_ADD_BAND_x, where x is the band number)
  # Qcal = Quantized and calibrated standard product pixel values (DN)

  band_corrected_without_sun_angle = band_file_without_zero * float(reflectance_mult_band) - float( reflectance_add_band)

  return band_corrected_without_sun_angle

def correct_toa_for_sun_angle(band_file_without_zero, sun_elevation):
  # https://www.usgs.gov/land-resources/nli/landsat/using-usgs-landsat-level-1-data-product
  # TOA reflectance can be corrected for the sun angle by:
  # ρλ = ρλ′ / cos(θSZ) = ρλ′ / sin(θSE)
  # ρλ=  TOA planetary reflectance
  # θSE =  Local sun elevation angle. The scene center sun elevation angle in degrees is provided in the metadata (SUN_ELEVATION).
  # θSZ = Local solar zenith angle;  θSZ = 90° - θSE
  # Rl = TOA planetary reflectance
  # Solar Elevation angle = local sun elevation from the metadata (SUN_ELEVATION)
  # SUN_ELEVATION is unique to each Landsat 8 Scene

  band_corrected_for_sun_angle = band_file_without_zero / math.sin( float(sun_elevation) )

  return band_corrected_for_sun_angle

def calculate_nbr(band_5_corrected, band_7_corrected):
  # http://un-spider.org/advisory-support/recommended-practices/recommended-practice-burn-severity/in-detail/normalized-burn-ratio
  # The Normalized Burn Ratio (NBR) is an index designed to highlight burnt areas in large fire zones. The formula is similar to NDVI, except that the formula combines the use of both near infrared (NIR) and shortwave infrared (SWIR) wavelengths.
  # NBR = (NIR-SWIR)/(NIR+SWIR)
  # Landsat 8:  NBR =(B5-B7)/(B5+B7)

  nbr = Int(Float(band_5_corrected - band_7_corrected) / (band_5_corrected + band_7_corrected)*1000)

  return nbr

if __name__ == '__main__':
  main()
1


