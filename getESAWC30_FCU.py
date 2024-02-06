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



def main(argv):
    outpath='/dat1/qiping_data/PV And Forest/WSP_LULC/LC_FCU_30m/'
    input_dir='/dat1/qiping_data/PV And Forest/WSP_LULC/'
    
    #  ESAWC30
    tif_ESAWC30=input_dir+'ESA_WC10/ESAWC30_buf2km.tif'
    ESAWC30_ds=gdal.Open(tif_ESAWC30,gdal.GA_ReadOnly)
    geotransform=ESAWC30_ds.GetGeoTransform()
    projection=ESAWC30_ds.GetProjection()
    ESAWC30_arr=ESAWC30_ds.ReadAsArray()
    ESAWC30_ds=None
    
    # forest: 10
    value_forest=[10]
    ESAWC30_forest_arr=np.where(np.isin(ESAWC30_arr,value_forest),1,0) 
    ESAWC30_forest_outpath=outpath+'ESAWC30_forest.tif'
    array_to_raster(ESAWC30_forest_outpath, ESAWC30_forest_arr, projection, geotransform, driver_name='GTiff', nodata=0)
    
    # cropland: 40
    value_cropland=[40]
    ESAWC30_cropland_arr=np.where(np.isin(ESAWC30_arr,value_cropland),1,0) 
    ESAWC30_cropland_outpath=outpath+'ESAWC30_cropland.tif'
    array_to_raster(ESAWC30_cropland_outpath, ESAWC30_cropland_arr, projection, geotransform, driver_name='GTiff', nodata=0)
    
    # urban: 50
    value_urban=[50]
    ESAWC30_urban_arr=np.where(np.isin(ESAWC30_arr,value_urban),1,0) 
    ESAWC30_urban_outpath=outpath+'ESAWC30_urban.tif'
    array_to_raster(ESAWC30_urban_outpath, ESAWC30_urban_arr, projection, geotransform, driver_name='GTiff', nodata=0)
    
    
if __name__ == "__main__":
   main(sys.argv[1:])