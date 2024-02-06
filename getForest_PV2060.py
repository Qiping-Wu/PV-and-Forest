# -*- coding: utf-8 -*-

from osgeo import gdal
import sys


wgs_albers='PROJCS["wgs_albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",105.0],PARAMETER["Standard_Parallel_1",25.0],PARAMETER["Standard_Parallel_2",47.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'


def resample_images(path_refer, path_resample, out_path_resample,nodata=None): 
    ds_refer = gdal.Open(path_refer, gdal.GA_ReadOnly)  
    proj_refer = ds_refer.GetProjection() 
    trans_refer = ds_refer.GetGeoTransform()  
    # band_refer = ds_refer.GetRasterBand(1)   
    width_refer = ds_refer.RasterXSize  
    height_refer = ds_refer.RasterYSize 
    bands_refer = ds_refer.RasterCount  
    
    ds_resample = gdal.Open(path_resample, gdal.GA_ReadOnly) 
    proj_resample = ds_resample.GetProjection()  
    band_resample=ds_resample.GetRasterBand(1)
    
    driver = gdal.GetDriverByName('GTiff')  
    ds_output = driver.Create(out_path_resample, width_refer, height_refer, bands_refer,
                              band_resample.DataType,options=["COMPRESS=LZW"]) 
    ds_output.SetGeoTransform(trans_refer)  
    ds_output.SetProjection(proj_refer)  
    
    gdal.ReprojectImage(ds_resample, ds_output, proj_resample, proj_refer, 
                        gdal.GRA_NearestNeighbour,
                        0.0, 0.0,
                        )
    
    band = ds_output.GetRasterBand(1)
    if None != nodata:
        band.SetNoDataValue(nodata)
    ds_refer=None
    ds_output=band=None
    ds_resample=band_resample=None
    
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
    outpath='/dat1/qiping_data/PV And Forest/WSP_wr/'
    clip_CN='/dat1/qiping_data/PV And Forest/CN_prj.shp'
    futr_forest_75_tif='/dat1/qiping_data/PV And Forest/WSP_forest/output/futr_forest_75.tif'
    PV_tif='/dat1/qiping_data/PV And Forest/WSP_wr/pv_2060_30m.tif'
   
    futr_forest_75_ds=gdal.Open(futr_forest_75_tif,gdal.GA_ReadOnly)
    geotransform=futr_forest_75_ds.GetGeoTransform()
    projection=futr_forest_75_ds.GetProjection()
    futr_forest_75_arr=futr_forest_75_ds.ReadAsArray()
    futr_forest_75_ds=None
    
    pv_2060_ds=gdal.Open(PV_tif,gdal.GA_ReadOnly)
    pv_2060_arr=pv_2060_ds.ReadAsArray()
    pv_2060_ds=None
    
    pv_2060_clip_forest_outpath=outpath+'clip_forestation_pv_2060.tif'
    futr_forest_75_arr[pv_2060_arr==0]=0
    array_to_raster(pv_2060_clip_forest_outpath, 
                    futr_forest_75_arr, 
                    projection, geotransform, driver_name='GTiff', nodata=0)
    
    clip_outpath_CN = outpath+"clip_forestation_pv_2060_CN.tif"
    clip(clip_CN,pv_2060_clip_forest_outpath,clip_outpath_CN)

if __name__ == "__main__":
   main(sys.argv[1:])

