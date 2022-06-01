#!/usr/bin/env python3
import os,sys
from argparse import ArgumentParser
import pandas
from collections import defaultdict
import plotly
import plotly.figure_factory as ff
import os

def parse_job_data(lines):
    """
    Return dictionary of data for each job
    """
    data = defaultdict()

    #start_time   05/29/2022 16:20:25.409
    #end_time     05/30/2022 03:53:42.892
    #ru_wallclock 41597.483

    for line in lines:
        lineSP = line.split()
        if not line: continue
        if lineSP[0] == 'ru_wallclock':
            t = float(lineSP[1])
            t_h = (t/60.0)/60.0
            data['run_time_h'] = t_h
        else:
            data[lineSP[0]] = " ".join(lineSP[1:])
    return data

if __name__ == "__main__":
    parser = ArgumentParser("This simple app gets qacct info, parses, and plots information")
    parser.add_argument("--job_num", '-j', required=True, help="Job Number.  Used to query qacct." )
    parser.add_argument('--input', '-i', help= "Optionally load an already saved qacct output.")

    options = parser.parse_args()

    if not options.input:
        os.system(f'qacct -j {options.job_num} > job_summary_{options.job_num}.txt')

    job_data = []
    lines=[]
    job_num = 0

    input_file = f'job_summary_{options.job_num}.txt'
    if options.input:
        input_file = options.input

    for line in open(input_file, 'r'):

        if line.startswith('=') and len(lines) !=0:
            job_data.append(parse_job_data(lines))
            lines = []
        elif line.startswith('='):
            continue
        else:
            lines.append(line)


    df = pandas.DataFrame.from_dict(job_data)
    df = df[df['run_time_h'] > 0.0]
    df['start_time'] = pandas.to_datetime(df['start_time'])
    df['end_time'] = pandas.to_datetime(df['end_time'])

    print(df)
    print('min : ', min(df['run_time_h']), 'max : ',max(df['run_time_h']), 'mean : ',df['run_time_h'].mean())
    print('total_runtime_h : ', sum(df['run_time_h']))
    df.to_csv(f'job_data_{options.job_num}.csv')

    fig = ff.create_distplot([list(df['run_time_h'])], ['run_time_h'])
    fig.write_image(f'{options.job_num}_run_time_kde_.pdf')

    fig = plotly.express.scatter(df, x='start_time', y='taskid', color='run_time_h')
    fig.write_image(f'{options.job_num}_start_times_v_taskid.pdf')

    df = df.sort_values('start_time')
    df = df.reset_index(drop=True)
    df['tasks_started'] = df.index

    fig = plotly.express.scatter(df, x='start_time', y='tasks_started', color='run_time_h')
    fig.write_image(f'{options.job_num}_start_times_v_ntasks.pdf')

    df['tasks'] = 1
    fig = plotly.express.histogram(df, x='start_time', y='tasks')
    fig.write_image(f'{options.job_num}_start_times_hist.pdf')

    fig = plotly.express.scatter(df, x='start_time', y='end_time', color='run_time_h')
    fig.write_image(f'{options.job_num}_start_time_v_end_time.pdf')