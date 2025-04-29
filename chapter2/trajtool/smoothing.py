'''
@File    :   smoothing.py
@Time    :   2023/09/06 14:23:29
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   
This module includes three smoothing methods for trajectory and indices:
- Kalman filter smooth
- exponential smooth
- double exponential smooth
'''


import numpy as np
from pykalman import KalmanFilter
from tqdm import tqdm


def KalmanSmooth_1D(indices:list, process_var=0.01, measure_var=0.01):
    """
    Smooth the indices using Kalman Filter 1D.
    process_var: process variance
    measure_var: measure variance
    """
    n = len(indices)
    size = (n,)

    # parameters
    Q = process_var  # process variance
    R = measure_var  # measure variance
    
    # initialize arrays
    xhat_ = np.zeros(size)  # a priori estimate of x
    xhat = np.zeros(size)  # a posteriori estimate of x
    P_ = np.zeros(size)  # a priori error estimate
    P = np.zeros(size)  # a posteriori error estimate
    K = np.zeros(size)  # gain factor

    xhat[0] = indices[0]
    P[0] = 1

    for k in range(1, n):
        # time update
        xhat_[k] = xhat[k-1]
        P_[k] = P[k-1] + Q

        # measurement update
        K[k] = P_[k] / (P_[k] + R)
        xhat[k] = xhat_[k] + K[k] * (indices[k] - xhat_[k])
        P[k] = (1 - K[k]) * P_[k]

    return xhat

def KalmanSmooth_2D(observations, timestamps, process_var=0.01, measure_var=0.00002):
    """
    Smooth the indices using Kalman Filter 1D.
    observations:
    timestamps:
    process_var: process variance
    measure_var: measure variance

    return: smoothed_states
    """
    transition_matrix = np.array([[1, 0, 1, 0],
                                  [0, 1, 0, 1],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])
    observation_matrix = np.array([[1, 0, 0, 0],
                                   [0, 1, 0, 0]])
    if isinstance(measure_var, list):
        observation_covariance = np.diag(measure_var)**2
    else:
        observation_covariance = np.eye(2) * measure_var**2
    if isinstance(process_var, list):
        transition_covariance = np.diag(process_var)**2
    else:
        transition_covariance = np.eye(4) * process_var**2

    # initial
    initial_state_mean = [observations[0, 0], observations[0, 1], 0, 0]
    initial_state_covariance = np.eye(4) * 1
    kf = KalmanFilter(
        transition_matrices=transition_matrix,
        observation_matrices=observation_matrix,
        initial_state_mean=initial_state_mean,
        initial_state_covariance=initial_state_covariance,
        observation_covariance=observation_covariance,
        transition_covariance=transition_covariance
    )

    # smooth
    smoothed_states = np.zeros((len(observations), 4))
    smoothed_states[0, :] = initial_state_mean
    current_state = initial_state_mean
    current_covariance = initial_state_covariance
    
    for i in range(1, len(observations)):
        dt = timestamps.iloc[i] - timestamps.iloc[i - 1]
        kf.transition_matrices = np.array([[1, 0, dt, 0],
                                           [0, 1, 0, dt],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]])
        current_state, current_covariance = kf.filter_update(
            current_state, current_covariance, observations[i]
        )
        smoothed_states[i, :] = current_state 
    
    return smoothed_states

def expSmooth(indices:list, alpha=0.3):
    """
    Smooth the indices using exponential smoothing.
    alpha: smoothing parameter
    """
    result = [indices[0]]
    n = len(indices)
    index = list(range(1, n))
    for i in set(index):
        result.append(alpha * result[i-1] + (1 - alpha) * indices[i])
    
    return result

def doubleExpSmooth(indices:list, alpha=0.3, beta=0.1):
    """
    Smooth the indices using double exponential smoothing.
    alpha: level smoothing parameter
    beta: trend smoothing parameter
    """
    # initialize the result
    result = [indices[0]]
    n = len(indices)
    index = list(range(1, n))
    for i in set(index):
        if i == 1:
            level, trend = indices[0], indices[1] - indices[0]
            value = indices[0]
        else:
            value = indices[i]
        level_, level = level, alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - level_) + (1 - beta) * trend
        result.append(level + trend)
    
    return result

def moving_average(indices: list, window_size=3):
    """
    Smooth the indices using centered moving average.
    window_size: size of the moving window (must be an odd number)
    """
    if window_size % 2 == 0:
        raise ValueError("Window size must be an odd number.")

    half_window = window_size // 2
    result = []

    for i in range(len(indices)):
        if i < half_window or i > len(indices) - half_window - 1:
            # Not enough elements to fill the window at the beginning or end
            result.append(indices[i])
        else:
            # Calculate the centered moving average
            window = indices[i - half_window:i + half_window + 1]
            result.append(sum(window) / window_size)
    
    return result



SMOOTH_DICT = {
    'exp': expSmooth,
    'dexp': doubleExpSmooth,
    'kal1D': KalmanSmooth_1D,
    'kal2D': KalmanSmooth_2D,
    'moving':moving_average
}

def smooth1D(
        traj,
        smoothCol,
        newCol,
        segCol=None,
        smoothFunc='exp',
        **params
):
    """
    Smooth the data sequence.
    smoothCol: list of columns that need smoothing.
    segCol: column name of tripID. If None, perform smoothing for the whole traj.
    smoothFunc: smoothing method.
        `exp`: exponentail smoothing
        `dexp`: double exponential smoothing
        `kal`: Kalman filter smoothing 
    **params: smoothing parameter for each method.
        `exp`:[alpha]
        `dexp`: [alpha, beta]
        `kal1D`: [process_var, measure_var]
    """
    smooth_func = SMOOTH_DICT[smoothFunc]

    traj = traj.copy()

    if segCol:
        for id in tqdm(set(traj[segCol].unique()), desc="Smoothing"):  
            # select trip from traj.df
            trip = traj[traj[segCol] == id].copy()

            for col in smoothCol:
                traj.loc[trip.index, col] = smooth_func(trip[col].to_list(), **params)
    
        return traj
    
    else:
        traj.loc[:, newCol] = smooth_func(traj[smoothCol].to_list(), **params)
        
        return traj

def smooth2D(
        traj,
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
    Smooth the data sequence for 2D data (trajectory coordination).
    segCol: column name of tripID. If None, perform smoothing for the whole traj.
    smoothFunc: smoothing method.
        `kal2D`: Kalman filter smoothing 
    **params: smoothing parameter for each method.
        `kal2D`: [process_var, measure_var]
    """
    smooth_func = SMOOTH_DICT[smoothFunc]

    traj = traj.copy()

    if segCol:
        for id in tqdm(set(traj[segCol].unique()), desc="Smoothing"):  
            # select trip from traj.df
            trip = traj[traj[segCol] == id].copy()

            observations = trip[[lonCol, latCol]].values
            timestamps = trip[timeCol]
            new = smooth_func(observations, timestamps, **params)
            traj.loc[trip.index, newLonCol] = new[:, 0]
            traj.loc[trip.index, newLatCol] = new[:, 1]
    
        return traj
    
    else:
        observations = traj[[lonCol, latCol]].values
        timestamps = traj[timeCol]
        new = smooth_func(observations, timestamps, **params)
        traj[newLonCol] = new[:, 0]
        traj[newLatCol] = new[:, 1]
        
        return traj

