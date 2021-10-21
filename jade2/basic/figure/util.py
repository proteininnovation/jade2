import matplotlib as mpl
from collections import defaultdict
from typing import List

def set_rc_params():
    mpl.rcParams['axes.xmargin'] = 0  # x margin.  See `axes.Axes.margins`
    mpl.rcParams['axes.ymargin'] = 0  # y margin See `axes.Axes.margins`

    mpl.rcParams['polaraxes.grid'] = True  # display grid on polar axes
    # axes3d.grid         : True    # display grid on 3d axes

    ### TICKS
    # see http://matplotlib.org/api/axis_api.html#matplotlib.axis.Tick
    mpl.rcParams['xtick.major.size'] = 4  # major tick size in points
    mpl.rcParams['xtick.minor.size'] = 2  # minor tick size in points
    mpl.rcParams['xtick.major.width'] = 1  # major tick width in points
    mpl.rcParams['xtick.minor.width'] = 1  # minor tick width in points
    mpl.rcParams['xtick.major.pad'] = 6  # distance to major tick label in points
    mpl.rcParams['xtick.direction'] = 'out'  # direction: in, out, or inout

    mpl.rcParams['ytick.major.size'] = 4  # major tick size in points
    mpl.rcParams['ytick.minor.size'] = 2  # minor tick size in points
    mpl.rcParams['ytick.major.width'] = 1  # major tick width in points
    mpl.rcParams['ytick.minor.width'] = 1  # minor tick width in points
    mpl.rcParams['ytick.major.pad'] = 6  # distance to major tick label in points
    # ytick.minor.pad      : 4      # distance to the minor tick label in points
    # ytick.color          : k      # color of the tick labels
    # ytick.labelsize      : medium # fontsize of the tick labels
    mpl.rcParams['ytick.direction'] = 'out'  # direction: in, out, or inout
    mpl.rcParams['figure.figsize'] = (8, 6)  # figure size in inches]

def set_legend_plot_order(exp_order: List) -> None:
    """
    Set the current plot's legend based on exp order.
    :return:
    """

    handles, labels = mpl.gca().get_legend_handles_labels()
    handle_dict = defaultdict()
    for i in range(0, len(labels)):
        handle_dict[labels[i]] = handles[i]

    new_handle_order = []
    for new_label in exp_order:
        new_handle_order.append(handle_dict[new_label])

    mpl.legend(new_handle_order, exp_order)

def set_subplot_ylim_offset(gg, pad_percent=.05):
    for ax in gg.axes:
        # print(ax.get_ylim()[0], ax.get_ylim()[1])
        current = ax.get_ylim()[0]
        d = abs(current - ax.get_ylim()[1])
        p = d * pad_percent
        # print("D:",  d)
        # print("P: ", p)

        new_lim = current - p

        # print("Old", current)
        # print("New", new_lim)
        ax.set_ylim(new_lim, None)

def pad_single_title(ax, x=.5, y=1.05):
    """
    Move the Title up in reference to the plot, essentially adding padding.
    SINGLE AXES
    :param ax:Axes
    :param x:
    :param y:
    :return:
    """
    ttl = ax.title
    ttl.set_position([x, y])

def set_common_title(fig, title, size=16, x=0, y=1.05):
    """
    for FACETED plots, add a common title.

    :param fig: Figure
    :param title: str
    :param x: int
    :param y: int
    :return:
    """

    fig.suptitle(title, size=size, x = x, y= y)

def set_common_x_y_label(fig, x_text, y_text):
    """
    For FACETED plots, add a common X or Y.

    :param fig: Figure
    :param x_text: str
    :param y_text: str
    :return:
    """
    for ax in fig.axes:
        ax.set_xlabel("")
        ax.set_ylabel("")

    fig.text(0.5, -.04, x_text, ha='center', fontsize=18)
    fig.text(-.04, 0.5, y_text, va='center', rotation='vertical', fontsize=18)


def best_fit(local_X, local_Y):
    """
    https://stackoverflow.com/questions/22239691/code-for-best-fit-straight-line-of-a-scatter-plot-in-python
    """

    xbar = sum(local_X) / float(len(local_X))
    ybar = sum(local_Y) / float(len(local_Y))
    n = len(local_X)  # or len(Y)

    numer = sum([xi * yi for xi, yi in zip(local_X, local_Y)]) - n * xbar * ybar
    denum = sum([xi ** 2 for xi in local_X]) - n * xbar ** 2

    b = numer / denum
    a = ybar - b * xbar
    #print('best fit line ', b)

    return a, b

