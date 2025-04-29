'''
@File    :   traj.py
@Time    :   2023/09/21 20:02:10
@Author  :   Qiuzi Chen 
@Version :   1.0.1
@Contact :   qiuzi.chen@outlook.com
@Desc    :   Class Traj, packing preprocessing tools
'''


import pandas as pd
from .encoding import encode, encodeTime
from .filtering import filter
from .segmentation import segment
from .densification import densify, densifyUnit
from .calculation import calParam, calParamUnit
from .smoothing import smooth


class TrajTool():
    """
    Contains functions for trajectory preprocessing and calculation.
    """
    def __init__(
            self,
    ) -> None:
        """
        A DataFrame of trajectory is necessary for initialize a Preprocess object.
        """
        pass

    def encode(
            self,
            traj:pd.DataFrame,
            encodingCol=[],
            sortBy=[],
            originCRS='GCJ02',
    ):
        """
        Encoding, and coordinate transform.
        traj: trajectory DataFrame.
        encodingCol: columns need encoding, list
        sortBy: columns to sort by, list
        originCRS: coordinate reference system of raw data
        """        
        return encode(traj, encodingCol, sortBy, originCRS)

    # def filter(self, traj:pd.DataFrame):
    #     """
    #     Filtering.
    #     traj: trajectory DataFrame.
    #     """
    #     if self.__filtered__:
    #         raise Warning("The trajectory had already been filtered. Re-filtering could raise potential error.")
    #     self.__filtered__ = True
        
    #     return filter(traj, **self.__filterParam__)

    # def segment(self, traj:pd.DataFrame):
    #     """
    #     Trip segmentation.
    #     traj: trajectory DataFrame.
    #     """
    #     if self.__segmented__:
    #         raise Warning("The trajectory had already been segmented. Re-segmentation could raise potential error.")
    #     self.__segmented__ = True

    #     return segment(traj, **self.__segmentParam__)

    def densify(
            self,
            traj:pd.DataFrame,
            lonCol='lon',
            latCol='lat',
            timeCol='time[s]',
            interpFunc='cubic'
    ):
        """
        Densify the trajectory of trips by interpolation.
        traj: trajectory DataFrame.
        lonCol: column name of longitude.
        latCol: column name of latitude.
        timeCol: column name of time.
        interpFunc: interpolation method.
        - see scipy.interpolate.interp1d doc: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html#scipy.interpolate.interp1d>
        """
        return densify(traj, lonCol, latCol, timeCol, interpFunc)

    # def calParam(self, traj:pd.DataFrame):
    #     """
    #     Calculate parameters.
    #     traj: trajectory DataFrame.
    #     demPath: path of the DEM file
    #     """
    #     if self.__calculated__:
    #         raise Warning("The trajectory had already been calculated. Re-calculation could raise potential error.")
    #     self.__calculated__ = True

    #     return calParam(traj, **self.__calculateParam__)

    def cal

    def smooth(self, traj:pd.DataFrame):
        """
        Smooth the data sequence.

        """
        return smooth(traj, **self.__smoothParam__)
        
    # # TODO: adjusted encodeTime func for multi-time-format
    # def encodeTime(self, traj:pd.DataFrame):
    #     """
    #     Encoding date and time.
    #     """
    #     return encodeTime(traj, **self.__encodeTimeParam__)

    def pipe(
            self,
            traj:pd.DataFrame,
            steps=['encode', 'filter', 'segment', 'densify', 'calculate', 'smooth', 'encodeTime']
    ):
        """
        A sequence of preprocessing steps.
        traj: trajectory dataframe.
        steps: sequence of preprocessing steps.
        """
        traj = traj.copy()

        self.funcNameDict = {
            'encode': self.encode,
            'filter': self.filter,
            'segment': self.segment,
            'densify': self.densify,
            'calculate': self.calParam,
            'smooth': self.smooth,
            'encodeTime': self.encodeTime,
        }
        
        traj = traj.copy()
        for step in steps:
            func = self.funcNameDict[step]
            traj = func(traj)
        
        return traj


