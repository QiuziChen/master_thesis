'''
@File    :   densification.py
@Time    :   2023/09/29 20:47:06
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   Provide tools for trajectory densification including interpolation and smoothing.
'''


import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.interpolate import interp1d
from multiprocessing import Pool, cpu_count


def densifyUnit(
        traj:pd.DataFrame,
        lonCol:str,
        latCol:str,
        timeCol:str,
        interpFunc='cubic'
):
    """
    Densify a trip trajectory.
    lonCol: column name of longitude.
    latCol: column name of latitude.
    timeCol: column name of time.
    interpFunc: interpolation method.
    - see scipy.interpolate.interp1d doc: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html#scipy.interpolate.interp1d>
    """
    traj = traj.copy()

    # advoid duplication
    traj.drop_duplicates(keep='first', inplace=True)
    
    # create cubic spline function
    lon = traj[lonCol]
    lat = traj[latCol]
    time = traj[timeCol]

    if len(time) == 1:
        return traj
    elif len(time) > 3:
        interpLon = interp1d(time, lon, interpFunc)
        interpLat = interp1d(time, lat, interpFunc)
    else:  # if only contain two points, use linear interpolation
        interpLon = interp1d(time, lon, 'linear')
        interpLat = interp1d(time, lat, 'linear')
    
    # number of points in the path
    pathLen = int(traj.iloc[-1][timeCol] - traj.iloc[0][timeCol] + 1)
    
    # time sequence
    time_ = np.array([traj.iloc[0][timeCol] + i for i in range(pathLen)])

    # other columns
    otherCol = traj.columns.to_list()
    otherCol.remove(lonCol)
    otherCol.remove(latCol)

    # generate new traj
    trajDict = {}
    trajDict[timeCol] = time_
    trajDict[lonCol] = interpLon(time_)
    trajDict[latCol] = interpLat(time_)

    # merge with other columns
    traj = pd.merge(pd.DataFrame(trajDict), traj[otherCol], how='left', on=timeCol)
    traj.interpolate(method='linear', inplace=True)
    return traj

def densify(
        traj:pd.DataFrame,
        lonCol:str,
        latCol:str,
        timeCol:str,
        segCol:str,
        sortBy:list,
        **kwargs
):
    """
    Densify the trajectory (longitude and latitude).
    lonCol: column name of longitude.
    latCol: column name of latitude.
    timeCol: column name of time.
    segCol: column name of segments (trip ID or car ID), if None, densify the traj as a whole trip.
    sortBy: reference cols for sorting trajectory point, list.
    """
    traj = traj.copy()
    
    length0 = traj.shape[0]
    # perform densification for each trip seperately
    if segCol: 

        trips = []
        for id in tqdm(set(traj[segCol].unique()), desc="Densifying"):
            # select trip from traj.df
            trip = traj[traj[segCol] == id].copy()
            trips.append(densifyUnit(trip, lonCol=lonCol, latCol=latCol, timeCol=timeCol, **kwargs))
            
        # concat
        traj = pd.concat(trips)
    
        # sort
        traj = traj.sort_values(by=sortBy)
        traj.reset_index(inplace=True, drop=True)
    
    # perform densification for the whole traj.df
    else:  
        traj = densifyUnit(traj, lonCol=lonCol, latCol=latCol, timeCol=timeCol, **kwargs)

    length1 = traj.shape[0]
    print("- densified length: %d;\n- densified ratio: %.2f%%." % (length1, length1/length0*100))
    return traj

# def densify(
#         traj:pd.DataFrame,
#         timeCol='time[s]',
#         tripIDCol='tripID',
#         sortBy=['vehID', 'tripID', 'time[s]'],
#         **kwargs
# ):
#     """
#     Densify the trajectory.
#     timeCol: column name of time.
#     tripIDCol: column name of tripID, if None, densify the traj as a whole trip.
#     sortBy: reference cols for sorting trajectory point.
#     """
#     # perform densification for each trip seperately
#     if tripIDCol:  
#         for id in tqdm(set(traj[tripIDCol].unique()), desc="Densifying trip No. "):
#             # select trip from traj.df
#             trip = traj[traj[tripIDCol] == id].copy()
#             # concat
#             traj = pd.concat([
#                 traj,
#                 densifyUnit(
#                     trip,
#                     timeCol=timeCol,
#                     **kwargs
#                 )
#             ])
#             # remove duplication
#             traj.drop_duplicates(subset=[tripIDCol, timeCol], keep='first', inplace=True)
        
#         # sort
#         traj = traj.sort_values(by=sortBy)
#         traj.reset_index(inplace=True, drop=True)
    
#     # perform densification for the whole traj.df
#     else:  
#         traj = densifyUnit(
#             traj,
#             timeCol=timeCol,
#             **kwargs
#         )

#     return traj