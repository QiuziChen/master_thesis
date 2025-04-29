'''
@File    :   BWEToolkit.py
@Time    :   2023/11/16 11:53:15
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   Provide modelling and calculation toolkits for BWE.
'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .braking import coastDownDetect
from .opmode import OpModeDetect, OpModeAgg, getDecelBinProp
from .er import calER, fitCurve
from .calculation import calTimeInterval, calDistInterval, calSpeed, calAcc, calVSP


class ERCalculator():
    """
    Toolkits for brake wear particle emission rate calculation.
    """
    def __init__(self) -> None:
        """
        Initialization a BWP emission calculation toolkit.
        """
        self.BRAKE_DECEL_BIN = np.arange(-4.5, 0.1, 0.1)
        
    def brakingDetect(
            self, 
            traj:pd.DataFrame,
            speedCol="speed[km/h]",
            accCol="acc[m/s2]",
            brakeColName="braking",
    ):
        """
        Determine whether braking event is happening according to braking detect models.
        f: trajectory DataFrame.
        speedCol: column name of speed.
        accCol: column name of acceleration.
        brakeColName: name of the newly derived column
        """
        return coastDownDetect(traj, speedCol, accCol, brakeColName)
    

    def OpModeDetect(
            self,
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
        return OpModeDetect(traj, gradeCol, speedCol, accCol, VSPCol, OpModeColName)
    

    def calOpModeERs(
            self,
            OpModesInfo:pd.DataFrame,
            decelBins,
            brakeFracCol='brakeFrac',
            decelPropCol='brakeDecelBinProp',
            prop_NAO_f = 0.7974,
            prop_LM_f = 0.1775,
            prop_SM_f = 0.0251,
            prop_NAO_r = 0.8186,
            prop_LM_r = 0.1755,
            prop_SM_r = 0.0058,
            prop_drum_f = 0,
            prop_drum_r = 0.2228,
            r_f_ratio = 0.5,
            drum_disc_ratio = 0.3
    ):
        """
        Calculate emission rates of each OpModes. 
        OpModesInfo: information for OpModes, should include:
            - braking fraction: ratio of braking events in each OpMode
            - deceleration distribution, e.g., [0.35, 0.25, 0.15,...]
        """
        def calERFunc(decel):
            return calER(
                decel,
                prop_NAO_f, prop_LM_f, prop_SM_f,
                prop_NAO_r, prop_LM_r, prop_SM_r,
                prop_drum_f, prop_drum_r,
                r_f_ratio, drum_disc_ratio
            )
        results = OpModesInfo.copy()
        results['ER[g/hr/veh]'] = results.apply(lambda x: sum(calERFunc(-decelBins[:-1]) * x[decelPropCol] * x[brakeFracCol]), axis=1)
        results.fillna(0, inplace=True)
        return results


    def calMOVESERs(
            self,
            OpModesInfo:pd.DataFrame,
            decelBins,
            brakeFracCol='brakeFrac',
            brakeCountCol='brakeCount',
            decelPropCol='brakeDecelBinProp',
            prop_NAO_f = 0.7974,
            prop_LM_f = 0.1775,
            prop_SM_f = 0.0251,
            prop_NAO_r = 0.8186,
            prop_LM_r = 0.1755,
            prop_SM_r = 0.0058,
            prop_drum_f = 0,
            prop_drum_r = 0.2228,
            r_f_ratio = 0.5,
            drum_disc_ratio = 0.3
    ):
        """
        Calculate emission rates of each OpModes. 
        OpModesInfo: information for OpModes, should include:
            - braking fraction: ratio of braking events in each OpMode
            - deceleration distribution, e.g., [0.35, 0.25, 0.15,...]
        """
        def calERFunc(decel):
            return calER(
                decel,
                prop_NAO_f, prop_LM_f, prop_SM_f,
                prop_NAO_r, prop_LM_r, prop_SM_r,
                prop_drum_f, prop_drum_r,
                r_f_ratio, drum_disc_ratio
            )
        results = OpModesInfo.copy()
        overallDecelBinProp = sum(results[decelPropCol] * results[brakeCountCol]) / sum(results[brakeCountCol])
        results['ER_MOVES[g/hr/veh]'] = results.apply(lambda x: sum(calERFunc(-decelBins[:-1]) * overallDecelBinProp * x[brakeFracCol]), axis=1)
        results.fillna(0, inplace=True)
        return results


    def calCycleBWP(
        self,
        data:pd.DataFrame,
        timeCol:str,
        speedCol:str,
        **kwargs 
    ):
        """
        Calculate BWP
        data: drive cycle profile
        timeCol: name of time column
        speedCol: name of speed column (km/h)
        """
        # preprocessing
        cycle = data.copy()
        cycle = calTimeInterval(cycle, timeCol, calDirect='forward')
        cycle.loc[:, 'grade[D]'] = 0
        cycle = calAcc(cycle, speedCol=speedCol)
        cycle = calVSP(cycle, speedCol=speedCol)

        # braking detection
        cycle = self.brakingDetect(cycle, speedCol=speedCol)

        # OpMode detect
        cycle = self.OpModeDetect(cycle, speedCol=speedCol)
        cycle.dropna(inplace=True)

        # OpMode ERs
        OpModesInfo = OpModeAgg(cycle, accBins=self.BRAKE_DECEL_BIN)
        OpModesInfo = self.calOpModeERs(OpModesInfo=OpModesInfo, decelBins=self.BRAKE_DECEL_BIN, **kwargs)
        OpModesInfo = self.calMOVESERs(OpModesInfo=OpModesInfo, decelBins=self.BRAKE_DECEL_BIN, **kwargs)

        # cal BWP
        mileage = sum(cycle[speedCol] * cycle['interval[s]']) / 3600  # km
        duration = cycle.shape[0] / 3600  # hour
        total_BWP = sum(OpModesInfo['ER[g/hr/veh]'] * OpModesInfo['trajCount']) / 3600  # g
        total_BWP_MOVES = sum(OpModesInfo['ER_MOVES[g/hr/veh]'] * OpModesInfo['trajCount']) / 3600  # g
        avg_ER = total_BWP / duration  # g/hr
        avg_ER_MOVES = total_BWP_MOVES / duration  # g/hr
        avg_EF = total_BWP / mileage * 1000  # mg/km
        avg_EF_MOVES = total_BWP_MOVES / mileage * 1000  # mg/km
        BWP_dict = {
            'duration[h]': duration,
            'mileage[km]': mileage,
            'BWP[g]': total_BWP,
            'avgER[g/h]': avg_ER,
            'avgEF[mg/km]': avg_EF,
            'BWP_MOVES[g]': total_BWP_MOVES,
            'avgER_MOVES[g/h]': avg_ER_MOVES,
            'avgEF_MOVES[mg/km]': avg_EF_MOVES,
        }

        return cycle, OpModesInfo, BWP_dict

    def fitCurves(
            self,
            data:pd.DataFrame,
            materialCol='Material',
            decelCol='Decel[m/s2]',
            ERCol='PM10ER[g/hr/brake]',
    ):
        """
        data: summary of emission rate data, three columns are required:
            - material: include three types: LM, NAO, SM
            - deceleration: average deceleration rate, m/s2
            - ER: emission rate, g/hr/brake 
        """
        # fit for each material
        for material in ['LM', 'NAO', 'SM']:
            material_data = data[data[materialCol] == material]
            decel = material_data[decelCol]
            er = material_data[ERCol]
            params, score = fitCurve(decel, er)
            
            # print
            print(f"Material: {material}, a = {params[0]:.4f}, b = {params[1]:.4f}, $R^2$ = {score:.4f}")
            print("-" * 30)
            
            # plot
            plt.figure()
            plt.scatter(decel, er)
            decels = np.arange(0, 8, 0.1)
            plt.plot(decels, params[0] * decels ** params[1], label=f'Fit: $a={params[0]:.2f}, b={params[1]:.2f}, R^2={score:.2f}$')
            plt.xlabel('Deceleration (m/s2)')
            plt.ylabel('PM10 ER (g/hr/brake)')
            plt.title(f'Material: {material}')
            plt.legend()
            plt.show()

            # update params
            if material == 'LM':
                self.LM_POW_PARAM = params
            elif material == 'NAO':
                self.NAO_POW_PARAM = params
            elif material == 'SM':
                self.SM_POW_PARAM = params