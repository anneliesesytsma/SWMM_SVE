import pandas as pd;
from pyswmm import Simulation;
from pyswmm import Subcatchments;
from pyswmm import Nodes;
from pyswmm import SystemStats;
from pyswmm import Simulation;
from swmmtoolbox import swmmtoolbox;
import pickle
import numpy as np
from math import sqrt
from shapely import affinity
import matplotlib.pyplot as plt;
import seaborn as sns


def concat(core,frames,sve_core):
    """
    function to combine SVE and SWMM simulations by p, ks, fI, and image
    computes error metrics for each SWMM simulation
    
    inputs:
        core = output dataframe (empty)
        frames = SWMM dataframes P_2,P_5 and P_8
        sve_core = SVE dataframe
    outputs:
        core dataframe
        swmm dataframe
    
    """
    swmm=pd.concat(frames)
    swmm['IF']=swmm['infiltration']/(swmm['P']*30./60./100.*50*100).astype(float).round(3)
    swmm['R_swmm']=(1-swmm['IF']).astype(float).round(3)
    swmm['p_Ks']=(swmm['P']/swmm['Ks']).astype(float).round(2)
    swmm['fI']=1-swmm['fV']
    swmm['fI']=swmm['fI'].astype(float).round(1)
    swmm['model']='swmm'
    swmm['f_dc']=swmm['A3']/(swmm['A3']+swmm['A1'])
    swmm['K_width']=swmm['W']/(50*100)
    
    sve_core2=sve_core[['scenario', 'fI','infl_frac','image','R_sve']].drop_duplicates()
    core = pd.merge(swmm, sve_core2,  how='inner',on=['scenario', 'fI','image'])
    
    #runoff ratio = runoff depth/ total rainfall depth
    core['RR_sve']=((1-core['infl_frac'])).astype(float)  
    core['RR_swmm']=((1-core['IF'])).astype(float)  
    
    #calculate runoff depth
    core['RD_sve']=(core['RR_sve'])*(core['P']*10.*30./60).astype(float)  
    core['RD_swmm']=((core['RR_swmm'])*(core['P']*10.*30./60.)).astype(float)  # P [cm/hr]* 10 mm/cm * 30 min/ 60 min 
    
    
    ## calculate error metrics
    
    # absolute error in IF
    core['error_IF_abs']=((core['infl_frac']-core['IF'])).astype(float)
    # absolute error in RR
    core['error_RR_abs']=((core['RR_sve']-core['RR_swmm'])).astype(float)  
    # absolute error in runoff depth
    core['error_RD_abs']=((core['RD_sve']-core['RD_swmm'])).astype(float)  

    
    # percent error in IF
    core['error_IF_pct']=((core['error_IF_abs'])/core['infl_frac']*100.0).astype(float)
    # percent error in RR
    core['error_RR_pct']=((core['error_RR_abs'])/core['RR_sve']*100.0).astype(float)
    # percent error in runoff depth
    core['error_RD_pct']=((core['error_RD_abs'])/(core['RD_sve'])*100).astype(float)  

    return core,swmm

def error_grid(error_metric,intersect):
    """
    function to compute 95th % confidence intervals on error metrics
    
    inputs:
        error_metric = one of SVE change metrics (SVE_IF_pct, SVE_IF_abs, SVE_RD_abs)  
                            or SWMM-SVE error metrics (error_IF, error_IF_abs, error_RD_abs)
        intersect = dataframe with all intersected initial to future transitions
    outputs:
        intersect_2 = dataframe with 95% confidence intervals and mean values for the specified metric
    """
    intersect_2 = intersect.copy()
    intersect_2['max_err']=0
    intersect_2['min_err']=0
    intersect_2['mean_err']=0
    intersect_2['mean_abs_err']=0

    for index,row in intersect.iterrows():
        alpha = 0.95
        
        #lower 95% CI
                
        p = ((1.0-alpha)/2.0) * 100
        min_err =  np.percentile(row[error_metric], p)
       
        #Upper 95% CI
        
        p = (alpha+((1.0-alpha)/2.0)) * 100
        max_err =  np.percentile(row[error_metric], p)
        
        #mean error
        
        mean_err = np.mean(row[error_metric])
        mean_abs_err = np.mean(np.abs(row[error_metric]))
        
        
        intersect_2.loc[index, 'max_err'] = max_err
        intersect_2.loc[index, 'min_err'] = min_err
        intersect_2.loc[index, 'mean_err'] = mean_err
        intersect_2.loc[index, 'mean_abs_err'] = mean_abs_err
        
    return intersect_2
