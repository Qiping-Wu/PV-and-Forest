# -*- coding: utf-8 -*-

from osgeo import gdal
import os
import sys
import numpy as np

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
                       options=["COMPRESS=LZW","BIGTIFF=YES"])
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
                              srcNodata=0, dstNodata=0)
    gdal.Warp(outpath,tif,options=clip_ops)
    
def count_pixels(tif_path):
    dataset = gdal.Open(tif_path,gdal.GA_ReadOnly)
    if dataset is None:
        print(f"cannot open：{tif_path}")
        return
    band = dataset.GetRasterBand(1)
    data = band.ReadAsArray()
    nodata_value=band.GetNoDataValue()
    non_nodata_pixels = np.sum(data != nodata_value)
    print(f"forest number of {tif_path}：{non_nodata_pixels}")
    dataset = None
    
def process_GLCFCS30(input_dir,outpath,clip_pv,year):
    tif_list=list()
    tif_files=os.listdir(input_dir)
    for filename in tif_files:
        if os.path.splitext(filename)[1]=='.tif':
            tif_list.append(input_dir+'/'+filename)
            
    merge_options=gdal.WarpOptions(format='GTiff',resampleAlg='near',srcNodata=None, dstNodata=255)
    merge_outpath=outpath+'GLCFCS30Mrg'+str(year)+'.tif'
    GLCFCS30Mrg=gdal.Warp(merge_outpath, tif_list,options=merge_options)
     
    proj_options=gdal.WarpOptions(format='GTiff',
                              srcSRS='EPSG:4326',
                              dstSRS=wgs_albers,
                              xRes=30,
                              yRes=30,
                              resampleAlg='near',
                              srcNodata=255, dstNodata=0
                              )
    prj_outpath=outpath+'GLCFCS30Prj'+str(year)+'.tif'
    GLCFCS30Prj=gdal.Warp(prj_outpath,GLCFCS30Mrg, options=proj_options)
    GLCFCS30Mrg=None  
    
    GLCFCS30Arr=GLCFCS30Prj.ReadAsArray()
    proj=GLCFCS30Prj.GetProjection()
    gt=GLCFCS30Prj.GetGeoTransform()
    GLCFCS30Prj=None
    
    forest_values=[51,52,61,62,71,72,81,82,91,92]
    nodata_value=0
    forestArr=np.full_like(GLCFCS30Arr,nodata_value,dtype=GLCFCS30Arr.dtype)
    mask=np.isin(GLCFCS30Arr,forest_values)
    forestArr[mask]=GLCFCS30Arr[mask]
    
    forest_outpath=outpath+'GLCFCS30Forest'+str(year)+'.tif'
    array_to_raster(forest_outpath, forestArr, proj, gt, driver_name='GTiff', nodata=0)
    
    clip_outpath=outpath+'GLCFCS30Clip'+str(year)+'.tif'
    clip(clip_pv,forest_outpath,clip_outpath)
    
    count_pixels(clip_outpath)

def main(argv):
    input_dir=argv[0]
    outpath=argv[1]+'/'
    clip_pv=argv[2]
    
    process_GLCFCS30(input_dir+'/2000',outpath,clip_pv,2000)
    process_GLCFCS30(input_dir+'/2010',outpath,clip_pv,2010)

if __name__ == "__main__":
   main(sys.argv[1:])