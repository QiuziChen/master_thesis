'''
@File    :   grade.py
@Time    :   2024/05/19 18:10:15
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   
'''


"""
ELEVATION AND GRADE
"""


import numpy as np
import pandas as pd
import warnings

from osgeo import osr, gdal
from .smoothing import expSmooth


def calGrade(
        traj:pd.DataFrame,
        lonCol:str,
        latCol:str,
        distCol:str,
        eleCol=None,
        newCol='grade[D]',
        fromDEM=False,
        dem=None,
):
    """
    Match elevation to traj points and calculate the grade.
    distCol: column name of dist interval, meter.
    eleCol: column name of elevation, if fromDEM is True, then set eleCol to None.
    fromDEM: if True, extract elevation and grade from DEM.
    dem: if fromDEM is True, input the DEM file.
    newCol: name of the new grade column.
    """
    traj = traj.copy()
    
    if fromDEM:  # elevation from DEM
        warnings.filterwarnings('ignore')

        # get elevation
        eleMap = dem2ele(dem)
        traj.loc[:, 'ele[m]'] = traj.apply(lambda x: eleMatch(x, dem, eleMap), axis=1)
        traj.loc[:, 'ele[m]'] = expSmooth(traj['ele[m]'].to_list(), alpha=0.7)
    
    else:  # elevation from altitude column
        traj.loc[:, 'ele[m]'] = expSmooth(traj[eleCol].to_list(), alpha=0.7)
    
    # calculate road grade
    a, b = traj['ele[m]'].diff(-1), (traj[distCol])
    traj.loc[:, newCol] = 0
    traj.loc[:, newCol] = np.divide(a, b, where=b!=0)  # avoid distance=0
    traj.loc[:, newCol] = traj[newCol].apply(np.arctan)  # theta=arctan(grade)
    traj[newCol] = traj[newCol].astype('float32')

    traj.drop(['ele[m]'], axis=1, inplace=True)

    return traj

# -------------------------------------------------------

def dem2ele(dem):
    """
    Obtain elevation from DEM.
    """
    band = dem.GetRasterBand(1)
    eleMap = band.ReadAsArray()
    return eleMap


def eleMatch(
        traj_point:pd.DataFrame,
        dem,
        eleMap,
        lonCol='lon',
        latCol='lat',
):
    """
    Match elevation to traj points.
    """
    lon, lat = traj_point[lonCol], traj_point[latCol]
    x, y = geo2xy(dem, lon, lat)
    return eleMap[x][y]

def geo2pro(dem, lon, lat):
    """
    Transfer geo longitude, latitude to projected x, y
    """
    # projected and geographic reference system
    psr = osr.SpatialReference()
    psr.ImportFromWkt(dem.GetProjection())
    gsr = psr.CloneGeogCS()
    
    # coordinate transformer
    ct = osr.CoordinateTransformation(gsr, psr)
    coords = ct.TransformPoint(lat, lon)
    return coords[0], coords[1]


def pro2xy(dem, x, y):
    """
    Transfer projected coordinate to row,col in rasters .
    """
    x0, dx, dxy, y0, dyx, dy = dem.GetGeoTransform()
    # if dxy == dyx == 0:
    #     col = (x - x0) / dx
    #     row = (y - y0) / dy
    a = np.array([[dx, dxy], [dyx, dy]])
    b = np.array([x - x0, y - y0])
    col, row = np.linalg.solve(a, b)
    return int(row), int(col)


def geo2xy(dem, lon, lat):
    """
    Transfer geo longitude, latitude to row, col in rasters.
    """
    x, y = geo2pro(dem, lon, lat)
    row, col = pro2xy(dem, x, y)
    return row, col
