import torch, dgl, pandas
import numpy as np
from collections import defaultdict
from typing import List, Dict


def get_edge_data_as_dict(dfl: pandas.DataFrame, metrics: List[str], upper_cutoffs: Dict[str, float] = None) -> List[Dict]:
    """
    Parses SimpleMetric output from a dataframe and returns a list of data with res1-res2 data.
    example of 3D data in dataframe: 1:2:0.0720444,1:11:0.00018397


    Returns a list of dictionaries as [edge_tuple][metric]:data
    ->  IE: [(res1,res2)][metric] : datapoint (float)

    if upper_cutoffs is given, will only save data less than the cutoff if listed for the metric.
    Upper cutoffs: [metric] = cutoff

    This is useful for distances
    """
    #print("Parsing 3D data")

    data = []
    i = 1
    #print(metrics)
    for index, row in dfl.iterrows():
        #Steven's idea
        #d = defaultdict( defaultdict )
        d = defaultdict(lambda:defaultdict(lambda: 0.0))
        for metric in metrics:

            #print("Loading ", metric)
            #print(type(row[metric]))
            if type(row[metric]) == float:
                #print("Skipping Nan", metric)
                continue

            for x in row[metric].split(','):
                xSP = x.split(':')
                res1 = int(xSP[0]) -1
                res2 = int(xSP[1]) -1
                datapoint = float(xSP[2])
                edge = (res1, res2)

                if upper_cutoffs and metric in upper_cutoffs:
                    if datapoint <= upper_cutoffs[metric]:
                        d[edge][metric] = datapoint

                else:
                    d[edge][metric] = datapoint

        data.append(d)
        if i % 1000 == 0:
            print(i)
        i+=1

    #print("Done")
    #print(data)
    return data
