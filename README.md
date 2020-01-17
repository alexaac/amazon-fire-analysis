Since the beginning of August 2019, NASA satellites have observed several fires near the border of Bolivia, Paraguay, and Brazil (not in the Amazon rainforest). On August 25, 2019, the Operational Land Imager (OLI) on Landsat 8 acquired images of one of the larger fires, which was burning north of the Paraguay River near Puerto Busch.

This project focuses on change detection analysis, estimating burn severity by analyzing Landsat images acquired before and after a fire. A differenced Normalized Burn Ratio (dNBR) can be used to support fire managers, to measure the burn scars to create a baseline for forest regeneration.

The Normalized Burn Ratio (NBR) is an index designed to highlight burnt areas in large fire zones. The formula is similar to NDVI, except that the formula combines the use of both near infrared (NIR) and shortwave infrared (SWIR) wavelengths. Burn severity describes how the fire intensity affects the functioning of the ecosystem in the area that has been burnt.

The analysis is conducted combining automated ArcGIS models and scripts with supervised classification. Based on pre and post fire Landsat scenes archives, we generate a differenced normalized burn ratio (dNBR) raster, then use supervised classification to produce a 4-class thematic burn severity signature file, then we reclassify dNBR, calculate acreage and find largest burnt perimeter using another model.