'''
@File    :   preprocess.py
@Time    :   2023/09/06 14:27:39
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   
'''

import numpy as np
import pandas as pd
from .geo import gcj02_to_wgs84, bd09_to_wgs84


def encode(
        df:pd.DataFrame,
        encodingCol=[],
        sortBy=[],
        originCRS='GCJ02',
):
    """
    Encoding data.
    df: trajectory data
    encodingCol: columns need encoding
    sortBy: columns to sort by, list
    originCRS: coordinate reference system of raw data
    """
    
    # encoding items
    if encodingCol:
        for col in encodingCol:
            df[col] = df[col].squeeze().map({item:id for id, item in enumerate(df[col].squeeze().unique())})
    
    # CRS transferring
    if originCRS == 'WGS84':
        pass
    elif originCRS == 'GCJ02':
        df['lon'] = df.apply(lambda row: np.float64(gcj02_to_wgs84(row['lon'], row['lat'])[0]), axis=1)
        df['lat'] = df.apply(lambda row: np.float64(gcj02_to_wgs84(row['lon'], row['lat'])[1]), axis=1)
    elif originCRS == 'BD09':
        df['lon'] = df.apply(lambda row: np.float64(bd09_to_wgs84(row['lon'], row['lat'])[0]), axis=1)
        df['lat'] = df.apply(lambda row: np.float64(bd09_to_wgs84(row['lon'], row['lat'])[1]), axis=1)
    else:
        raise KeyError("Tranferring from %s to WGS84 is not available." % originCRS)
    
    # sort
    if sortBy:
        df = df.sort_values(by=sortBy)
        df.reset_index(inplace=True, drop=True)
    
    return df


