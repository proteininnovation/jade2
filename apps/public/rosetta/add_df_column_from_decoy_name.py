#!/usr/bin/env python3
from argparse import ArgumentParser
import sys,os
import pandas
from jade2.rosetta_jade.score_util import get_dataframe_from_json
from jade2.basic.dataframe.util import add_piece_of_decoy_name_as_subset

if __name__ == "__main__":
    parser = ArgumentParser("This script takes a JSON scorefile and adds a new df column based on "
                            "splitting the decoy name and taking a position.  "
                            "Useful when experiments are embedded in decoy names.")

    parser.add_argument("--scorefile", '-s',
                        help="The path to the JSON file. Default: score.sc",
                        default="score.sc")

    parser.add_argument("--out", '-o',
                        help = "The path and full name to the output file. Default: score2.json",
                        default="score2.json")

    parser.add_argument("--new_column_name", '-n',
                        help = "The new column name to be added.",
                        required=True)

    parser.add_argument("--delimiter", '-d',
                        help = "The delimiter we will use for splitting. Default is _",
                        default="_")

    parser.add_argument("--position", '-p',
                        help = "The position we will use.",
                        required = True)
    parser.add_argument("--csv", "-c",
                        help = "Output as CSV?",
                        default = False,
                        action = "store_true")

    options = parser.parse_args()




    if not os.path.exists(options.scorefile):
        sys.exit("Scorefile passed does not exist! "+options.scorefile)


    if options.scorefile.split('.')[-1] == "csv":
        print("Reading CSV")
        df = pandas.read_csv(options.scorefile)
    else:
        df = get_dataframe_from_json(options.scorefile)

    print("Dataframe Read")
    df = add_piece_of_decoy_name_as_subset(df, int(options.position), options.new_column_name)
    if options.csv:
        df.to_csv(options.out, index=False)
        print("New CSV output to "+options.out)
    else:
        df.to_json(options.out, orient='records', lines=True)
        print("New JSON output to "+options.out)