'''
@File    :   MOVES.py
@Time    :   2023/10/15 14:25:45
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   A module containing toolkits and methods provided by MOVES.
'''


import pandas as pd
import numpy as np


def OpModeDetect(
        traj:pd.DataFrame,
        gradeCol='grade[D]',
        speedCol='speed[km/h]',
        accCol='acc[m/s2]',
        VSPCol='VSP[kW/t]',
        OpModeColName="OpModeID"
):
        """
        Detect Operating Mode for each traj point.
        traj: trajectory DataFrame.
        gradeCol: column name of grade.
        speedCol: column name of speed.
        accCol: column name of acc.
        VSPCol: column name of VSP.
        """
        traj = traj.copy()
        traj[OpModeColName] = None

        g = 9.8
        traj['acc_grade'] = traj[accCol] + g * np.sin(np.arctan(traj[gradeCol]))
        traj['acc_grade_t-1'] = traj['acc_grade'].shift(1)
        traj['acc_grade_t-2'] = traj['acc_grade'].shift(2)

        traj.loc[(traj['acc_grade']<=-0.894) | ((traj['acc_grade']<-0.447) & (traj['acc_grade_t-1']<-0.447) & (traj['acc_grade_t-2']<-0.447)), OpModeColName] = 0

        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]<1.609), OpModeColName] = 1

        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=1.609) & (traj[speedCol]<40.234) & (traj[VSPCol]<0), OpModeColName] = 11
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=1.609) & (traj[speedCol]<40.234) & (traj[VSPCol]>=0) & (traj[VSPCol]<3), OpModeColName] = 12
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=1.609) & (traj[speedCol]<40.234) & (traj[VSPCol]>=3) & (traj[VSPCol]<6), OpModeColName] = 13
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=1.609) & (traj[speedCol]<40.234) & (traj[VSPCol]>=6) & (traj[VSPCol]<9), OpModeColName] = 14
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=1.609) & (traj[speedCol]<40.234) & (traj[VSPCol]>=9) & (traj[VSPCol]<12), OpModeColName] = 15
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=1.609) & (traj[speedCol]<40.234) & (traj[VSPCol]>=12), OpModeColName] = 16

        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]<0), OpModeColName] = 21
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]>=0) & (traj[VSPCol]<3), OpModeColName] = 22
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]>=3) & (traj[VSPCol]<6), OpModeColName] = 23
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]>=6) & (traj[VSPCol]<9), OpModeColName] = 24
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]>=9) & (traj[VSPCol]<12), OpModeColName] = 25
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]>=12) & (traj[VSPCol]<18), OpModeColName] = 27
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]>=18) & (traj[VSPCol]<24), OpModeColName] = 28
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]>=24) & (traj[VSPCol]<30), OpModeColName] = 29
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=40.234) & (traj[speedCol]<80.467) & (traj[VSPCol]>=30), OpModeColName] = 30

        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=80.467) & (traj[VSPCol]<6), OpModeColName] = 33
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=80.467) & (traj[VSPCol]>=6) & (traj[VSPCol]<12), OpModeColName] = 35
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=80.467) & (traj[VSPCol]>=12) & (traj[VSPCol]<18), OpModeColName] = 37
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=80.467) & (traj[VSPCol]>=18) & (traj[VSPCol]<24), OpModeColName] = 38
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=80.467) & (traj[VSPCol]>=24) & (traj[VSPCol]<30), OpModeColName] = 39
        traj.loc[(traj['acc_grade']>-0.894) & (traj[speedCol]>=80.467) & (traj[VSPCol]>=30), OpModeColName] = 40


        traj.drop(['acc_grade', 'acc_grade_t-1', 'acc_grade_t-2'], inplace=True, axis=1)

        return traj


def getDecelBinProp(data, accBins):
    """
    Obtain counts for each brake deceleration bin.
    """
    # interval = 0.1
    # bins = np.arange(interval, 4.6, interval)
    # count_list = [traj[(traj[accCol] > -bin) & (traj[accCol] <= -bin+interval)].shape[0] for bin in bins]
    if len(data) == 0:
          return np.zeros_like(accBins[:-1])
    else:
        weights = np.ones_like(data)
        hist, bin_edges = np.histogram(data, bins=accBins, weights=weights)
        prop = hist / np.sum(weights)
        return prop


def OpModeAgg(
    traj:pd.DataFrame,
    OpModeCol='OpModeID',
    brakeCol='braking',
    accCol='acc[m/s2]',
    accBins = np.arange(-4.6, 0.1, 0.1)
):
        """
        Aggregate information of each OpMode.
        """
        # generate index
        OpModeID_list = [0,1,11,12,13,14,15,16,21,22,23,24,25,27,28,29,30,33,35,37,38,39,40]

        # define agg file
        df_agg = pd.DataFrame(
                columns=['trajCount', 'brakeCount', 'brakeFrac', 'brakeDecelBinProp'],
                index=OpModeID_list
        )
        df_agg.loc[:,:] = 0

        # start aggregating
        for id in OpModeID_list:
                df = traj[(traj[OpModeCol] == id)].copy()
                df_agg.loc[id]['trajCount'] = df.shape[0]
                df_agg.loc[id]['brakeCount'] = df[df[brakeCol]==True].shape[0]
                df_agg.loc[id]['brakeFrac'] = df[df[brakeCol]==True].shape[0] / df.shape[0] if df.shape[0] != 0 else 0
                df_agg.loc[id]['brakeDecelBinProp'] = getDecelBinProp(df[df[brakeCol]==True][accCol].values, accBins)

        return df_agg