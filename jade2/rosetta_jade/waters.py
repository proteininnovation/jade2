# A collection of PyRosetta water functions

from pyrosetta import *
from rosetta import *

from collections import defaultdict
from typing import DefaultDict, AnyStr, List

### Need to load Rosetta with -ignore_waters false ###
### Rosetta will place h's onto oxygen waters, but with bad placement. ###

### Recommended to pack waters using optH protocol ###
### For packing, options are:
###  -include_vrt false
###  -corrections::water::wat_rot_sampling 20
###  -beta

### Decreasing the wat sampling angle will improve results.  I've had good results with 20. ###


def pack_waters(pose):
    """
    Returns a water-packed pose using optH.
    """
    p = pose.clone()
    score = get_score_function()
    opth = rosetta.core.pack.task.operation.OptH()
    sel = rosetta.core.select.residue_selector.ResidueNameSelector()
    sel.set_residue_names("HOH")

    prev = rosetta.core.pack.task.operation.PreventRepackingRLT()
    op = rosetta.core.pack.task.operation.OperateOnResidueSubset(prev, sel, True)
    init = rosetta.core.pack.task.operation.InitializeFromCommandline()

    tf = rosetta.core.pack.task.TaskFactory()

    tf.push_back(opth)
    tf.push_back(init)
    tf.push_back(op)

    packer = rosetta.protocols.minimization_packing.PackRotamersMover()

    packer.score_function(score)
    packer.task_factory(tf)

    packer.apply(p)
    return p

def next_hb_res(c_hb, res: int, debug=False) -> int:
    """
    Get the residue of this hbond, regardless of donor/acceptor status.
    """
    if (c_hb.don_res() == res):
        if (debug):
            print(res, "-", c_hb.acc_res())
        return c_hb.acc_res()
    else:
        if (debug):
            print(res, "-", c_hb.don_res())
        return c_hb.don_res()


# hb = "14-12-10-8"
def find_water_mediated_hb_paths(local_hb_set, local_waters: List[int], paths: DefaultDict[AnyStr, int], current_res, current_path: AnyStr="", current_depth: int=0, max_depth:int=3,
                  previous_hbond=None) -> None:

    """
    Recursive function to
      get all unique Water-mediated hbond [paths] at a specific depth.

    Hbond paths are: 14-12-10-8
     where 12 and 10 would be waters in our water list.

    """

    hbs = local_hb_set.residue_hbonds(current_res)
    if (current_depth > max_depth): return

    #print("Current_Depth: ", current_depth)
    if (len(hbs) > 0):
        for local_hb in hbs:
            next_res = next_hb_res(local_hb, current_res)
            if previous_hbond:
                if previous_hbond == local_hb:
                    # print("Same hb to prev")
                    continue

            # print('n_res', next_res)
            if current_depth == 0:
                if next_res in local_waters:
                    current_path = str(current_res) + "-" + str(next_res)
                    new_depth = current_depth + 1
                    find_water_mediated_hb_paths(local_hb_set, local_waters, paths, next_res, current_path, new_depth, max_depth,
                                  previous_hbond=local_hb)
                else:
                    continue
            else:

                # Reached max depth or next residue is not a water
                # print("Water: ", (next_res in local_waters))
                if ((current_depth == max_depth) and (next_res not in local_waters)) or (next_res not in local_waters):
                    current = current_path + "-" + str(next_res)
                    if current in paths:
                        paths[current] += 1
                    else:
                        paths[current] = 1
                    # print("End of line")
                    continue
                elif (next_res in local_waters):
                    new_depth = current_depth + 1
                    current = current_path + "-" + str(next_res)
                    find_water_mediated_hb_paths(local_hb_set, local_waters, paths, next_res, current, new_depth, max_depth,
                                  previous_hbond=local_hb)
                else:
                    continue

    else:
        return


def get_all_water_mediated_h_bonds(p, waters: List[int], max_depth=1) -> DefaultDict[AnyStr, int]:
    """
    Return a dictionary of ALL unique water mediated h-bond paths at the specified depth.

    First and last residue in path are NOT waters, IE - these are paths from one res to another, mediated by waters

    Hbond paths are splitable string: 14-12-10-8
     where 12 and 10 would be waters in our water list.

    Note these paths may include paths back to self.
    """
    all_paths = defaultdict()

    hb_set = rosetta.core.scoring.hbonds.HBondSet(p, False)

    for c_res in range(1, p.size() + 1):
        if c_res in waters: continue
        hb_paths = defaultdict()
        find_water_mediated_hb_paths(hb_set, waters, hb_paths, c_res, current_path="", max_depth=max_depth)
        all_paths.update(hb_paths)

    return all_paths



