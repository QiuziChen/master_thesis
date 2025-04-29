'''
@File    :   calculation.py
@Time    :   2023/09/06 12:08:54
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   
This module contains calculation functions to obtain distance, mileage and other information for trajectory.
'''

import math
import numpy as np
import pandas as pd
from tqdm import tqdm


def getDistByCoord(long1,lat1,long2,lat2):
    """
    Get distance (km) between two points.
    use the same method in google map (WSG-84)
    output: meters
    """
    if pd.isna([long1,lat1,long2,lat2]).any():
        return float("nan")
    else:
        earthRadius = 6378.137
        radLat1 = lat1 * math.pi / 180.0
        radLat2 = lat2 * math.pi / 180.0
        a = math.fabs((lat1-lat2)) * math.pi / 180.0
        b = math.fabs((long1-long2)) * math.pi / 180.0
        s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2),2) + math.cos(radLat1)*math.cos(radLat2)*math.pow(math.sin(b/2),2)))
        s = s * earthRadius
        # s = round(s * 10000) / 10000  # km
        return s * 1000
    

def getMileageByCoord(traj, lonCol='lon', latCol='lat'):
    """
    Get traj mileage using coordination.
    lonCol: column name of longitude
    latCol: column name of latitude
    """
    m = 0
    for i in range(traj.shape[0]-1):
        long1 = traj[lonCol].iloc[i]
        lat1 = traj[latCol].iloc[i]
        long2 = traj[lonCol].iloc[i+1]
        lat2 = traj[latCol].iloc[i+1]
        m += getDistByCoord(long1, lat1, long2, lat2)  # meters
    return m


def calDistInterval(
        traj:pd.DataFrame,
        lonCol='lon',
        latCol='lat',
        distColName='dist[m]',
        calDirect='forward'
):
    """
    Calculate adjacent distance between O-D coordinates in a row.
    lonCol: column name of longitude
    latCol: column name of latitude
    dsitColName: column name of the newly generated distance
    calDirect: calculate method
    'forward' means to calculate the distance with the later point,
    'backward' means to calculate the distance with the earlier point
    output: meters
    """
    traj = traj.copy()

    if calDirect == 'forward':
        traj['lon_'] = traj[lonCol].shift(-1)
        traj['lat_'] = traj[latCol].shift(-1)
    else:
        traj['lon_'] = traj[lonCol].shift(1)
        traj['lat_'] = traj[latCol].shift(1)    
    # distance between two point / km  
    traj.loc[:, distColName] = traj.apply(lambda row: getDistByCoord(row[lonCol], row[latCol], row['lon_'], row['lat_']), axis=1)
    traj.drop(['lon_', 'lat_'], axis=1, inplace=True)
   
    traj[distColName] = traj[distColName].astype('float32')

    return traj


def calTimeInterval(
        traj:pd.DataFrame,
        timeCol='time[s]',
        intervalColName='interval[s]',
        calDirect='forward'
):
    """
    Calculate adjacent time interval.
    timeCol: column name of time.
    intervalColName: column name of the newly generated interval.
    calDirect: calculate method.
    'forward' means to calculate the interval with the later point,
    'backward' means to calculate the interval with the earlier point
    """
    traj = traj.copy()

    if calDirect == 'forward':
        traj.loc[:, intervalColName] = traj[timeCol].diff().shift(-1)
    else:
        traj.loc[:, intervalColName] = traj[timeCol].diff()
    
    traj[intervalColName] = traj[intervalColName].astype('float32')

    return traj


def calSpeed(
        traj:pd.DataFrame, 
        intervalCol='interval[s]', 
        distCol='dist[m]', 
        speedColName='speed[km/h]', 
):
    """
    Calculate the [forward] speed from adjacent point.
    timeCol: column name of time in second or unix
    distCol: column name of adjacent distance
    speedColName: column name of the newly generated speed
    """
    traj = traj.copy()

    # speed [forward]
    traj.loc[:, speedColName] = traj[distCol] / traj[intervalCol] * 3.6
    traj[speedColName] = traj[speedColName].astype('float32')

    return traj


def calAcc(
        traj:pd.DataFrame,
        intervalCol='interval[s]',  
        speedCol='speed[km/h]',
        accColName='acc[m/s2]' 
):
    """
    Calculate the [forward] acceleration [m/s2] from adjacent point.
    timeCol: column name of time in second or unix.
    speedCol: column name of speed in km/h.
    accCol: column name of the newly generated accleration.
    """
    traj = traj.copy()

    traj.loc[:, accColName] = traj[speedCol].diff().shift(-1)
    traj.loc[:, accColName] = traj[accColName] / traj[intervalCol] / 3.6
    traj[accColName] = traj[accColName].astype('float32')

    return traj


def calVSP(
        traj:pd.DataFrame,
        speedCol='speed[km/h]',
        accCol='acc[m/s2]',
        gradeCol='grade[D]',
        VSPColName='VSP[kW/t]',
        weight=1.497,  # weight of LDV, mass/ton
):
    """
    Calculate VPS of each trajectory point.
    weight: weight of the vehicle in mass/ton
    speedCol: column name of speed in km/h    
    accCol: column name of acceleration in m/s2    
    gradeCol: column name of grade in degree    
    VSPColName: column name of the newly generated VSP
    """
    # VSP / kW/t
    A, B, C = 0.156461, 0.0020002, 0.000493
    g = 9.8  # m/s^2
    
    # traj.loc[:, 'v'] = traj[speedCol] / 3.6
    # traj.loc[:, 'v2'] = traj['v'].apply(lambda x: x**2)
    # traj.loc[:, 'v3'] = traj['v'] * traj['v2']
    # traj.loc[:, 'av'] = traj['v'] * traj[accCol]
    
    # # VSP with 0 grade
    # traj.loc[:, 'VSP0'] = traj.apply(lambda row: A/weight*row['v'] + B/weight*row['v2'] + C/weight*row['v3'] + row['av'], axis=1)
    # traj.drop(['v2', 'v3', 'av'], axis=1, inplace=True)
    
    traj = traj.copy()

    # VSP with 0 grade
    traj.loc[:, 'VSP0'] = traj.apply(
        lambda x: A / weight * (x[speedCol]/3.6)
                + B / weight * ((x[speedCol]/3.6)**2)
                + C / weight * ((x[speedCol]/3.6)**3)
                + (x[speedCol]/3.6) * x[accCol],
        axis=1
    )

    # # VSP with grade
    # traj.loc[:, 'sin'] = traj[gradeCol].apply(np.sin)  # sin(theta)
    # traj.loc[:, 'sin'] = traj['sin'] * traj['v'] * g   # g*sin(theta)*v
    # traj.loc[:, VSPColName] = traj['VSP0'] + traj['sin']
    
    if gradeCol:
        # VSP with grade
        traj.loc[:, VSPColName] = traj.apply(
            lambda x: x['VSP0'] + np.sin(x[gradeCol]) * (x[speedCol]/3.6) * g,
            axis=1
        )
        traj.drop(['VSP0'], axis=1, inplace=True)
    else:
        traj.rename(columns={'VSP0': VSPColName}, inplace=True)
    
    traj[VSPColName] = traj[VSPColName].astype('float32')

    return traj

