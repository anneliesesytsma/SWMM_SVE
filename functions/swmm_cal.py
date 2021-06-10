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
import os
from os.path import dirname
parent_dir = (dirname(os.getcwd()))

def two_params(sve_core,n):

    params_df=sve_core[['fV','So','p','A_dc','image']].drop_duplicates()
    params_df['A']=50*100*0.0001 #A in hectares
    params_df['A2']=params_df['A']*params_df['fV']
    params_df['A_imp']=params_df['A']*(1-params_df['fV'])
    params_copy = pd.DataFrame(np.repeat(params_df.values,n,axis=0))
    params_copy.columns = params_df.columns
    
    kW_array= np.arange(start = 100, stop = 1000) #kw range from 0.01 to .1
    
    i=0
    rows_list = []
    while (i<n): 
        d=[]
        np.random.seed(i)
        d=np.random.choice(kW_array,size=len(params_df),replace=False)/10000.
        rows_list.extend(d)
        i=i+1
    params_copy['K_width'] = rows_list       
    Adc_array= np.arange(start = 1, stop = 1000)
    
    i=0
    rows_list = []
    while (i<n): 
        d=[]
        np.random.seed(i+2)
        d=np.random.choice(Adc_array,size=len(params_df),replace=False)/1000.
        rows_list.extend(d)
        i=i+1
    params_copy['Adc_frac'] = rows_list
 
    params_final=params_copy.reset_index()
    params_final['W2']=params_final['K_width']*(params_final['A']/0.0001)
    params_final['W1']=params_final['W2']
    params_final['W3']=params_final['W2']
    params_final['A3'] = params_final['Adc_frac']*params_final['A_imp']
    params_final['A1'] = params_final['A_imp']-params_final['A3']
    params_final['A_check']=(params_final['A']-params_final['A1']-params_final['A2']-params_final['A3']).astype(float).round(3)    
    params_dict=params_final.to_dict()

    file = os.path.join(parent_dir, 'out\\2params.pickle')

    with open(file, 'wb') as handle:
        pickle.dump(params_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        

# def nrmse(core):
#     diff=np.max(core['infl_frac'])-np.min(core['infl_frac'])
#     core['nrmse']=np.float64(sqrt(mean_squared_error(core['infl_frac'],core['IF']))/diff)        

def run_sim_cal(write_path,A1,A2,A3,W1,W2,W3,S,P):
    
    """
    run pyswmm
    
    inputs:
        write = write file path
        A1 = impervious subcatchment area
        A2 = pervious subcatchment area
        W1 = impervious subcatchment width
        W2 = pervious subcatchment width
        S = slope
        P = rainfall depth
        
    outputs:
        infiltration = total infiltration
        runoff = total runoff
        runon = total runon
    
    """

    with Simulation(write_path,'r') as sim:

        d=dict()
        
        s1 =  Subcatchments(sim)["S1"]
        s2 =  Subcatchments(sim)["S2"]
        s3 =  Subcatchments(sim)["S3"]
        
        s1.area = A1
        s2.area = A2
        s3.area = A3
        
        s1.width = W1
        s2.width = W2
        s3.width = W3
        
        fV=(A2/(A1+A2+A3))
        
        for step in sim:
            pass
        system_routing = SystemStats(sim)
#         sim.report()
        d=system_routing.runoff_stats # sets dictionary keys
        infiltration=d['infiltration']
        runoff=d['runoff']
        rainfall=d['rainfall']
        stor=d['final_storage']
        
    return infiltration,runoff,rainfall,stor
