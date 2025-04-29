'''
@File    :   trajtool.py
@Time    :   2024/05/19 18:08:33
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   
'''


import pandas as pd
from .time import encodeTime
from .densification import densify
from .plot import plot_traj, plot_heat, plot_series
from .calculation import getMileageByCoord
from .calculation import calDistInterval, calTimeInterval
from .calculation import calSpeed, calAcc, calVSP
from.grade import calGrade
from .smoothing import smooth1D, smooth2D
from .segmentation import segment_time_intv


class TrajTool():
    """
    
    """
    def __init__(self) -> None:
        pass

    def encode_time(
            self,
            traj:pd.DataFrame,
            timeCol:str,
            newCol:str,
            fromFormat:str,
            toFormat:str
    ):
        """
        Encoding date and time.
        traj: traj DataFrame
        timeCol: name of time column
        newCol: name of the new column
        fromFormat: format of the original time item, both unix time and format code in `time` package are supported.
        toFormat: formant of time item that is needed:
            - get str if choose `date`, `week`, or `time`;
            - get int if choose `hour of day`, `min of day`, `sec of day`;
            - self-defined time format according to the format code is also supported.
        """
        return encodeTime(traj, timeCol, newCol, fromFormat, toFormat)

    def densify(
            self,
            traj:pd.DataFrame,
            lonCol:str,
            latCol:str,
            timeCol:str,
            segCol=None,
            sortBy=None,
            **kwargs
    ):
        """
        Densify the trajectory (longitude and latitude).
        traj: traj DataFrame
        lonCol: column name of longitude.
        latCol: column name of latitude.
        timeCol: column name of time.
        segCol: column name of segments (trip ID or car ID), if None, densify the traj as a whole trip.
        sortBy: reference cols for sorting trajectory point, list.
        """
        return densify(traj, lonCol, latCol, timeCol, segCol, sortBy, **kwargs)
    
    def cal_mileage(
            self,
            traj:pd.DataFrame,
            lonCol:str,
            latCol:str,
            segCol=None
    ) -> dict:
        """
        Calculate mileage of trips.
        traj: traj DataFrame
        lonCol: column name of longitude.
        latCol: column name of latitude.
        segCol: column name of segments (trip ID or car ID), if None, calculate mileage for the traj as a whole trip.
        """
        if segCol:
            mi = {
                id:getMileageByCoord(traj[traj[segCol]]==id, lonCol, latCol)
                for id in traj[segCol].unique().to_list()
            }
            return mi
        else:
            return {0: getMileageByCoord(traj, lonCol, latCol)}

    def cal_interval(
            self,
            traj:pd.DataFrame,
            lonCol:str=None,
            latCol:str=None,
            timeCol:str=None,
            newDistCol:str=None,
            newTimeCol:str=None,
            calDist=True,
            calTime=True,
            calDirect='forward'
    ) -> pd.DataFrame:
        """
        Calculate adjacent distance and time gap between O-D coordinates in a row.
        lonCol: column name of longitude
        latCol: column name of latitude
        dsitColName: column name of the newly generated distance
        calDirect: calculate method
        'forward' means to calculate the distance with the later point,
        'backward' means to calculate the distance with the earlier point
        """
        traj = traj.copy()
        if calDist:
            traj = calDistInterval(traj, lonCol, latCol, newDistCol, calDirect)
        if calTime:
            traj = calTimeInterval(traj, timeCol, newTimeCol, calDirect)
        return traj

    def cal_grade(
            self,
            traj:pd.DataFrame,
            lonCol:str,
            latCol:str,
            distIntCol:str,
            eleCol=None,
            newCol='grade[D]',
            fromDEM=False,
            dem=None,
    ):
        """
        Match elevation to traj points and calculate the grade.
        distIntCol: column name of dist interval, meter.
        eleCol: column name of elevation, if fromDEM is True, then set eleCol to None.
        fromDEM: if True, extract elevation and grade from DEM.
        dem: if fromDEM is True, input the DEM file.
        newCol: name of the new grade column.
        """
        return calGrade(traj, lonCol, latCol, distIntCol, eleCol, newCol, fromDEM, dem)

# TODO: calculate single params

    def cal_speed(
            self,
            traj:pd.DataFrame,
            timeIntCol:str,
            distIntCol:str,
            newSpeedCol='speed[km/h]',
    ):
        """
        traj: trajectory data
        timeIntCol: column name of time interval
        distIntCol: column name of distance interval
        gradeCol: column name of road grade
        newSpeedCol: column name of the newly generated speed
        newAccCol: column name of the newly generated acceleration
        newVSPCol: column name of the newly generated VSP
        weight: weight of the vehicle [kg]
        """
        traj = traj.copy()
        traj = calSpeed(traj, timeIntCol, distIntCol, newSpeedCol)

        return traj

    def cal_acc(
            self,
            traj:pd.DataFrame,
            timeIntCol:str,
            speedCol='speed[km/h]',
            newAccCol='acc[m/s2]',
    ):
        """
        traj: trajectory data
        timeIntCol: column name of time interval
        speedCol: column name of speed
        newAccCol: column name of the newly generated acceleration
        """
        traj = traj.copy()
        traj = calAcc(traj, timeIntCol, speedCol, newAccCol)

        return traj

    def cal_VSP(
            self,
            traj:pd.DataFrame,
            speedCol='speed[km/h]',
            accCol='acc[m/s2]',
            newVSPCol='VSP[kW/t]',
            gradeCol=None,
            weight=1.497,  # weight of LDV, mass/ton
    ):
        """
        traj: trajectory data
        timeIntCol: column name of time interval
        distIntCol: column name of distance interval
        gradeCol: column name of road grade
        newSpeedCol: column name of the newly generated speed
        newAccCol: column name of the newly generated acceleration
        newVSPCol: column name of the newly generated VSP
        weight: weight of the vehicle [kg]
        """
        traj = traj.copy()
        traj = calVSP(traj, speedCol, accCol, gradeCol, newVSPCol, weight)

        return traj

    def cal_params(
            self,
            traj:pd.DataFrame,
            timeIntCol:str,
            distIntCol:str,
            gradeCol=None,
            newSpeedCol='speed[km/h]',
            newAccCol='acc[m/s2]',
            newVSPCol='VSP[kW/t]',
            weight=1.497,  # weight of LDV, mass/ton
    ):
        """
        traj: trajectory data
        timeIntCol: column name of time interval
        distIntCol: column name of distance interval
        gradeCol: column name of road grade
        newSpeedCol: column name of the newly generated speed
        newAccCol: column name of the newly generated acceleration
        newVSPCol: column name of the newly generated VSP
        weight: weight of the vehicle [kg]
        """
        traj = traj.copy()
        traj = calSpeed(traj, timeIntCol, distIntCol, newSpeedCol)
        traj = calAcc(traj, timeIntCol, newSpeedCol, newAccCol)
        traj = calVSP(traj, weight, newSpeedCol, newAccCol, gradeCol, newVSPCol)

        return traj

    def smooth(
            self,
            traj:pd.DataFrame,
            smoothCol,
            newCol,
            segCol=None,
            smoothFunc='exp',
            **params
    ):
        """
        
        """
        return smooth1D(traj, smoothCol, newCol, segCol, smoothFunc, **params)
    
    def smooth_traj(
            self,
            traj:pd.DataFrame,
            lonCol,
            latCol,
            timeCol,
            newLonCol,
            newLatCol,
            segCol=None,
            smoothFunc='kal2D',
            **params 
    ):
        """
        Use Kalman filter to smooth trajectory (x,y) or (lon, lat).
        """
        return smooth2D(traj, lonCol, latCol, timeCol, newLonCol, newLatCol, segCol, smoothFunc, **params)

    def segment_timeIntv(
            self,
            traj:pd.DataFrame,
            timeIntCol:str,
            newCol='segID',
            maxInterval=2,
    ):
        """
        """
        return segment_time_intv(traj, timeIntCol, newCol, maxInterval)


    def plot_traj(
            self,
            traj:pd.DataFrame,
            lonCol:str,
            latCol:str,
            linecolor='red',
            linewidth=1,
            markersize=20,
            basemap=True,
            segCol=None,
            figsize=(5,5),
            axis=False,
            **kwargs
    ):
        """
        
        """
        plot_traj(traj, lonCol, latCol, linecolor, linewidth, markersize, basemap, segCol, figsize, axis, **kwargs)
    
    def plot_heat(
            self,
            traj:pd.DataFrame,
            lonCol:str,
            latCol:str,
            heatCol:str,
            cmap='Spectral_r',
            linecolor='grey',
            linewidth=1,
            markersize=10,
            basemap=True,
            figsize=(5,5),
            axis=False,
            **kwargs    
    ):
        """
        
        """
        plot_heat(traj, lonCol, latCol, heatCol, cmap, linecolor, linewidth, markersize, basemap, figsize, axis, **kwargs)

    def plot_series(
            self,
            traj:pd.DataFrame,
            plotCol:list,
            timeCol,
            segCol=None,
            subplots=True,
            figsize=(5,3)
    ):
        """
        
        """
        plot_series(traj, plotCol, timeCol, segCol, subplots, figsize)
