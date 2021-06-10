from __future__ import division
import pandas as pd;
from pyswmm import Simulation;
from pyswmm import Subcatchments;
from pyswmm import Nodes;
from pyswmm import SystemStats;
from pyswmm import Simulation;
from swmmtoolbox import swmmtoolbox;
import numpy as np
from scipy.spatial import distance
from scipy.spatial import minkowski_distance


def update_inp(read,write,n_imperv,n_perv,d_imperv,d_perv,Ks,H_i,IMD):
    """
    function to update Dstorage paramters in SWMM .inp file
    
    inputs:
        read: read file
        write: write file
        Dstore and roughness params
        Ks: saturated hydraulic conductivity (in/hr)

        
     outputs:
         updates .inp file 
       
    """

    fin = open(read,'r')
    filedata = fin.read()
    fin.close()
    
    newdata=filedata.replace('S1               0.01       0.1        0          0          0          OUTLET    ', 
                                      'S1               '+ str(n_imperv) + '       '+ str(n_perv) + '        '+ str(d_imperv) +'          '+ str(d_perv) + '          0          OUTLET    ')
    newdata2=newdata.replace('S2               0.01       0.1        0          0          0          OUTLET    ', 
                                      'S2               '+ str(n_imperv) + '       '+ str(n_perv) + '        '+ str(d_imperv) +'          '+ str(d_perv) + '          0          OUTLET    ')
    newdata3=newdata2.replace('S3               0.01       0.1        0          0          0          OUTLET    ', 
                                      'S3               '+ str(n_imperv) + '       '+ str(n_perv) + '        '+ str(d_imperv) +'          '+ str(d_perv) + '          0          OUTLET    ')
   
    newdata4=newdata3.replace('S2               0	    10         0         ', 
                                'S2               '+ str(H_i) + '	    '+ str(Ks) + '         '+ str(IMD) + '')   
        
    f = open(write,'w')
    f.write(newdata4)
    f.close()


def paths(P,dur,current_dir,folder):
    
    """
    Function to return read, write filepaths for .inp files and outpath for csv files
    
    input: 
    1. 'P' precip scenario
    2. 'dur' duration scenario
    3. 'current dir' current directory
    4. 'folder' for inp and output files
    
    output:
    write path, read path, outpath
    
    """
    
    read='P'+str(P)+'_READ.inp'
    write='P'+str(P)+'_WRITE.inp'
    write_path = '\\'.join([current_dir, 'inp_files\\'+str(folder)+'\\'+str(dur)+'\\'+str(write)])
    read_path = '\\'.join([current_dir, 'inp_files\\'+str(folder)+'\\'+str(dur)+'\\'+str(read)])
    out_path= '\\'.join([current_dir, 'out\\'+str(folder)+'\\'])
    run='P-'+str(P)+',dur-'+str(dur)
    return write_path,read_path,out_path,run


def test_sim(write_path):
    """
    Function to test a single simulation.
    
    input: write path
    
    """
    with Simulation(write_path,'r') as sim:
        for step in sim:
            pass
        system_routing = SystemStats(sim)
        sim.report()
        print(system_routing.runoff_stats)
        
        
        



