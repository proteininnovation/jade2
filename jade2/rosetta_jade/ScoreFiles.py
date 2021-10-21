import json

from collections import OrderedDict

import pandas

from jade2.pymol_jade.PyMolScriptWriter import *
from jade2.basic.dataframe.util import *
from jade2.basic.figure.creation import *
from jade2.basic.path import *
from jade2.basic.string_util import *

##Original Author: Luki Goldschmidt <lugo@uw.edu>
##Forked by Jared Adolf-Bryfogle.
##Has been completely refactored to work with Dataframes, still needs more refactoring

def get_dataframe(filename, match="", order_by="total_score", set_index=True):
    """
    Convert a Rosetta Score file directly to a dataframe.
    
    :param filename: path to file
    :return: dataframe.DataFrame
    """
    sc = ScoreFile(filename, match)
    df = sc.get_Dataframe(order_by=order_by)
    if set_index:
        df = df.set_index('decoy')
    df = df.reindex(sorted(df.columns), axis=1)
    return df

class ScoreFile:
  def __init__(self, filename, match="", strip_last_inc=False, strip_prefix=False):
    self.filename = filename
    self.strip_inc = strip_last_inc
    self.strip_prefix = strip_prefix

    self.name = os.path.basename(self.filename)

    self.decoys = [] #Main holder of data.  Array of dict of scoreterms and 'decoy']

    self.decoy_field_name = "decoy"
    self.decoy_dir = os.path.dirname(filename) #Assume filename is in decoy dir.  This is not nessessarily the case...


    lines = open(filename, 'r').readlines()
    #print(lines)

    headerSP = ""
    if len(lines) > 1:
        headerSP = lines[1].split()

    #print repr(headerSP)
    for line in lines:

        if (match):
            if re.search(match, line):
                pass
            else:
                continue
        try:
            local_line = line.replace("nan", "NaN")
            o = json.loads(local_line)
            # print o[self.decoy_field_name]
            # print repr(o)
            self.decoys.append(o)
        except Exception as e:
            ##Store as defaultdict instead of JSON.

            #print "Cannot load as regular JSON file!  Parsing as old-school scorefile instead: "+ str(e)
            d = defaultdict()
            values = line.split()
            if len(values) != len(headerSP):
                if len(values) == 1 and values[0] =="SEQUENCE:": continue
                print("Failed to parse JSON object or as regular score file; skipping line:\n", line)
            elif values[1] == headerSP[1]:
                continue
            else:
                for i in range(0, len(values)):
                    k = headerSP[ i ]
                    if  k == "description":
                        k = "decoy"

                    if values[i] == "SCORE:": continue

                    d[ k ] = deduce_str_type(values[i])

                self.decoys.append(d)

    #Strip _0001 that is added when re-scoring decoys.
    if self.strip_inc:
        new_decoys = []
        for o in self.decoys:
            nameSP = o[self.decoy_field_name].split('_')
            if nameSP[-1] == "0001":
                new_name = "_".join(nameSP[0:-1])
                o[self.decoy_field_name] = new_name
                new_decoys.append(o)
            else:
                new_decoys.append(o)
        self.decoys = new_decoys

    if self.strip_prefix:
        new_decoys = []
        for o in self.decoys:
            nameSP = o[self.decoy_field_name].split('_')
            new_name = "_".join(nameSP[1:])
            o[self.decoy_field_name] = new_name
            new_decoys.append(o)
        self.decoys = new_decoys

    #print repr(self.decoys)

  def get_decoy_count(self):
    return len(self.decoys)

  def get_decoy_names(self):
    return [str(r[self.decoy_field_name]) for r in self.decoys]

  def get_scoreterm_names(self):
    r = []
    for rec in self.decoys:
      for k in list(rec.keys()):
        if k != self.decoy_field_name and not k in r:
          r.append(str(k))
    r.sort()
    return r

  def get_scoreterms(self, scoreterms=""):
    if type(scoreterms) == str:
      if scoreterms in ["", "*"]:
        scoreterms = self.get_scoreterm_names()
        scoreterms.sort()
      else:
        scoreterms = scoreterms.split(",")
    r = OrderedDict()
    for rec in self.decoys:
      scores = {}
      for scoreterm in scoreterms:
        scores[scoreterm] = rec.get(scoreterm)
      r[str(rec[self.decoy_field_name])] = scores
    return r

  def get_scoreterm(self, scoreterm):
    r = {}
    for rec in self.decoys:
      r[str(rec[self.decoy_field_name])] = rec.get(scoreterm)
    return r

  def get_stats(self, scoreterms="", decoy_names = None):

    print(repr(len(decoy_names)))
    scores = self.get_scoreterms(scoreterms)
    stats = None

    if not decoy_names:
      decoy_names = self.get_decoy_names()

    #print repr(decoy_names)
    # Collect data
    for decoy_name in scores:
      if not decoy_name in [ os.path.basename(x) for x in decoy_names]:
        continue
      decoy = scores[decoy_name]
      if stats == None:
        columns = list(decoy.keys())
        stats = {k: [] for k in columns}

      for term in decoy:
        score = decoy[term]
        if not score is None and type(score) == float:
          stats[term].append(score)

    # Compute Stats
    calc_stats = OrderedDict()

    def median(s):
      s.sort()
      return s[int(len(s) / 2)]

    def stddev(s):
      mean = sum(s) / len(s)
      r = 0.0
      for x in s:
        r += pow(x - mean, 2)
      return pow(r / len(s), 0.5)

    for column in columns:
      s = stats[column]
      calc_stats[column] = {
        'n': len(s),
        'mean': sum(s) / len(s) if len(s) > 0 else None,
        'median': median(s) if len(s) > 0 else None,
        'stddev': stddev(s) if len(s) > 0 else None,
        'min': min(s) if len(s) > 0 else None,
        'max': max(s) if len(s) > 0 else None
      }

    return calc_stats

  def get_ordered_decoy_list(self, scoreterm, decoy_names = None, top_n=-1, reverse=False, ):
    """
    Get an ordered tuple of [[score, decoy_name], ...]
    Will automatically order some known scoreterms (hbonds_int, dSASA_int)

    :rtype: list[list]
    """

    if not decoy_names:
      decoy_names = self.get_decoy_names()

    if scoreterm == "hbonds_int" or scoreterm == "dSASA_int": reverse = True
    return sorted([[x[scoreterm], x[self.decoy_field_name]] for x in self.decoys if x[self.decoy_field_name] in decoy_names and scoreterm in x ], reverse=reverse)[:top_n]

  def get_score(self, decoy, scoreterm):
    """
    Get Score of a particular decoy and scoreterm
    :param decoy: str
    :param scoreterm: str
    :rtype: float
    """
    for o in self.decoys:
      if o[self.decoy_field_name] == decoy:
        return o[scoreterm]

  def get_scores(self, scoreterm, decoy_names=None, top_n=-1, reverse=False):
    ordered_decoy_names = self.get_ordered_decoy_list(scoreterm, decoy_names, top_n, reverse)
    return [self.get_score( decoy, scoreterm) for decoy in ordered_decoy_names]

  def get_Dataframe(self, scoreterms=None, order_by="total_score", top_n=-1, reverse=True):
    """
    Get data as a dataframe dataframe.  Definitely preferred now.
    :param scoreterms: list
    :param order_by: str
    :param top_n: int
    :param reverse: bool
    :rtype: pandas.DataFrame
    """
    #print(self.name)
    #print(self.decoys)

    df = pandas.DataFrame.from_dict(self.decoys)
    df = detect_numeric(df)
    #df.to_csv("debugging.csv", sep=",")
    #print(df.columns)
    if order_by in df.columns:
        df = df.sort_values(order_by, ascending=reverse)

    if (top_n!=-1):
        df = df.head(top_n)

    if scoreterms:
      df = get_columns(df, scoreterms)
    df.name = self.name
    df.scorefile = self.filename
    df["name"] = self.name
    df["scorefile"] = self.filename

    if 'decoy' in df.columns:
        if os.path.dirname(self.filename):
          df["decoy_path"] = os.path.dirname(self.filename)+"/"+df["decoy"]
          df["decoy_path"] = [get_decoy_path(p) for p in df["decoy_path"]]
        else:
          df["decoy_path"] = df["decoy"]
          df["decoy_path"] = [get_decoy_path(p) for p in df["decoy_path"]]

    return df

def get_scorefiles(indir = os.getcwd()):
    """
    Get Score files from a directory.  Walk through all directories in directory.
    :param indir: str
    :rtype: list
    """
    matches = []
    matches.extend(glob.glob(indir+"/*.sc"))
    for root, dirnames, filenames in os.walk(indir):

        for dirname in dirnames:
            matches.extend( glob.glob(root+"/"+dirname+"/*.sc") )

    return matches


def plot_score_vs_rmsd(df, title, outpath, score="total_score", rmsd="looprms", top_p=.95, reverse=True):
  """
  Plot a typical Score VS RMSD using matplotlib, save it somewhere. Return the axes.
  By default, plot the top 95%
  :param df: dataframe.DataFrame
  :param outpath: str
  :param score: str
  :param rmsd: str
  :rtype: matplotlib.Axes
  """


  return plot_x_vs_y_sea_with_regression(df, title, outpath, score, rmsd, top_p=top_p, reverse=reverse)


def pymol_session_on_top_df(df, outdir, decoy_dir = None,
                         scoreterm="total_score",
                         top_n=10,
                         decoy_column="decoy",
                         native_path = None,
                         out_prefix_override=None,
                         ab_structure = False,
                         superimpose = False,
                         run_pymol = True
                        ):
    """
    Make a PyMol session (or setup a scripter) on top X using a dataframe.
    Return the scripter for extra control.

    df should have an attribute of 'name' or out_prefix_override should be set.

    :param df: dataframe.DataFrame
    :param outdir: str
    :param decoy_dir: str
    :param scoreterm: str
    :param top_n: int
    :param decoy_column: str
    :param native_path: str
    :param out_prefix_override: str
    :param ab_structure: boolean
    :param superimpose: boolean
    :rtype: PyMolScriptWriter
    """

    if not os.path.exists(outdir): os.mkdir(outdir)

    if out_prefix_override:
        session_prefix = out_prefix_override
    elif hasattr(df, "name"):
        session_prefix = df.name+"_"
    else:
        session_prefix = "pml_session_"
        print("WARNING: out_prefix_override not set and dataframe has no attribute name!")


    pymol_name  = session_prefix+scoreterm
    #print(pymol_name)

    ascending = True
    if scoreterm == "hbonds_int" or scoreterm == "dSASA_int": ascending = False
    df2 = df.sort(scoreterm, ascending = ascending)
    df2 = df2[0:top_n]
    #print df2['total_score'].tail()
    if decoy_dir:
        df2['decoy_path'] = decoy_dir+"/"+df2[decoy_column]
    elif 'decoy_path' in df2.columns:
        pass
    else:
        df2['decoy_path'] = df2[decoy_column]

    top_decoys = list(zip(list(df2[scoreterm]), list( df2[ 'decoy_path' ])))
    #print repr(top_decoys)
    scripter = make_pymol_session_on_top_scored(top_decoys, outdir, outdir, pymol_name, int(top_n), native_path,
                                     ab_structure, parellel=False, super = superimpose, run_pymol = run_pymol)

    return scripter