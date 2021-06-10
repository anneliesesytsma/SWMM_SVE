import pandas as pd;
from pyswmm import Simulation;
from pyswmm import Subcatchments;
from pyswmm import Nodes;
from pyswmm import SystemStats;
from pyswmm import Simulation;
from swmmtoolbox import swmmtoolbox;
import SALib
from SALib.analyze import sobol
from SALib.sample import saltelli
from SALib.plotting.bar import plot as barplot

def run_sim_sens(write_path,A1,A2,A3,W1,W2,W3,S,P):
    
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
        
        s1.slope = S/100.
        s2.slope = S/100.
        s3.slope = S/100.
        
        
        for step in sim:
            pass
        system_routing = SystemStats(sim)
        sim.report()
        d=system_routing.runoff_stats # sets dictionary keys
        infiltration=d['infiltration']
        runoff=d['runoff']
        
    return infiltration,runoff

def sobol_(problem,params,Y,P,Ks,fI,S):
    """
    
    Function assign compile output files into a single file
    and parameter names to sobol problem
    
    intputs:
        problem = Sobol problem
        params = parameter dictionary
        Y = file path to output file
        P = rainfall scenario
        Ks = saturated hydraulic conductivity
        fI = impervious fraction
        S = slope
        
    outputs:
        Si_df = dataframe of sobol variance metrics for the output file

    """

    # analyze output file to get sobol metrics
    Si = sobol.analyze(problem, Y, print_to_console=False)

    #get variance metrics from Si
    S1      = Si['S1']
    S1_conf = Si['S1_conf']
    ST      = Si['ST']
    ST_conf = Si['ST_conf']
    S2      = Si['S2']
    S2_conf = Si['S2_conf']

    # get parameters
    k_width=params[:,0] 
    f_routed=params[:,1]
    n_perv=params[:,2]
    n_imperv= params[:,3]
    d_perv=params[:,4]
    d_imperv=params[:,5]
    
    zipped=zip(problem['names'], Si['S1'], Si['ST'], params.mean(axis=0))
    Si_df=pd.DataFrame(zipped,columns=["Name", "1st","Total", "Mean of Input"])
    Si_df['p'] = float(P)
    Si_df['Ks'] = float(Ks)
    Si_df['fI'] = float(fI)
    Si_df['S'] = float(S)
    
    #return Si_df dataframe of the sobol metrics with associated P, Ks, fI, and S
    return Si_df