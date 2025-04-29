'''
@File    :   time.py
@Time    :   2024/05/21 11:27:42
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   
'''


import time
import pandas as pd


def encodeTime(
        traj:pd.DataFrame,
        timeCol:str,
        newCol:str,
        fromFormat:str,
        toFormat:str
) -> pd.DataFrame:
    """
    Encoding date and time.
    df: traj DataFrame
    timeCol: name of time column
    newCol: name of the new column
    fromFormat: format of the original time item, both unix time and format code in `time` package are supported.
    toFormat: formant of time item that is needed:
        - get str if choose `date`, `week`, or `time`;
        - get int if choose `hour of day`, `min of day`, `sec of day`;
        - self-defined time format according to the format code is also supported.
    """
    df = traj.copy()
    
    # from unix time
    if fromFormat == 'unix':

        if toFormat == 'datetime':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(t)))
        elif toFormat == 'date':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime("%Y/%m/%d", time.localtime(t)))
        elif toFormat == 'time':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime("%H:%M:%S", time.localtime(t)))
        elif toFormat == 'week':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime("%A", time.localtime(t)))
        elif toFormat == 'hour of day':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.localtime(t).tm_hour)
        elif toFormat == 'min of day':
            df[newCol] = df[timeCol].squeeze().map(minMap_unix)
        elif toFormat == 'sec of day':
            df[newCol] = df[timeCol].squeeze().map(timeSecMap_unix)
        else:  # to self-defined time format
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime(toFormat, time.localtime(t)))

    # from time format codes
    else:

        if toFormat == 'datetime':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(str(t), fromFormat)))
        elif toFormat == 'date':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime("%Y/%m/%d", time.strptime(str(t), fromFormat)))
        elif toFormat == 'time':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime("%H:%M:%S", time.strptime(str(t), fromFormat)))
        elif toFormat == 'week':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime("%A", time.strptime(str(t), fromFormat)))
        elif toFormat == 'hour of day':
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strptime(str(t), fromFormat).tm_hour)
        elif toFormat == 'min of day':
            df[newCol] = df[timeCol].squeeze().map(lambda t: minMap(str(t), fromFormat))
        elif toFormat == 'sec of day':
            df[newCol] = df[timeCol].squeeze().map(lambda t: timeSecMap(str(t), fromFormat))
        else:  # to self-defined time format
            df[newCol] = df[timeCol].squeeze().map(lambda t: time.strftime(toFormat, time.strptime(str(t), fromFormat)))

    return df

# ---------

def timeSecMap_unix(unixt):
    """
    Transfer unix time to second of the day.
    """
    t = time.localtime(unixt)
    return t.tm_hour*3600 + t.tm_min*60 + t.tm_sec

def minMap_unix(unixt):
    """
    Transfer unix time to minute of the day.
    """
    t = time.localtime(unixt)
    return t.tm_hour*60 + t.tm_min

def timeSecMap(t, format):
    """
    Transfer format time to second of the day.
    """
    t = time.strptime(t, format)
    return t.tm_hour*3600 + t.tm_min*60 + t.tm_sec

def minMap(t, format):
    """
    Transfer unix time to minute of the day.
    """
    t = time.strptime(t, format)
    return t.tm_hour*60 + t.tm_min

