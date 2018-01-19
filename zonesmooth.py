import arcpy
import os
import shutil
import sys

# ArcGIS extensions
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.AddMessage("Checking out Spatial")
    arcpy.CheckOutExtension("Spatial")
else:
    arcpy.AddError("Unable to get spatial analyst extension")
    arcpy.AddMessage(arcpy.GetMessages(0))
    sys.exit(0)

# inputs
zones = arcpy.GetParameterAsText(0)  # C:\Users\kfisher\Documents\welikia\ecosystems\work\DEM and tidal zones\tidal_zones_poly.shp
zonename = arcpy.GetParameterAsText(1)  # MSL_1609
dem = arcpy.GetParameterAsText(2)  # C:\Users\kfisher\Documents\welikia\ecosystems\work\DEM and tidal zones\DEMFIX7_jan121.tif
iterations = arcpy.GetParameter(3)  # 5
window = arcpy.GetParameter(4)  # 100
aoi = arcpy.GetParameterAsText(5)  # C:\Users\kfisher\Documents\welikia\ecosystems\work\DEM and tidal zones\WELIKIA_EXTENT_POLY_v2.shp
outfile = arcpy.GetParameterAsText(6)  # C:\Users\kfisher\Documents\welikia\ecosystems\work\DEM and tidal zones\output\tidal.tif
neighborhood = arcpy.sa.NbrRectangle(window, window, "CELL")

# environment
arcpy.env.overwriteOutput = True
TEMP_DIR = os.path.join(os.path.dirname(outfile), 'temp')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem

# clear existing temp files
for the_file in os.listdir(TEMP_DIR):
    file_path = os.path.join(TEMP_DIR, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        arcpy.AddError(e)


# convert zones to grid
focalfile = os.path.join(TEMP_DIR, 'focal.tif')
arcpy.PolygonToRaster_conversion(in_features=zones,
                                 value_field=zonename,
                                 out_rasterdataset=focalfile,
                                 cellsize=dem)

# loop iterations times and run focalwindow on previous loop's input
working = arcpy.Raster(focalfile)
for i in range(0, iterations):
    arcpy.AddMessage('Loop %s [window: %s]' % (i+1, window))
    working = arcpy.sa.FocalStatistics(in_raster=working,
                                       neighborhood=neighborhood,
                                       statistics_type='MEAN')

# clip final grid back to AOI
outraster = arcpy.sa.ExtractByMask(in_raster=working,
                                   in_mask_data=aoi)
outraster.save(outfile)
