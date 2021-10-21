from jade2.basic.figure.creation import *
from typing import *
import pandas
import seaborn
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

class GenPlot(object):
    """
    A general class for configuring and making plots with various packages.
    """
    def __init__(self):
        self.violin_bw=.25
        self.jitter = .06

    def set_violin_bw(self, setting: float):
        """
        Set the bandwidth for any violin plots.
        """
        self.violin_bw = setting

    def set_jitter(self, setting: float):
        """
        Set the jitter for any strip plots.
        """
        self.jitter = setting

    def plot_categorical_scatter(self, x: str, y: str, df: pandas.DataFrame, p_type: str, box:bool = True, whiskers:bool = True, flip: bool=True):
        """
        Plot categorical values as strip, swarm, or violin plots (with swarm).
        Means are shown as dots for box plots.

        flip will show them with categories on y axis.

        Adds means for strip/swarm when no box plot is given.

        :param p_type: ["swarm", "strip", "violin"]
        :param box: add a box-plot
        :param whiskers: keep whiskers
        :param flip: flip to y axis
        """

        #Means shown as dots:
        #https://stackoverflow.com/questions/54132989/is-there-a-way-to-change-the-color-and-shape-indicating-the-mean-in-a-seaborn-bo
        ax=""
        p_types = ["swarm", "strip", "violin"]
        if p_type not in p_types:
            print("p_type not understood.")
            print("Available options are:"+" ".join(p_types))
            return

        if box and p_type != "violin":

            if whiskers:
                #ax = seaborn.boxplot(x="experiment", y=data, data=top_scoring, whis=np.inf, showmeans=True, boxprops={'facecolor': 'None'})
                ax = seaborn.boxplot(x=x, y=y, data=df, showmeans=True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"}, boxprops={'facecolor': 'None'})
            else:
                #ax = seaborn.boxplot(x="experiment", y=data, data=top_scoring, whis=np.inf, showmeans=True, boxprops={'facecolor': 'None'})
                ax = seaborn.boxplot(x=x, y=y, data=df, whis=np.inf, showfliers=False, showmeans=True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"}, boxprops={'facecolor': 'None'})


        if p_type=="swarm":
            ax = seaborn.swarmplot(x=x, y=y, data=df, linewidth=1)
            #ax = seaborn.violinplot(x="experiment", y=data, data=top_scoring, split=True, scale="count")

        elif p_type=="violin":
            #ax = seaborn.swarmplot(x=x, y=y, data=df, linewidth=1)
            ax = seaborn.stripplot(x=x, y=y, data=df, linewidth=1, jitter=.02)
            ax = seaborn.violinplot(x=x, y=y, data = df, split = True, inner = None, bw=self.violin_bw)
        else:
            ax = seaborn.stripplot(x=x, y=y, data=df, linewidth=1, jitter=self.jitter)

        #plt.ylim(0, round(plt.ylim()[1]) + 1)

        if not box and p_type!="violin":
            mean_width = 0.7

            # https://stackoverflow.com/questions/37619952/drawing-points-with-with-median-lines-in-seaborn-using-stripplot
            if not flip:
                for tick, text in zip(plt.gca().get_xticks(), plt.gca().get_xticklabels()):
                    sample_name = text.get_text()  # "X" or "Y"

                    # calculate the median value for all replicates of either X or Y
                    mean_val = df[df[x] == sample_name][y].mean()
                    #print(sample_name, tick, mean_val)

                    # plot horizontal lines across the column, centered on the tick
                    ax.plot([tick - mean_width / 2, tick + mean_width / 2], [mean_val, mean_val],
                            lw=2)
            else:
                for tick, text in zip(plt.gca().get_yticks(), plt.gca().get_yticklabels()):
                    sample_name = text.get_text()  # "X" or "Y"

                    # calculate the median value for all replicates of either X or Y
                    mean_val = df[df[y] == sample_name][x].mean()
                    #print(sample_name, tick, mean_val)

                    # plot horizontal lines across the column, centered on the tick
                    ax.plot([mean_val, mean_val], [tick - mean_width / 2, tick + mean_width / 2],
                            lw=2)
        return ax