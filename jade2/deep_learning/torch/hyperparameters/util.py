from .Parameters import Parameters, Params

from typing import List
import itertools
from collections import defaultdict

def get_permutations(param_list: List[Parameters]) -> List[Params]:
    """
    Gets a list of hyperparameters as permutations.
    :param parameters:
    :return:
    """
    params = []
    arg_names = []
    param_classes = []

    #First, we turn them into combos
    for p in param_list:
        for x in list(p.parameters.keys()):
            #print(x)
            params.append(p.parameters[x])
            arg_names.append(x)

    print(params)

    combos = list(itertools.product(*params))
    #print(combos)

    #Then, we take those combos and return a list of Params objects
    for c in combos:
        val_dict = defaultdict()
        for name, val in zip(arg_names, c):
            val_dict[name] = val
        #print(val_dict)
        run_params = Params(val_dict)
        param_classes.append(run_params)

    return param_classes