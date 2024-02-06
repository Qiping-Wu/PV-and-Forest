# -*- coding: utf-8 -*-

from osgeo import gdal
import sys
wgs_albers='PROJCS["wgs_albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",105.0],PARAMETER["Standard_Parallel_1",25.0],PARAMETER["Standard_Parallel_2",47.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'


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
    outpath='/dat1/qiping_data/PV And Forest/WSP_pv2020/'
    clip_PV='/dat1/qiping_data/PV And Forest/PV_CN_7503.shp'
    futr_forest_75_tif='/dat1/qiping_data/PV And Forest/WSP_forest/output/futr_forest_75.tif'
        
    clip_forestation_outpath = outpath+"clip_forestation_pv_2020_CN.tif"
    clip(clip_PV,futr_forest_75_tif,clip_forestation_outpath)
    

if __name__ == "__main__":
   main(sys.argv[1:])

