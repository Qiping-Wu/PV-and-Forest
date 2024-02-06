# -*- coding: utf-8 -*-

import numpy as np
from osgeo import gdal
import sys

wgs_albers='PROJCS["wgs_albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",105.0],PARAMETER["Standard_Parallel_1",25.0],PARAMETER["Standard_Parallel_2",47.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'

def numpy_to_gdal(dtype):
    """convert numpy dtype to gdal dtype"""
    numpy_dtype = ["byte", "uint8", "uint16", "uint32",
        "uint64", "int8", "int16", "int32",
        "int64", "float16", "float32", "float64",
        "cint16", "cint32", "cfloat32", "cfloat64"]
    gdal_dtype = [gdal.GDT_Byte, gdal.GDT_Byte, 
        gdal.GDT_UInt16, gdal.GDT_UInt32, gdal.GDT_Float32, 
        gdal.GDT_Int16, gdal.GDT_Int16, gdal.GDT_Int32, 
        gdal.GDT_Float32, gdal.GDT_Float32, gdal.GDT_Float32, 
        gdal.GDT_Float64, gdal.GDT_CInt16, gdal.GDT_CInt32, 
        gdal.GDT_CFloat32, gdal.GDT_CFloat64]
    return gdal_dtype[numpy_dtype.index(dtype.name)]


def array_to_raster(path, array, proj, gt, driver_name='GTiff', nodata=None):
    """ Saving a 2-d array to raster file. """
    assert len(array.shape) == 2
    driver = gdal.GetDriverByName(driver_name)
    dtype = numpy_to_gdal(array.dtype)
    ds = driver.Create(path,
                       array.shape[1],
                       array.shape[0],
                       1, dtype,
                       options=["COMPRESS=LZW"])
    ds.SetProjection(proj)
    ds.SetGeoTransform(gt)
    band = ds.GetRasterBand(1)
    band.WriteArray(array)
    if None != nodata:
        band.SetNoDataValue(nodata)
    ds = band = None


def clip(shp,tif,outpath):
    clip_ops=gdal.WarpOptions(format='GTiff',
                              srcSRS=wgs_albers,
                              dstSRS=wgs_albers,
                              cutlineDSName=shp,
                              cropToCutline=True,
                              creationOptions=["COMPRESS=LZW"],
                              srcNodata=0, dstNodata=0)
    gdal.Warp(outpath,tif,options=clip_ops)


def main(argv):
    input_dir='/dat1/qiping_data/PV And Forest/WSP_LULC/LC_FCU_30m/'

    #  potential forestation area
    tif_forestation='/dat1/qiping_data/PV And Forest/WSP_forest/output/forestation_buf2km.tif'
    forestation_ds=gdal.Open(tif_forestation,gdal.GA_ReadOnly)
    geotransform=forestation_ds.GetGeoTransform()
    projection=forestation_ds.GetProjection()
    forestation_arr=forestation_ds.ReadAsArray()
    forestation_ds=None
    # existing forest
    CLCD_forest=input_dir+'CLCD_forest.tif'
    ESACCI_forest=input_dir+'ESACCI_forest.tif'
    ESAWC30_forest=input_dir+'ESAWC30_forest.tif'
    Esri30_forest=input_dir+'Esri30_forest.tif'
    GLCFCS_forest=input_dir+'GLCFCS_forest.tif'
    GL30_forest=input_dir+'GL30_forest.tif'
    ModisLC_forest=input_dir+'ModisLC_forest.tif'   
    
    forest_list=[CLCD_forest,ESACCI_forest,ESAWC30_forest,Esri30_forest,GLCFCS_forest,GL30_forest,ModisLC_forest]
    FCU_forest_arr=np.zeros_like(forestation_arr)
    for item in forest_list:
        ds=gdal.Open(item,gdal.GA_ReadOnly)
        arr=ds.ReadAsArray()
        FCU_forest_arr=np.add(FCU_forest_arr,arr)
        ds=None    
        
    FCU_forest_outpath=input_dir+'FCU_7forest.tif'
    array_to_raster(FCU_forest_outpath, FCU_forest_arr, projection, geotransform, driver_name='GTiff', nodata=0)
    
    # cropland
    CLCD_cropland=input_dir+'CLCD_cropland.tif'
    ESACCI_cropland=input_dir+'ESACCI_cropland.tif'
    ESAWC30_cropland=input_dir+'ESAWC30_cropland.tif'
    Esri30_cropland=input_dir+'Esri30_cropland.tif'
    GLCFCS_cropland=input_dir+'GLCFCS_cropland.tif'
    GL30_cropland=input_dir+'GL30_cropland.tif'
    ModisLC_cropland=input_dir+'ModisLC_cropland.tif'   
    
    cropland_list=[CLCD_cropland,ESACCI_cropland,ESAWC30_cropland,Esri30_cropland,GLCFCS_cropland,GL30_cropland,ModisLC_cropland]
    FCU_cropland_arr=np.zeros_like(forestation_arr)
    for item in cropland_list:
        ds=gdal.Open(item,gdal.GA_ReadOnly)
        arr=ds.ReadAsArray()
        FCU_cropland_arr=np.add(FCU_cropland_arr,arr)
        ds=None    
        
    FCU_cropland_outpath=input_dir+'FCU_7cropland.tif'
    array_to_raster(FCU_cropland_outpath, FCU_cropland_arr, projection, geotransform, driver_name='GTiff', nodata=0)

    
    # urban
    CLCD_urban=input_dir+'CLCD_urban.tif'
    ESACCI_urban=input_dir+'ESACCI_urban.tif'
    ESAWC30_urban=input_dir+'ESAWC30_urban.tif'
    Esri30_urban=input_dir+'Esri30_urban.tif'
    GLCFCS_urban=input_dir+'GLCFCS_urban.tif'
    GL30_urban=input_dir+'GL30_urban.tif'
    ModisLC_urban=input_dir+'ModisLC_urban.tif'   
    
    urban_list=[CLCD_urban,ESACCI_urban,ESAWC30_urban,Esri30_urban,GLCFCS_urban,GL30_urban,ModisLC_urban]
    FCU_urban_arr=np.zeros_like(forestation_arr)
    for item in urban_list:
        ds=gdal.Open(item,gdal.GA_ReadOnly)
        arr=ds.ReadAsArray()
        FCU_urban_arr=np.add(FCU_urban_arr,arr)
        ds=None    
        
    FCU_urban_outpath=input_dir+'FCU_7urban.tif'
    array_to_raster(FCU_urban_outpath, FCU_urban_arr, projection, geotransform, driver_name='GTiff', nodata=0)


if __name__ == "__main__":
   main(sys.argv[1:])