import sqlite3
import os
import sys
from collections import defaultdict, Counter
from jade2.antibody import outliers
#A Collection of functions to query the AbDb


def get_pdb_chain_subset(db, gene, use_cutoffs = False, res_cutoff = 2.8, rfac_cutoff = .3):
    """
    Return a list of tuples of [pdb, chain] of the particular gene
    """
    #print db_fname

    db.row_factory = sqlite3.Row
    c = db.cursor()
    if not use_cutoffs:
        c.execute("SELECT DISTINCT PDB, original_chain FROM cdr_data WHERE gene =?", (gene,))
    else:
        c.execute("SELECT DISTINCT PDB, original_chain FROM cdr_data WHERE gene = ? and resolution <= ? and rfactor <= ?", [gene, res_cutoff, rfac_cutoff])
    rows = c.fetchall()
    entries = []
    for row in rows:

        list(row.keys())
        entries.append([row['PDB'],row['original_chain']])
    return entries

def get_all_lengths(db, cdr, limit_to_known = True, res_cutoff = 2.8, rfac_cutoff = .3):
    """
    Get all unique lengths for a CDR
    """


    c = db.cursor()
    lengths = []

    if limit_to_known:
        in_data = ['loopKeyNotInPaper', cdr, res_cutoff, float(rfac_cutoff)]

        for row in c.execute("SELECT DISTINCT length from "+"cdr_data"+" WHERE datatag!=? and CDR=? and resolution<=? and rfactor<=?", in_data):
            lengths.append(row[0])
    else:
        in_data = [cdr, res_cutoff, rfac_cutoff]
        for row in c.execute("SELECT DISTINCT length from "+"cdr_data WHERE CDR=? and resolution<=? and rfactor<=?", in_data):
            lengths.append(row[0])
    c.close()
    return lengths

def get_all_clusters_for_length(db, cdr, length, limit_to_known = True, res_cutoff = 2.8, rfac_cutoff = .3):
    """
    Get all unique clusters for a length and a cdr
    """
    c = db.cursor()
    clusters = []
    if limit_to_known:
        data = ['loopKeyNotInPaper', cdr, length, res_cutoff, rfac_cutoff]
        for row in c.execute("SELECT DISTINCT fullcluster from cdr_data"+" WHERE datatag!=? and CDR=? and length=? and resolution <= ? and rfactor <= ?", data):
            clusters.append(row[0])
    else:
        data = [cdr, length, res_cutoff, rfac_cutoff]
        for row in c.execute("SELECT DISTINCT fullcluster from cdr_data WHERE CDR=? and length=? and resolution<=? and rfac_cutoff<=?", data):
            clusters.append(row[0])
    c.close()

    return clusters

def get_center_for_cluster_and_length(db, cdr, length, cluster, data_names_array):
    """
    Get the center for a particular cluster and length
    
    """
    sele = ", ".join(data_names_array)

    #print sele
    data = []
    c = db.cursor()

    #print  "Getting data for: "+" ".join([cdr, repr(length), cluster])
    in_data = ['loopKeyNotInPaper', cdr, length, cluster]
    for row in c.execute("SELECT "+sele+" FROM cdr_data WHERE center=1 and datatag!=? and CDR=? and length=? and fullcluster=?",in_data):
        data.append(row)

    #print data
    if len(data) == 0: return data
    else: return data[0]

def get_center_dih_degrees_for_cluster_and_length(db, cdr, length, cluster):
    """
    Returns a dictionary of center dihedral angles in positional order.  Or returns False if not found.
    result["phis'] = [phis as floats]
    result["psis"] = [Psis as floats]
    result["omegas"] = [Omegas as floats]
    """


    result = defaultdict()
    result["phis"] = []
    result["psis"] = []
    result["omegas"] = []

    data_names_array = ["dihedrals"]
    data = get_center_for_cluster_and_length(db, cdr, length, cluster, data_names_array)
    if len(data) == 0: return False
    dihedrals = data[0]
    dihSP = dihedrals.split(":")

    phii = 0; psii = 1; omega_i = 2
    for i in range(0, length):
        phi = dihSP[phii]; psi = dihSP[psii]; omega = dihSP[omega_i]

        result["phis"].append(float(phi)); result["psis"].append(float(psi)); result["omegas"].append(float(omega))

        phii+=3; psii+=3; omega_i+=3

    assert(len(result["phis"]) == len(result["psis"]) == len(result["omegas"]))
    return result

def get_dihedral_string_for_centers(db, limit_to_known = True):
    """
    Get a string of the dihedral angles for all centers
    """
    sele = "SELECT fullcluster, length_type, ss, dihedrals from cdr_data where center=1"

    data = defaultdict()
    c = db.cursor()
    for row in c.execute(sele):
        data[row[0]] = [row[1], row[2], row[3]]
    return data

def get_data_for_cluster_and_length(db, cdr, length, cluster, data_names_array, limit_to_known = True, res_cutoff = 2.8, rfac_cutoff = .3):
    """

    Get a set of data of a particular length, cdr, and cluster.
    data_names_array is a list of the types of data.  Can include DISTINCT keyword
      Example: data_names_array = ["PDB", "original_chain", "new_chain", "sequence"]


    """
    sele = ", ".join(data_names_array)
    #print sele
    data = []

    c = db.cursor()
    if limit_to_known:
        in_data = ['loopKeyNotInPaper', cdr, length, cluster, res_cutoff, rfac_cutoff]
        for row in c.execute("SELECT "+sele+" FROM cdr_data WHERE datatag!=? and CDR=? and length=? and fullcluster=? and resolution<=? and rfactor <=?", in_data):
            data.append(row)
    else:
        in_data = [cdr, length, cluster, res_cutoff, rfac_cutoff]
        for row in c.execute("SELECT "+sele+" FROM cdr_data WHERE CDR=? and length=? and fullcluster=? and resolution<=? and rfactor<=?", in_data):
            data.append(row)

    c.close()

    return data


def get_unique_sequences_for_cluster(db, cluster, include_outliers, outlier_definition = "conservative"):
    sequences = []
    cur = db.cursor()

    for row in cur.execute("select DISTINCT seq FROM cdr_data WHERE fullcluster=? "+outliers.get_outlier_string(include_outliers, outlier_definition), [cluster]):
        sequences.append(row[0])
    cur.close()
    return sequences


def get_cdr_rmsd_for_entry(db, pdb, original_chain, cdr, length, fullcluster):
    #Make sure string to to unicode bullshit.
    sele = [str(pdb), str(original_chain), str(cdr), length, str(fullcluster)]

    cur = db.cursor()
    rmsds = []
    for row in cur.execute("select bb_rmsd_cdr_align FROM cdr_data WHERE PDB=? AND original_chain = ? AND CDR=? AND length=? and fullcluster=?", sele):
        rmsds.append(row[0])

    cur.close()
    if len(rmsds) < 1:
        return -1
    else:
        return rmsds[0]

def get_stem_rmsd_for_entry(db, pdb, original_chain, cdr, length, fullcluster):
    #Make sure string to to unicode bullshit.
    sele = [str(pdb), str(original_chain), str(cdr), length, str(fullcluster)]

    cur = db.cursor()
    rmsds = []
    for row in cur.execute("select bb_rmsd_stem_align FROM cdr_data WHERE PDB=? AND original_chain = ? AND CDR=? AND length=? and fullcluster=?", sele):
        rmsds.append(row[0])

    cur.close()
    if len(rmsds) < 1:
        return -1
    else:
        return rmsds[0]

def get_consensus_seq(db, cluster):

    c = db.cursor()
    sele = [cluster]
    cons =[]
    query = "SELECT ConsSeq from CDRClusterSum WHERE Loop = ?"

    for row in c.execute(query, sele):
        cons.append(row[0])

    c.close()

    if len(cons) != 0:
        return cons[0]
    else:
        #print("cluster not found: "+cluster)
        return "NA"

def get_median_pdb(db, cluster):

    c = db.cursor()
    sele = [cluster]
    cons =[]
    query = "SELECT MedianPDB from CDRClusterSum WHERE Loop = ?"

    for row in c.execute(query, sele):
        cons.append(row[0])

    c.close()

    if len(cons) != 0:
        return cons[0]
    else:
        #print("cluster not found: " + cluster)
        return "NA"

def get_n_clusters(db, cluster):

    c = db.cursor()
    sele = [cluster]
    cons =[]
    query = "SELECT NumStructures from CDRClusterSum WHERE Loop = ?"

    for row in c.execute(query, sele):
        cons.append(row[0])

    c.close()

    if len(cons) != 0:
        return cons[0]
    else:
        #print("cluster not found: " + cluster)
        return "NA"

def get_gene_for_custer(db, cluster):

    c = db.cursor()
    sele = [cluster]
    cons =[]
    query = "SELECT gene from CDRClusterSum WHERE Loop = ?"

    for row in c.execute(query, sele):
        cons.append(row[0])

    c.close()

    if len(cons) != 0:
        return cons[0]
    else:
        #print("cluster not found: " + cluster)
        return "NA"

def get_loop_conformation_for_custer(db, cluster):

    c = db.cursor()
    sele = [cluster]
    cons =[]
    query = "SELECT LoopConformation from CDRClusterSum WHERE Loop = ?"

    for row in c.execute(query, sele):
        cons.append(row[0])

    c.close()

    if len(cons) != 0:
        return cons[0]
    else:
        #print("cluster not found: " + cluster)
        return "NA"

def get_cluster_info(db, data_key, cluster, ):

    c = db.cursor()
    sele = [cluster]
    cons =[]
    query = "SELECT "+data_key+" from CDRClusterSum WHERE Loop = ?"

    for row in c.execute(query, sele):
        cons.append(row[0])

    c.close()

    if len(cons) != 0:
        return cons[0]
    else:
        #print("cluster not found: " + cluster)
        return "NA"


def get_dominant_cdr_cluster_for_germline_cdr(db, germline, cdr="cdr1", pure_germline=False):
    """
    Return a the dominant cluster and string percentage of a particular germline gene.
    pure_germline doesn't quite work for some reason.
    """
    # print db_fname

    cur = db.cursor()
    clusters = []
    ex = "SELECT " + cdr + "_cluster FROM GermlineAssignments WHERE frame_species='Hu' and frame_ig LIKE ?"
    if pure_germline:
        ex = "SELECT " + cdr + "_cluster FROM GermlineAssignments WHERE frame_species='Hu' and frame_pc=100 AND cdr1_pc=100 AND cdr2_pc=100 and frame_ig LIKE ?"

    gl = germline + "%"
    # print(ex,gl)
    for row in cur.execute(ex, [gl]):
        if row[0] == '-': continue
        clusters.append(row[0])

    if len(clusters) == 0: return "NA"

    counts = Counter(clusters)
    common = Counter.most_common(counts)
    rep_cluster = common[0][0]
    perc = "%.2f" % (common[0][1] / float(len(clusters)))
    # print("PERC",perc)
    cur.close()

    return rep_cluster, perc


def get_dominant_length_for_germline_cdr(db, germline, cdr="cdr1", pure_germline=False):
    """
    Return the dominant length and string percent for a germline.
    pure_germline doesn't quite work.
    """
    # print db_fname

    cur = db.cursor()
    clusters = []
    ex = "SELECT " + cdr + "_len FROM GermlineAssignments WHERE frame_species='Hu' and frame_ig LIKE ?"
    if pure_germline:
        ex = "SELECT " + cdr + "_len FROM GermlineAssignments WHERE frame_species='Hu' and frame_pc=100 AND cdr1_pc=100 AND cdr2_pc=100 and frame_ig LIKE ?"

    gl = germline + "%"
    # print(ex,gl)
    for row in cur.execute(ex, [gl]):
        if row[0] == '-': continue
        clusters.append(row[0])

    if len(clusters) == 0: return ["NA", "0"]

    counts = Counter(clusters)
    common = Counter.most_common(counts)
    rep_len = common[0][0]
    perc = "%.2f" % (common[0][1] / float(len(clusters)))
    # print("PERC",perc)
    cur.close()

    return str(rep_len), perc


def get_human_clusters(db, cdr="cdr1", grafted=False):
    """
    Get all Human clusters that have no cdr length differences to the germline for CDR1 and CDR2

    If grafted, includes non-Hu onto Hu frameworks
    return cluster_list, counts dictionary, percents [list], and string percents[list
    """
    # print db_fname

    cur = db.cursor()
    clusters = []
    ex = ""

    ex = "SELECT " + cdr + "_cluster FROM GermlineAssignments WHERE frame_species='Hu'"
    if grafted:
        ex = ex + " and " + cdr + "_species='Hu'"
    else:
        ex = ex + " and " + cdr + "_species!='Hu'"

    ex = ex + " and cdr1_diffLen=0 and cdr2_diffLen=0"
    # print(ex,gl)
    for row in cur.execute(ex):
        if row[0] == '-': continue
        if row[0].split('-')[-1] == '*': continue

        clusters.append(row[0])

    if len(clusters) == 0: return ["NA", "0"]

    gene_counts = defaultdict(int)
    for clus in clusters:
        if clus.startswith('L'):
            gene_counts['L'] += 1
        else:
            gene_counts['H'] += 1
    # print(gene_counts)
    clusters.sort()
    counts = Counter(clusters)
    cluster_list = [x for x in counts]
    cluster_list.sort()
    rcounts = [counts[x] for x in cluster_list]
    pcounts = [(counts[x] / float(gene_counts[x[0]])) * 100 for x in cluster_list]
    pfcounts = ["%.2f" % x for x in pcounts]

    # print("PERC",perc)
    cur.close()

    return cluster_list, counts, pcounts, pfcounts