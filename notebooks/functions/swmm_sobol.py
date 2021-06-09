import pandas as pd;
from pyswmm import Simulation;
from pyswmm import Subcatchments;
from pyswmm import Nodes;
from pyswmm import SystemStats;
from pyswmm import Simulation;
from swmmtoolbox import swmmtoolbox;

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