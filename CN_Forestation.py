# -*- coding: utf-8 -*-

import h5py
import numpy as np
from osgeo import gdal,osr
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
    input_dir='/dat1/qiping_data/PV And Forest/WSP_forest/potential_forest_china_1km/'
    outpath='/dat1/qiping_data/PV And Forest/WSP_forest/output/' 
    clip_buf='/dat1/qiping_data/PV And Forest/CN_prj_buf2km.shp' 
    clip_CN='/dat1/qiping_data/PV And Forest/CN_prj.shp' 
    
    Bastin_mat = h5py.File(input_dir+"Potential_forest_china_Bastin_RF_bytsc_1km.mat")
    ORCHIDEE_mat = h5py.File(input_dir+"Potential_forest_china_ORCHIDEE_downscale_by_RF_1km.mat")
    WRI_mat = h5py.File(input_dir+"Potential_forest_china_WRI_with_woodland_1km.mat")

    geotransform = (70, 1.0 / 120, 0, 55, 0, -1.0 / 120)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  
    projection=srs.ExportToWkt()

    Bastin_mat_t = np.transpose(Bastin_mat['potential_forest'])
    ORCHIDEE_mat_t = np.transpose(ORCHIDEE_mat['potential_forest'])
    WRI_mat_t = np.transpose(WRI_mat['potential_forest'])
    proj_ops=gdal.WarpOptions(format='GTiff',
                              srcSRS='EPSG:4326',
                              dstSRS=wgs_albers,
                              xRes=30,
                              yRes=30,
                              resampleAlg='near',
                              creationOptions=["COMPRESS=LZW"],
                              srcNodata=0, dstNodata=0
                              )
    multiply_1=np.add(Bastin_mat_t, ORCHIDEE_mat_t)
    forastation=np.add(multiply_1,WRI_mat_t)

    forestation_outpath=outpath+'forestation.tif'
    array_to_raster(forestation_outpath, forastation, projection, geotransform, driver_name='GTiff', nodata=0)
    
    prj_outpath_30m=outpath+'forestation_prj.tif'
    gdal.Warp(prj_outpath_30m,forestation_outpath, options=proj_ops)
    
    forestation_buf_outpath = outpath+"forestation_buf2km.tif"
    forestation_CN_outpath = outpath+"forestation_CN.tif"
    clip(clip_buf,prj_outpath_30m,forestation_buf_outpath)
    clip(clip_CN,prj_outpath_30m,forestation_CN_outpath)


if __name__ == "__main__":
   main(sys.argv[1:])