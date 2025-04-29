'''
@File    :   rate.py
@Time    :   2023/11/12 15:14:44
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   Emission rate calculation.
'''


import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score


# ER data path
PATH_LM_POW_PARAM = "calculator/emission-data/LM_PM10_pow_param.npy"
PATH_NAO_POW_PARAM = "calculator/emission-data/NAO_PM10_pow_param.npy"
PATH_SM_POW_PARAM = "calculator/emission-data/SM_PM10_pow_param.npy"


def _pow(x, a, b):
    """
    Perform power function.
    """
    return a * np.power(x, b)


def calER(
        decel,
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
    Calculate emission rate according to deceleration.
    decel: deceleration value(s) number or ndarray.
    prop_NAO_f: share of NAO for front brake pads
    prop_LM_f: share of LM for front brake pads
    prop_SM_f: share of SM for front brake pads
    prop_NAO_r: share of NAO for rear brake pads
    prop_LM_r: share of LM for rear brake pads
    prop_SM_r: share of SM for rear brake pads
    prop_drum_f: share of drum brake for front brake
    prop_drum_r: share of drum brake for rear brake
    r_f_ratio: brake force on front axle vs rear axle
    drum_disc_ratio: ratio of drum emissions to disc emissions 
    """
    # load params of ER-decel curves
    LM_POW_PARAM = np.load(PATH_LM_POW_PARAM)
    NAO_POW_PARAM = np.load(PATH_NAO_POW_PARAM)
    SM_POW_PARAM = np.load(PATH_SM_POW_PARAM)

    # mix for disc brake
    ER_f_disc = (_pow(decel, *NAO_POW_PARAM) * prop_NAO_f) \
                + (_pow(decel, *LM_POW_PARAM) * prop_LM_f) \
                + (_pow(decel, *SM_POW_PARAM) * prop_SM_f)
    ER_r_disc = (_pow(decel, *NAO_POW_PARAM) * prop_NAO_r) \
                + (_pow(decel, *LM_POW_PARAM) * prop_LM_r) \
                + (_pow(decel, *SM_POW_PARAM) * prop_SM_r)
    ER_r_disc *= r_f_ratio
        
    # adjust for axles
    ER_f_drum = ER_f_disc * drum_disc_ratio
    ER_r_drum = ER_r_disc * drum_disc_ratio

    # mix for veh
    ER = (1 - prop_drum_f) * ER_f_disc \
        + prop_drum_f * ER_f_drum \
        + (1 - prop_drum_r) * ER_r_disc \
        + prop_drum_r * ER_r_drum
    ER *= 2
    
    return ER  


def fitCurve(
        decel,
        er,
):
    """
    Fit the ER-deceleration curve with input data and power function.

    """
    def func(x, a, b):
        return a * (x ** b)
    
    xdata = decel
    ydata = er
    params, cov = curve_fit(func, xdata, ydata)
    score = r2_score(ydata, func(xdata, params[0], params[1]))
    
    return params, score