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
    input_dir='/dat1/PV and forest/Globeland30_2020'
    outpath='/dat1/qiping_data/PV And Forest/WSP_LULC/Globeland30_2020/'
    clip_buf2km='/dat1/qiping_data/PV And Forest/CN_prj_buf2km.shp' 
    clip_CN='/dat1/qiping_data/PV And Forest/CN_prj.shp'
     
    tif_file=input_dir+'/Globeland30_china_30m_clip.tif'
    resample_outpath=outpath+'GL30_Resample.tif'
    path_refer='/dat1/qiping_data/PV And Forest/WSP_forest/output/forestation_buf2km.tif'
    resample_images(path_refer, tif_file, resample_outpath,nodata=0)
    
    clip1_outpath = outpath+"GL30_buf2km.tif"
    clip2_outpath = outpath+"GL30_CN.tif"
    clip(clip_buf2km,resample_outpath,clip1_outpath)
    clip(clip_CN,resample_outpath,clip2_outpath)
 
if __name__ == "__main__":
   main(sys.argv[1:])