## -*- coding: utf-8 -*-

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
    outpath='/dat1/qiping_data/PV And Forest/WSP_forest/output/'
    clip_CN='/dat1/qiping_data/PV And Forest/CN_prj.shp' 
    input_dir='/dat1/qiping_data/PV And Forest/WSP_LULC/LC_FCU_30m/'

    #  potential forestation area
    tif_forestation='/dat1/qiping_data/PV And Forest/WSP_forest/output/forestation_buf2km.tif'
    forestation_ds=gdal.Open(tif_forestation,gdal.GA_ReadOnly)
    geotransform=forestation_ds.GetGeoTransform()
    projection=forestation_ds.GetProjection()
    forestation_arr=forestation_ds.ReadAsArray()
    forestation_ds=None
    
    # existing forest
    FCU_forest_tif=input_dir+'FCU_forest.tif'
    FCU_forest_ds=gdal.Open(FCU_forest_tif,gdal.GA_ReadOnly)
    FCU_forest_arr=FCU_forest_ds.ReadAsArray()
    FCU_forest_ds=None 
    
    FCU_forest_arr=np.where(FCU_forest_arr>=5,1,0) 
    FCU_forest_75_outpath=input_dir+'FCU_forest_75.tif'
    array_to_raster(FCU_forest_75_outpath, FCU_forest_arr, projection, geotransform, driver_name='GTiff', nodata=0)
    forestation_arr = np.where(FCU_forest_arr == 1, 0, forestation_arr)
    
    # cropland
    FCU_cropland_tif=input_dir+'FCU_cropland.tif'
    FCU_cropland_ds=gdal.Open(FCU_cropland_tif,gdal.GA_ReadOnly)
    FCU_cropland_arr=FCU_cropland_ds.ReadAsArray()
    FCU_cropland_ds=None 
        
    FCU_cropland_arr=np.where(FCU_cropland_arr>=5,1,0) 
    FCU_cropland_75_outpath=input_dir+'FCU_cropland_75.tif'
    array_to_raster(FCU_cropland_75_outpath, FCU_cropland_arr, projection, geotransform, driver_name='GTiff', nodata=0)
    forestation_arr = np.where(FCU_cropland_arr == 1, 0, forestation_arr)
    
    # urban
    FCU_urban_tif=input_dir+'FCU_urban.tif'
    FCU_urban_ds=gdal.Open(FCU_urban_tif,gdal.GA_ReadOnly)
    FCU_urban_arr=FCU_urban_ds.ReadAsArray()
    FCU_urban_ds=None      
        
    FCU_urban_arr=np.where(FCU_urban_arr>=5,1,0) 
    FCU_urban_75_outpath=input_dir+'FCU_urban_75.tif'
    array_to_raster(FCU_urban_75_outpath, FCU_urban_arr, projection, geotransform, driver_name='GTiff', nodata=0)
    forestation_arr = np.where(FCU_urban_arr == 1, 0, forestation_arr)
    
    futr_forest_75_outpath=outpath+'futr_forest_75.tif'
    array_to_raster(futr_forest_75_outpath, forestation_arr, projection, geotransform, driver_name='GTiff', nodata=0)
    
    futr_forest_CN_75_outpath=outpath+'futr_forest_CN_75.tif'
    clip(clip_CN,futr_forest_75_outpath,futr_forest_CN_75_outpath)
    

if __name__ == "__main__":
   main(sys.argv[1:])