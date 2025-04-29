'''
@File    :   plot.py
@Time    :   2024/05/21 11:23:48
@Author  :   Qiuzi Chen 
@Version :   1.0
@Contact :   qiuzi.chen@outlook.com
@Desc    :   
'''

import pandas as pd

import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 150

import contextily as ctx
import transbigdata as tbd
import geopandas as gpd
from shapely import Point, LineString


def plot_traj(
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
    fig, ax = plt.subplots(1,1, figsize=figsize, constrained_layout=True)

    # if plot for each segment
    # TODO: plot for segments
    if segCol:
        pass

    # plot the whole traj
    else:
        # convert to Points
        points = traj.apply(lambda x: Point(x[lonCol], x[latCol]), axis=1)
        # convert to GeoDataFrame
        traj_gdf = gpd.GeoDataFrame(
            {'index':[0], 'geometry': [LineString(points)]},
            geometry='geometry', crs=4326
        )
        # plot traj
        traj_gdf.plot(
            ax=ax,
            color=linecolor, linewidth=linewidth,
            **kwargs
        )
        # plot o-d points
        o_gdf = gpd.GeoDataFrame({'index':['o'], 'geometry':[points[0]]}, geometry='geometry', crs=4326)
        o_gdf.plot(ax=ax, color='red', marker='$O$', markersize=markersize)
        d_gdf = gpd.GeoDataFrame({'index':['d'], 'geometry':[points[len(points)-1]]}, geometry='geometry', crs=4326)
        d_gdf.plot(ax=ax, color='red', marker='$D$', markersize=markersize)
    
    # basemap
    if basemap:
        ctx.add_basemap(
            ax=ax, crs=traj_gdf.crs.to_string(),
            source='https://c.tile.thunderforest.com/cycle/{z}/{x}/{y}.png?apikey=41f4f936f1d148f69cbd100812875c88'
        )

    if not axis:
        plt.axis('off')
    plt.show()


def plot_heat(
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
    fig, ax = plt.subplots(1,1, figsize=figsize, constrained_layout=True)

    # convert to Points
    points = traj.apply(lambda x: Point(x[lonCol], x[latCol]), axis=1)
    
    # convert to GeoDataFrame
    traj_gdf = gpd.GeoDataFrame(
        {'index':[0], 'geometry': [LineString(points)]},
        geometry='geometry', crs=4326
    )
    
    # plot traj
    traj_gdf.plot(
        ax=ax,
        color=linecolor, linewidth=linewidth,
        **kwargs, zorder=1
    )
    
    # plot points
    point_gdf = gpd.GeoDataFrame({'index':list(range(len(points))), heatCol: traj[heatCol].to_list(), 'geometry':points}, geometry='geometry', crs=4326)
    point_gdf.plot(
        ax=ax, column=heatCol, cmap=cmap, markersize=markersize, 
        legend=True, legend_kwds={"label": heatCol, "shrink":0.8},
        zorder=2
    )

    # basemap
    if basemap:
        ctx.add_basemap(
            ax=ax, crs=traj_gdf.crs.to_string(),
            source='https://c.tile.thunderforest.com/cycle/{z}/{x}/{y}.png?apikey=41f4f936f1d148f69cbd100812875c88'
        )

    if not axis:
        plt.axis('off')
    plt.show()


def plot_series(
        traj:pd.DataFrame,
        plotCol:list,
        timeCol,
        segCol=None,
        subplots=True,
        figsize=(5,3)
):
    # TODO: segment plot

    if len(plotCol) > 1:  # plot multiple cols
        
        if subplots == True:
            n = len(plotCol)
            fig, ax = plt.subplots(n,1, figsize=figsize, constrained_layout=True)

            # subplots
            for i, col in enumerate(plotCol):
                if segCol:
                    for id in traj[segCol].unique():
                        ax[i].plot(traj[traj[segCol]==id][timeCol], traj[traj[segCol]==id][col], linewidth=1)
                else:
                    ax[i].plot(traj[timeCol], traj[col], linewidth=1)
                ax[i].set_ylabel(col)
                ax[i].grid()
        else:
            fig, ax = plt.subplots(1,1, figsize=figsize, constrained_layout=True)
            for i, col in enumerate(plotCol):
                if segCol:
                    for id in traj[segCol].unique():
                        ax.plot(traj[traj[segCol]==id][timeCol], traj[traj[segCol]==id][col], linewidth=1)
                else:
                    ax.plot(traj[timeCol], traj[col], linewidth=1, label=col)
            ax.grid()
            ax.legend()

    else:
        fig, ax = plt.subplots(1,1, figsize=figsize, constrained_layout=True)

        ax.plot(traj[timeCol], traj[plotCol[0]], linewidth=1)
        ax.set_ylabel(plotCol[0])
        ax.grid()

    plt.show()