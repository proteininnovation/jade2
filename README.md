
# Jade2


A repository for modules and applications to aid in the design and analysis of Biological molecules, especially when working with Rosetta or PyRosetta.

* Free software: BSD license


## Features


- A suite of modules for working with biological molecules in python.
- A suite of public and pilot applications to make day-to-day tasks easier.
  - Commonly used ones include score_analysis.py, get_seq.py, and RunRosettaMPI.py

## PyRosetta

Used for some applications and the `rosetta_jade` module.


[rosetta_logo]:  https://www.rosettacommons.org/sites/all/themes/rosettacommons/logo.png "Rosetta Logo"

![Rosetta Logo][rosetta_logo]

* Rosetta  : [http://www.rosettacommons.org]
* PyRosetta: [http://www.pyrosetta.org]

## Setup

Simple setup for development (and cluser) purposes.
1) Run the `setup.py` script to copy apps into the bin directory.
2) Add **jade2** to your *PythonPath*.
3) Add the **/bin** directory to your *Path*.

## Caveats

This package is still under heavy development, and test code coverage is limited at the moment.


Table of Contents
=================

   * [Jade2](#jade2)
      * [Features](#features)
      * [PyRosetta](#pyrosetta)
      * [Setup](#setup)
      * [Caveats](#caveats)
   * [Application Docs](#application-docs)
      * [Glycan_scanning](#glycan_scanning)
         * [analyze_glycan_scan.py](#analyze_glycan_scanpy)
      * [General](#general)
         * [convert_fig.py](#convert_figpy)
         * [canceljobs.py](#canceljobspy)
         * [genscript_to_fasta.py](#genscript_to_fastapy)
         * [get_seq.py](#get_seqpy)
         * [rename_designs.py](#rename_designspy)
      * [Rosetta](#rosetta)
         * [score_analysis.py](#score_analysispy)
         * [RunRosettaDBMode.py](#runrosettadbmodepy)
         * [check_missing_rosetta_nstruct.py](#check_missing_rosetta_nstructpy)
         * [insert_natives_table_into_features_db.py](#insert_natives_table_into_features_dbpy)
         * [create_score_json_from_scored_decoys.py](#create_score_json_from_scored_decoyspy)
         * [RunRosettaMPI.py](#runrosettampipy)
      * [PyRosetta](#pyrosetta-1)
         * [find_my_residues.py](#find_my_residuespy)
         * [find_my_glycans.py](#find_my_glycanspy)
         * [get_phi_psi.py](#get_phi_psipy)
         * [create_glycan_scanning_job.py](#create_glycan_scanning_jobpy)
         * [get_mutation_energy.py](#get_mutation_energypy)
         * [build_loop_pyrosetta.py](#build_loop_pyrosettapy)
      * [Antibody_utils](#antibody_utils)
         * [split_antibody_components.py](#split_antibody_componentspy)
         * [generate_rabd_features_dbs.py](#generate_rabd_features_dbspy)
         * [RAbD_Jade.py](#rabd_jadepy)
         * [convert_IMGT_to_fasta.py](#convert_imgt_to_fastapy)
         * [order_ab_chains.py](#order_ab_chainspy)
         * [match_antibody_structures.py](#match_antibody_structurespy)
         * [create_features_json.py](#create_features_jsonpy)
      * [Pdb_utils](#pdb_utils)
         * [remove_redundent_lines.py](#remove_redundent_linespy)
         * [delete_chains.py](#delete_chainspy)
         * [place_TERs.py](#place_terspy)
         * [strip_ANISOU.py](#strip_anisoupy)
         * [strip_ter.py](#strip_terpy)
         * [fix_space_chain.py](#fix_space_chainpy)
      * [Antibody_benchmark_utils](#antibody_benchmark_utils)
         * [bm-RAbD_Jade.py](#bm-rabd_jadepy)
         * [bm-calculate_plot_mc_acceptance_rabd.py](#bm-calculate_plot_mc_acceptance_rabdpy)
         * [bm-output_all_clusters.py](#bm-output_all_clusterspy)
         * [RunRosettaBenchmarksMPI.py](#runrosettabenchmarksmpipy)
         * [bm-calculate_recoveries_and_risk_ratios.py](#bm-calculate_recoveries_and_risk_ratiospy)
         * [bm-calculate_graft_closure_rabd.py](#bm-calculate_graft_closure_rabdpy)
         * [bm-plot_features.py](#bm-plot_featurespy)
         * [bm-run_rabd_benchmarks.py](#bm-run_rabd_benchmarkspy)

Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)


# Application Docs
------------------


## Glycan_scanning
---------------

### analyze_glycan_scan.py

```
usage: Analyze data output from a glycan_scanning job created using the JADE create_glycan_scanning_job script
       [-h] [-s S] [--outdir_prefix OUTDIR_PREFIX] [--get_top] [--get_plots]
       [--native_path NATIVE_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -s S                  Score file with extra metrics.
  --outdir_prefix OUTDIR_PREFIX
                        Prefix for output directories
  --get_top             Get pymol sessions and top models
  --get_plots           Get plots for analysis
  --native_path NATIVE_PATH
                        Path to native
```


## General
-------

### convert_fig.py

```
usage: convert_fig.py [-h]

Converts images to TIFF figures at 300 DPI for publication using sips.
Arguments: INFILE OUTFILEExample: convert_to.py in_fig.pdf out_fig.tiff
Example: convert_to.py in_fig.png out_fig.eps eps

optional arguments:
  -h, --help  show this help message and exit
```

### canceljobs.py

```
Use: canceljobs.py start end
```

### genscript_to_fasta.py

```
usage: genscript_to_fasta.py [-h] --format {mutagenesis,GeneSynth} infile

This script outputs fasta files from a genscript format. Pass the --format
option to control which genscript format as input ~~~ Ex: python
genscript_mut_to_fasta.py --format mutagenesis MutagenesisFormatU68 ~~~

positional arguments:
  infile                The mutagenesis format file.

optional arguments:
  -h, --help            show this help message and exit
  --format {mutagenesis,GeneSynth}
                        The genscript file format
```


### get_seq.py

```
usage: get_seq.py [-h] [--pdb PDB] [--pdblist PDBLIST]
                  [--pdblist_input_dir PDBLIST_INPUT_DIR] [--chain CHAIN]
                  [--cdr CDR]
                  [--format {basic,fasta,general_order,IgG_order,IgG_order_lambda,IgG_order_kappa,IgG_order_heavy}]
                  [--outpath OUTPATH] [--prefix PREFIX] [--region REGION]
                  [--strip_c_term STRIP_C_TERM] [--pad_c_term PAD_C_TERM]
                  [--output_original_seq]

Uses Biopython to print sequence information. Example: get_seq.py --pdb
2j88_A.pdb --format fasta --outpath test.txt

optional arguments:
  -h, --help            show this help message and exit
  --pdb PDB, -s PDB     Input PDB path
  --pdblist PDBLIST, -l PDBLIST
                        Input PDB List
  --pdblist_input_dir PDBLIST_INPUT_DIR, -i PDBLIST_INPUT_DIR
                        Input directory if needed for PDB list
  --chain CHAIN, -c CHAIN
                        A specific chain to output
  --cdr CDR             Pass a specific CDR to output alignments of.
  --format {basic,fasta,general_order,IgG_order,IgG_order_lambda,IgG_order_kappa,IgG_order_heavy}
                        The output format requried.
  --outpath OUTPATH, -o OUTPATH
                        Output path. If none is specified it will write to
                        screen.
  --prefix PREFIX, -t PREFIX
                        Tag to add before chain
  --region REGION       specify a particular region, start:end:chain
  --strip_c_term STRIP_C_TERM
                        Strip this sequence off the C-term of resulting
                        sequences. (Useful for antibodies
  --pad_c_term PAD_C_TERM
                        Pad this sequence with some C-term (Useful for
                        antibodies
  --output_original_seq
                        Output the original sequence and the striped seqeunce
                        if stripped. Default FALSE.
```


### rename_designs.py

```
usage: rename_designs.py [-h] -i NEW_NAMES

Renames original files to new names for design ordering. Copy all models going
to be ordered into a single directory first. Run from directory with pdb files
already copied in!

optional arguments:
  -h, --help            show this help message and exit
  -i NEW_NAMES, --new_names NEW_NAMES
                        File with new to old names. Example line: new_name *
                        filename. Can have lines that don't have all three.
                        Will only rename if it has a star in the second
                        column.
```



## Rosetta
-------

### score_analysis.py

```
usage: score_analysis.py [-h] -s [SCOREFILES [SCOREFILES ...]]
                         [--scoretypes [SCORETYPES [SCORETYPES ...]]]
                         [-n TOP_N] [--top_n_by_10 TOP_N_BY_10]
                         [--top_n_by_10_scoretype TOP_N_BY_10_SCORETYPE]
                         [--decoy_names [DECOY_NAMES [DECOY_NAMES ...]]]
                         [--list_scoretypes] [--pdb_dir PDB_DIR] [--summary]
                         [--csv] [--make_pdblist] [--pymol_session]
                         [--plot [PLOT [PLOT ...]]] [--copy_top_models]
                         [--prefix PREFIX] [--outdir OUTDIR]
                         [--plot_type {line,scatter,bar,hist,box,kde,area,pie,hexbin}]
                         [--plot_filter PLOT_FILTER] [--native NATIVE]
                         [--ab_structure] [--super SUPER]

This utility parses and extracts data from score files in JSON format

optional arguments:
  -h, --help            show this help message and exit
  -s [SCOREFILES [SCOREFILES ...]], --scorefiles [SCOREFILES [SCOREFILES ...]]
                        Scorefiles to use
  --scoretypes [SCORETYPES [SCORETYPES ...]]
                        List of score terms to extract
  -n TOP_N, --top_n TOP_N
                        Only list Top N when doing top scoring decoys or
                        making pymol sessionsDefault is to print all of them.
  --top_n_by_10 TOP_N_BY_10
                        Top N by 10 percent total score to print out.
  --top_n_by_10_scoretype TOP_N_BY_10_SCORETYPE
                        Scoretype to use for any top N by 10 printing. If
                        scoretype not present, won't do anything.
  --decoy_names [DECOY_NAMES [DECOY_NAMES ...]]
                        Decoy names to use
  --list_scoretypes     List score term names
  --pdb_dir PDB_DIR, -d PDB_DIR
                        Directory for PDBs if different than the directory of
                        the scorefile

OUTPUT:
  General output options.

  --summary, -S         Compute stats summarizing data
  --csv, -c             Output selected columns, top, and decoys as CSV.
  --make_pdblist        Output PDBlist file(s)
  --pymol_session       Make pymol session(s) of the scoretypes specified
  --plot [PLOT [PLOT ...]]
                        Plot one score type vs another. Save the plot. 2 or 3
                        Arguments. [X, Y, 'Title''] OR [X, 'Title']. If title
                        has spaces, use quotes. Nothing special, just used for
                        quick info.
  --copy_top_models     Copy the top -n to the output directory for each
                        scorefile passed.
  --prefix PREFIX, -p PREFIX
                        Prefix to use for any file output. Do not include any
                        _
  --outdir OUTDIR, -o OUTDIR
                        Output dir. Default is current directory.

PLOTTING:
  Options for plot output

  --plot_type {line,scatter,bar,hist,box,kde,area,pie,hexbin}
                        The type of plot we are outputting.
  --plot_filter PLOT_FILTER
                        Filter X to top Percent of this - useful to remove
                        outliers.

PYMOL:
  Options for pymol session output

  --native NATIVE       Native structure to use for pymol sessions.
  --ab_structure        Specify if the module is a renumbered antibody
                        structure. Will run pymol script for ab-specific
                        selection
  --super SUPER         Super this selection instead of align all to.
```

### RunRosettaDBMode.py

```
usage: This program runs Rosetta MPI locally or on a cluster using slurm or qsub.  Relative paths are accepted.
       [-h] [-s S] [-l L] [--np NP] [--nstruct NSTRUCT] [--job_name JOB_NAME]
       [--outdir OUTDIR] [--json_run JSON_RUN] [--extra_options EXTRA_OPTIONS]
       [--script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]] [--jd3]
       [--program PROGRAM] [--print_only] [--local_test] [--one_file_mpi]
       [--job_manager {slurm,qsub,local,local_test}]
       [--job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]]
       [--json_base JSON_BASE] [--compiler {gcc,clang}] [--mpiexec MPIEXEC]
       [--machine_file MACHINE_FILE] [--db_mode {sqlite3,mysql,postgres}]
       [--db_name DB_NAME] [--db_batch DB_BATCH] [--db_in] [--db_out]

optional arguments:
  -h, --help            show this help message and exit

Common Options:
  -s S                  Path to a pdb file
  -l L                  Path to a list of pdb files
  --np NP               Number of processors to use for MPI. Default = 101
  --nstruct NSTRUCT     The number of structures/parallel runs. Can also set
                        this in any JSON file.
  --job_name JOB_NAME   Set the job name used for mpi_tracer_to_file dir and
                        queue. Default = 'rosetta_run'. (Benchmarking:
                        Override any set in json_base.)
  --outdir OUTDIR, -o OUTDIR
                        Outpath. Default = 'pwd/decoys'
  --json_run JSON_RUN   JSON file for specific Rosetta run. Not required. Pre-
                        Configured JSONS include:
                        ['antibody_designer_even_clus_dock.json',
                        'relax.json', 'remodel.json', 'cluster_features.json',
                        'NGK_smooth.json',
                        'antibody_designer_even_len_clus_dock.json',
                        'pareto_optimal_relax.json', 'relaxed_design.json',
                        'antibody_H3.json', 'antibody_features.json',
                        'antibody_designer_even_len_clus.json',
                        'glycosylate_relax.json', 'dualspace_relax.json',
                        'interface_analyzer.json', 'common_flags.json',
                        'blank.json', 'relaxed_design_ds.json',
                        'antibody_designer_even_clus.json', 'NGK.json',
                        'antibody_designer_dock.json', 'snugdock.json',
                        'antibody_designer.json', 'rosetta_scripts.json',
                        'glycan_clash_check.json', 'NGK_smooth_shap.json']
  --extra_options EXTRA_OPTIONS
                        Extra Rosetta options. Specify in quotes!
  --script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]
                        Any script vars for XML scripts.Specify as you would
                        in Rosetta. like: glycosylation=137A,136A
  --jd3                 Is this app JD3? Must build with
                        extras=mpi,serialization.
  --program PROGRAM     Define the Rosetta program to use if not set in
                        json_run

Testing and Debugging:
  --print_only          Do not actually run anything. Just print setup for
                        review.
  --local_test          Is this a local test? Will change nstruct to 1 and run
                        on 2 processors
  --one_file_mpi        Output all MPI std::out to a single file instead of
                        splitting it.

Special Options for controlling execution:
  --job_manager {slurm,qsub,local,local_test}
                        Job Manager to launch job. (Or none if local or
                        local_test)Default = 'slurm '
  --job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]
                        Extra options for the job manager, such as queue or
                        processor requestsRemove double dashes. Exclusive is
                        on by default. Specify like: -p imperial exclusive.
  --json_base JSON_BASE
                        JSON file for setting up base paths/etc. for the
                        cluster.Default =
                        'database/rosetta/jsons/common_flags.json'
  --compiler {gcc,clang}
                        Set the compiler used. Will set clang automatically
                        for macos. Default = 'gcc'
  --mpiexec MPIEXEC     Specify a particular path (or type of) MPI exec.
                        Default is srun (due to vax). If local or local test,
                        will use mpiexex
  --machine_file MACHINE_FILE
                        Optional machine file for passing to MPI

Relational Databases:
  Options for Rosetta Database input and output. Use for features or for
  inputting and output structures as databases

  --db_mode {sqlite3,mysql,postgres}
                        Set the mode for Rosetta to use if using a database.
                        Features will be output to a database. If not sqlite3,
                        must build Rosetta with extras. If any post-processing
                        is required, such as combining sqlite3 dbs, will do
                        this. Default DB mode for features is sqlite3.
  --db_name DB_NAME     In or Out database name
  --db_batch DB_BATCH   Batch of structures.
  --db_in               Use an input database
  --db_out              Use an output database
```


### check_missing_rosetta_nstruct.py

```
usage: check_missing_rosetta_nstruct.py [-h] [-n NSTRUCT]
                                        [--pdb_files [PDB_FILES [PDB_FILES ...]]]
                                        [--pdblist PDBLIST] [--dir DIR]

This extremely simple script checks nstruct of the input files and outputs
which nstruct number is missing.

optional arguments:
  -h, --help            show this help message and exit
  -n NSTRUCT, --nstruct NSTRUCT
  --pdb_files [PDB_FILES [PDB_FILES ...]]
                        Path to PDB files we will be checking.
  --pdblist PDBLIST, -l PDBLIST
                        Optional INPUT PDBLIST (without 00s, etc. for which to
                        check
  --dir DIR             The Directory to check. As opposed to a list of pdb
                        files.
```


### insert_natives_table_into_features_db.py

```
usage: insert_natives_table_into_features_db.py [-h] [--pdblist PDBLIST]
                                                [--db DB]

This script takes a PDBLIST of natives and then adds a new table to the
database with struct_id as proper foreign primary key and the native structure
based solely on a search of the name tag.

optional arguments:
  -h, --help         show this help message and exit
  --pdblist PDBLIST  PDBLIST of native structures used.
  --db DB            The database we are working on.
```


### create_score_json_from_scored_decoys.py

```
usage: create_score_json_from_scored_decoys.py [-h] [--prefix PREFIX]
                                               [decoys [decoys ...]]


This script creates a Rosetta score file from a set of structures - by parsing
the score from them. Pass a directory, a PDBLIST, and/or a list of filenames

positional arguments:
  decoys           A directory, a PDBLIST, and/or a list of filenames

optional arguments:
  -h, --help       show this help message and exit
  --prefix PREFIX  Any prefix to use.
```


### RunRosettaMPI.py

```
usage: This program runs Rosetta MPI locally or on a cluster using slurm or qsub.  Relative paths are accepted.
       [-h] [-s S] [-l L] [--np NP] [--nstruct NSTRUCT] [--job_name JOB_NAME]
       [--outdir OUTDIR] [--json_run JSON_RUN] [--extra_options EXTRA_OPTIONS]
       [--script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]] [--jd3]
       [--program PROGRAM] [--print_only] [--local_test] [--one_file_mpi]
       [--job_manager {slurm,qsub,local,local_test}]
       [--job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]]
       [--json_base JSON_BASE] [--compiler {gcc,clang}] [--mpiexec MPIEXEC]
       [--machine_file MACHINE_FILE]

optional arguments:
  -h, --help            show this help message and exit

Common Options:
  -s S                  Path to a pdb file
  -l L                  Path to a list of pdb files
  --np NP               Number of processors to use for MPI. Default = 101
  --nstruct NSTRUCT     The number of structures/parallel runs. Can also set
                        this in any JSON file.
  --job_name JOB_NAME   Set the job name used for mpi_tracer_to_file dir and
                        queue. Default = 'rosetta_run'. (Benchmarking:
                        Override any set in json_base.)
  --outdir OUTDIR, -o OUTDIR
                        Outpath. Default = 'pwd/decoys'
  --json_run JSON_RUN   JSON file for specific Rosetta run. Not required. Pre-
                        Configured JSONS include:
                        ['antibody_designer_even_clus_dock.json',
                        'relax.json', 'remodel.json', 'cluster_features.json',
                        'NGK_smooth.json',
                        'antibody_designer_even_len_clus_dock.json',
                        'pareto_optimal_relax.json', 'relaxed_design.json',
                        'antibody_H3.json', 'antibody_features.json',
                        'antibody_designer_even_len_clus.json',
                        'glycosylate_relax.json', 'dualspace_relax.json',
                        'interface_analyzer.json', 'common_flags.json',
                        'blank.json', 'relaxed_design_ds.json',
                        'antibody_designer_even_clus.json', 'NGK.json',
                        'antibody_designer_dock.json', 'snugdock.json',
                        'antibody_designer.json', 'rosetta_scripts.json',
                        'glycan_clash_check.json', 'NGK_smooth_shap.json']
  --extra_options EXTRA_OPTIONS
                        Extra Rosetta options. Specify in quotes!
  --script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]
                        Any script vars for XML scripts.Specify as you would
                        in Rosetta. like: glycosylation=137A,136A
  --jd3                 Is this app JD3? Must build with
                        extras=mpi,serialization.
  --program PROGRAM     Define the Rosetta program to use if not set in
                        json_run

Testing and Debugging:
  --print_only          Do not actually run anything. Just print setup for
                        review.
  --local_test          Is this a local test? Will change nstruct to 1 and run
                        on 2 processors
  --one_file_mpi        Output all MPI std::out to a single file instead of
                        splitting it.

Special Options for controlling execution:
  --job_manager {slurm,qsub,local,local_test}
                        Job Manager to launch job. (Or none if local or
                        local_test)Default = 'slurm '
  --job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]
                        Extra options for the job manager, such as queue or
                        processor requestsRemove double dashes. Exclusive is
                        on by default. Specify like: -p imperial exclusive.
  --json_base JSON_BASE
                        JSON file for setting up base paths/etc. for the
                        cluster.Default =
                        'database/rosetta/jsons/common_flags.json'
  --compiler {gcc,clang}
                        Set the compiler used. Will set clang automatically
                        for macos. Default = 'gcc'
  --mpiexec MPIEXEC     Specify a particular path (or type of) MPI exec.
                        Default is srun (due to vax). If local or local test,
                        will use mpiexex
  --machine_file MACHINE_FILE
                        Optional machine file for passing to MPI
```


## PyRosetta
---------

### find_my_residues.py

```
Simple app to scan a PDB file and print PDB info and Rosetta understood chains
and resnums.

positional arguments:
  pdb_file              The PDB file to scan.

optional arguments:
  -h, --help            show this help message and exit
  --chain CHAIN, -c CHAIN
                        Specify only a single chain to scan.
  --echo_input, -e      Echo the input structure as output. This is to check
                        how Rosettta worked reading it.
```

### find_my_glycans.py

```
This simple script aims to identify glycosylated positions in a PDB and thier associated rosetta Resnums.
Please specifiy a PDB as the only argument to this script.
```

### get_phi_psi.py

```
usage: Get Phi/Psi of all residues in protein or a range of residues
       [-h] -s S [--start START] [--span SPAN]

optional arguments:
  -h, --help     show this help message and exit
  -s S           Input Structure
  --start START  Starting resnum (pose/PDB - EX:24L)
  --span SPAN    Number of residues to print from start
```

### create_glycan_scanning_job.py

```
usage: Create a JD3 Job Definition file to scan compatible surface residues and do denovo glycosylation and modeling. This is for IDEAL sequons only
       [-h] [--selections SELECTIONS] [--selector SELECTOR] -s S
       [--include_prolines] [--include_glycines_if_D] [--design_plus_1]
       [--enable_T_and_S] [--design_sequon_regardless_of_plus_two_layer]
       [--include_boundary_buried]
       [--include_boundary_hydrophobics INCLUDE_BOUNDARY_HYDROPHOBICS]
       [--glycan_relax_rounds GLYCAN_RELAX_ROUNDS]
       [--skip_functional_sites SKIP_FUNCTIONAL_SITES]

optional arguments:
  -h, --help            show this help message and exit
  --selections SELECTIONS, -x SELECTIONS
                        Input XML to pull ResidueSelections to limit scan.
  --selector SELECTOR   Name of a residue selector from input xml to limit
                        search to. Loops, regions, etc. This will be combined
                        as AND logic
  -s S                  Input PDB we will be scanning.
  --include_prolines
  --include_glycines_if_D
                        Include glycines? Glycines can either be D/L
                        conformation. Set this option to only include glycines
                        if they are D. Otherwise, skip them at +2
  --design_plus_1       Design the +1 position?
  --enable_T_and_S      Enable Threonine and Serine at +2? By default we use
                        only threonine as this has been shown to havehigher
                        occupancy at the glycan site in general.
  --design_sequon_regardless_of_plus_two_layer
                        Enable design of the primary sequon if the +2 residue
                        is part of the core (and not already ser/thr)?
  --include_boundary_buried
                        Only use the LayerSelector to define the core for the
                        +2 residues. Otherwise, we use the SC sasa measured in
                        addition for the boundary residues and do not include
                        these if not designing
  --include_boundary_hydrophobics INCLUDE_BOUNDARY_HYDROPHOBICS
                        Include hydrophobic boundary residues (for +2 design)?
                        By default we leave these out to maintain foldability
  --glycan_relax_rounds GLYCAN_RELAX_ROUNDS
                        Number of glycan relax rounds (which is multiplied by
                        n glycans. Default is 100 (25 in app), but since this
                        is per-position, 100 is reasonable.
  --skip_functional_sites SKIP_FUNCTIONAL_SITES
                        Comma-separated List of residues (PDBnumbering -ex
                        286A) to skip as including as a potential sequon. This
                        means we skip any potential sequon that includes these
                        residues.
```


### get_mutation_energy.py

```
usage: get_mutation_energy.py [-h] [--pdb PDB] [--outpath OUTPATH]
                              [--filename FILENAME] [--region REGION]
                              [--relax_whole_structure] [--alanine_scan]

Basic app to get mutation energy of each residue in a particular region using
PyRosetta

optional arguments:
  -h, --help            show this help message and exit
  --pdb PDB, -s PDB     Path to PDB file. Required.
  --outpath OUTPATH, -o OUTPATH
                        Full output directory path. Default is pwd/RESULTS
  --filename FILENAME, -n FILENAME
                        The filename of the results file
  --region REGION, -r REGION
                        (region designated as start:end:chain) If none is
                        given, will use whole PDB
  --relax_whole_structure, -m
                        Relax the whole structure? Default is to only relax
                        chain under question. If no region is set, will
                        default to true
  --alanine_scan, -a    Trigger the script to do an alanine scan of the
                        mutations instead of a full mutational scan.
```


### build_loop_pyrosetta.py

```
usage: build_loop_pyrosetta.py [-h] --start START --stop STOP --sequence
                               SEQUENCE [--out_prefix OUT_PREFIX]
                               [--retain_aligned_roots] --pdb PDB [--kic]
                               [--dump_midpoints]

This script builds a loop between two places in a structure with the given
sequence, and closes the loop.It is not meant to be the last modeling step,
just to create missing density or to prepare for loop modeling.

optional arguments:
  -h, --help            show this help message and exit
  --start START         Starting resnum. Ex: 24L
  --stop STOP           Ending resnum. Ex. 42L.
  --sequence SEQUENCE   Sequence of the loop
  --out_prefix OUT_PREFIX
                        Any prefix to give results.
  --retain_aligned_roots
                        Attempt to keep any aligned root residues during the
                        build
  --pdb PDB, -s PDB     Input model
  --kic                 Run KIC peruturber after closing the loop?
  --dump_midpoints      Dump midpoint PDBs?
```


## Antibody_utils
--------------

### split_antibody_components.py

```
usage: split_antibody_components.py [-h] [--any_structure] --ab_dir AB_DIR
                                    --output_dir OUTPUT_DIR

Script for splitting AHO renumbered antibodies into Fv, Fc, and linker regions

optional arguments:
  -h, --help            show this help message and exit
  --any_structure       Be default, we only output structures with both L/H.
                        Pass this option to split structures that are L or H
                        only.
  --ab_dir AB_DIR, -a AB_DIR
                        Antibody Directory with AHO-renumbered structures to
                        split. Can be .pdb, or .pdb.gz
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        Output Directory for antibody structures.
```


### generate_rabd_features_dbs.py

```
usage: Creates Features Databases for antibody design using MPI.  This uses RunRosettaMPI, so that it can be run locally or on a cluster.
       [-h] [--indir INDIR]
       [--analysis {all,cluster_features,antibody_features}]
       [--use_present_dbs] --db_prefix DB_PREFIX [--native] [-s S] [-l L]
       [--np NP] [--nstruct NSTRUCT] [--job_name JOB_NAME] [--outdir OUTDIR]
       [--json_run JSON_RUN] [--extra_options EXTRA_OPTIONS]
       [--script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]] [--jd3] [--print_only]
       [--local_test] [--one_file_mpi]
       [--job_manager {slurm,qsub,local,local_test}]
       [--job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]]
       [--json_base JSON_BASE] [--compiler {gcc,clang}] [--mpiexec MPIEXEC]
       [--machine_file MACHINE_FILE] [--db_mode {sqlite3,mysql,postgres}]
       [--db_name DB_NAME] [--db_batch DB_BATCH] [--db_in] [--db_out]

optional arguments:
  -h, --help            show this help message and exit

RAbD Analyze:
  Options specific for Analysis of RAbD Output Structures

  --indir INDIR         Input directory used for either PDBLIST path (if
                        PDBLIST and this is given) or a path full of PDBs to
                        analyze
  --analysis {all,cluster_features,antibody_features}
                        Analysis to run on PDBs
  --use_present_dbs     Do not attempt to delete features databases present
  --db_prefix DB_PREFIX
                        Prefix to use for output databases. Recommended to use
                        the design and strategy name
  --native              Indicate that this is a set of native structures

Common Options:
  -s S                  Path to a pdb file
  -l L                  Path to a list of pdb files
  --np NP               Number of processors to use for MPI. Default = 101
  --nstruct NSTRUCT     The number of structures/parallel runs. Can also set
                        this in any JSON file.
  --job_name JOB_NAME   Set the job name used for mpi_tracer_to_file dir and
                        queue. Default = 'rosetta_run'. (Benchmarking:
                        Override any set in json_base.)
  --outdir OUTDIR, -o OUTDIR
                        Outpath. Default = 'pwd/decoys'
  --json_run JSON_RUN   JSON file for specific Rosetta run. Not required. Pre-
                        Configured JSONS include:
                        ['antibody_designer_even_clus_dock.json',
                        'relax.json', 'remodel.json', 'cluster_features.json',
                        'NGK_smooth.json',
                        'antibody_designer_even_len_clus_dock.json',
                        'pareto_optimal_relax.json', 'relaxed_design.json',
                        'antibody_H3.json', 'antibody_features.json',
                        'antibody_designer_even_len_clus.json',
                        'glycosylate_relax.json', 'dualspace_relax.json',
                        'interface_analyzer.json', 'common_flags.json',
                        'blank.json', 'relaxed_design_ds.json',
                        'antibody_designer_even_clus.json', 'NGK.json',
                        'antibody_designer_dock.json', 'snugdock.json',
                        'antibody_designer.json', 'rosetta_scripts.json',
                        'glycan_clash_check.json', 'NGK_smooth_shap.json']
  --extra_options EXTRA_OPTIONS
                        Extra Rosetta options. Specify in quotes!
  --script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]
                        Any script vars for XML scripts.Specify as you would
                        in Rosetta. like: glycosylation=137A,136A
  --jd3                 Is this app JD3? Must build with
                        extras=mpi,serialization.

Testing and Debugging:
  --print_only          Do not actually run anything. Just print setup for
                        review.
  --local_test          Is this a local test? Will change nstruct to 1 and run
                        on 2 processors
  --one_file_mpi        Output all MPI std::out to a single file instead of
                        splitting it.

Special Options for controlling execution:
  --job_manager {slurm,qsub,local,local_test}
                        Job Manager to launch job. (Or none if local or
                        local_test)Default = 'slurm '
  --job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]
                        Extra options for the job manager, such as queue or
                        processor requestsRemove double dashes. Exclusive is
                        on by default. Specify like: -p imperial exclusive.
  --json_base JSON_BASE
                        JSON file for setting up base paths/etc. for the
                        cluster.Default =
                        'database/rosetta/jsons/common_flags.json'
  --compiler {gcc,clang}
                        Set the compiler used. Will set clang automatically
                        for macos. Default = 'gcc'
  --mpiexec MPIEXEC     Specify a particular path (or type of) MPI exec.
                        Default is srun (due to vax). If local or local test,
                        will use mpiexex
  --machine_file MACHINE_FILE
                        Optional machine file for passing to MPI

Relational Databases:
  Options for Rosetta Database input and output. Use for features or for
  inputting and output structures as databases

  --db_mode {sqlite3,mysql,postgres}
                        Set the mode for Rosetta to use if using a database.
                        Features will be output to a database. If not sqlite3,
                        must build Rosetta with extras. If any post-processing
                        is required, such as combining sqlite3 dbs, will do
                        this. Default DB mode for features is sqlite3.
  --db_name DB_NAME     In or Out database name
  --db_batch DB_BATCH   Batch of structures.
  --db_in               Use an input database
  --db_out              Use an output database
```


### RAbD_Jade.py

```
usage: RAbD_Jade.py [-h] [--db_dir DB_DIR] [--analysis_name ANALYSIS_NAME]
                    [--native NATIVE] [--root_dir ROOT_DIR]
                    [--cdrs [{L1,H1,L1,H2,L3,H3} [{L1,H1,L1,H2,L3,H3} ...]]]
                    [--pyigclassify_dir PYIGCLASSIFY_DIR]
                    [--jsons [JSONS [JSONS ...]]]

GUI application to analyze designs output by RosettaAntibodyDesign. Designs
should first be analyzed by both the AntibodyFeatures and CDRClusterFeatures
reporters into sqlite3 databases.

optional arguments:
  -h, --help            show this help message and exit
  --db_dir DB_DIR       Directory with databases to compare. DEFAULT =
                        databases
  --analysis_name ANALYSIS_NAME
                        Main directory to complete analysis. DEFAULT =
                        prelim_analysis
  --native NATIVE       Any native structure to compare to
  --root_dir ROOT_DIR   Root directory to run analysis from
  --cdrs [{L1,H1,L1,H2,L3,H3} [{L1,H1,L1,H2,L3,H3} ...]]
                        A list of CDRs for the analysis (Not used for Features
                        Reporters)
  --pyigclassify_dir PYIGCLASSIFY_DIR
                        Optional PyIgClassify Root Directory with DBOUT. Used
                        for debugging.
  --jsons [JSONS [JSONS ...]], -j [JSONS [JSONS ...]]
                        Analysis JSONs to use. See RAbD_MB.AnalysisInfo for
                        more on what is in the JSON.The JSON allows us to
                        specify the final name, decoy directory, and features
                        db associated with the benchmark as well as all
                        options that went into it.
```


### convert_IMGT_to_fasta.py

```
usage: convert_IMGT_to_fasta.py [-h] --inpath INPATH --outpath OUTPATH

This script converts an IMGT output file (5_AA-seqs.csv) to a FASTA. All
Framework and CDRs are concatonated. * is skipped. The FASTA file can then be
used by PyIgClassify.

optional arguments:
  -h, --help            show this help message and exit
  --inpath INPATH, -i INPATH
                        Input IMGT file path
  --outpath OUTPATH, -o OUTPATH
                        Output Fasta outfile path.
```


### order_ab_chains.py

```
usage: order_ab_chains.py [-h] [--in_dir IN_DIR] [--in_pdblist IN_PDBLIST]
                          [--in_single IN_SINGLE] [--out_dir OUT_DIR]
                          [--reverse]

Reorders PDBFiles in a dirctory according to A_LH in order for Rosetta
Antibody Design benchmarking. Removes HetAtm

optional arguments:
  -h, --help            show this help message and exit
  --in_dir IN_DIR, -i IN_DIR
                        Input Directory of PDB files listed in any passed
                        PDBLIST. Default=PWD
  --in_pdblist IN_PDBLIST, -l IN_PDBLIST
                        Input PDBList file. Assumes PDBList has no paths and
                        requires an input directory as if we run Rosetta.
  --in_single IN_SINGLE, -s IN_SINGLE
                        Path to Input PDB File, instead of list.
  --out_dir OUT_DIR, -d OUT_DIR
                        Output Directory. Resultant PDB files will go here.
  --reverse, -r         Reverse order (LH_A instead of A_LH). Used for
                        snugdock
```


### match_antibody_structures.py

```
usage: match_antibody_structures.py [-h] --db DB --ab_dir AB_DIR --where WHERE
                                    [--outdir OUTDIR] [--prefix PREFIX]
                                    [--cdr CDR] [--native NATIVE]

This App aims to make pymol alignments using the PyIgClassify database and
structures, matching specific criterion.

optional arguments:
  -h, --help            show this help message and exit

Required Arguments:
  --db DB, -d DB        Database to use from PyIgClassify.
  --ab_dir AB_DIR, -b AB_DIR
                        Directory with renumbered antibody PDBs (Full or CDRs-
                        only)
  --where WHERE, -w WHERE
                        Your where clause for the db in quotes. Not including
                        WHERE. Use ' ' for string matches

Other Arguments:
  --outdir OUTDIR, -o OUTDIR
                        Output directory.
  --prefix PREFIX, -p PREFIX
                        Output prefix
  --cdr CDR, -c CDR     Optionally load the CDR PDBs of the given type in the
                        ab_dir. If this option is set, the ab_dir should be of
                        CDRs only from PyIgClassify.
  --native NATIVE, -n NATIVE
                        Align everything to this PDB, the native or something
                        you are interested in.
```


### create_features_json.py

```
usage: create_features_json.py [-h] [--databases [DATABASES [DATABASES ...]]]
                               [--script {cluster,antibody,interface,antibody_minimal}]
                               [--db_path DB_PATH] [--outdir OUTDIR]
                               [--outname OUTNAME]
                               [--add_comparison_to_this_json ADD_COMPARISON_TO_THIS_JSON]
                               [--run]

This script will create either cluster features or antibody features json for
use in Features R script. Example Cmd-line: python create_features_json.py
--database databases/baseline_comparison.txt --scripts cluster

optional arguments:
  -h, --help            show this help message and exit
  --databases [DATABASES [DATABASES ...]], -l [DATABASES [DATABASES ...]]
                        List of dbs: db_name,short_name,ref keyword if the
                        reference databaseSeparated by white space.
  --script {cluster,antibody,interface,antibody_minimal}, -s {cluster,antibody,interface,antibody_minimal}
                        Script type. Will setup the appropriate output formats
                        and R scripts
  --db_path DB_PATH, -p DB_PATH
                        Path to databases. Default is pwd/databases
  --outdir OUTDIR, -o OUTDIR
                        Where to put the result of the analysis scripts.
                        Currently unsupported by the features framework.
  --outname OUTNAME, -n OUTNAME
                        Output file name of json file
  --add_comparison_to_this_json ADD_COMPARISON_TO_THIS_JSON, -a ADD_COMPARISON_TO_THIS_JSON
                        Add all this data to this json as more sample sources.
  --run, -r             Go ahead and run compare_sample_sources.R. Must be in
                        path!!
```



## Pdb_utils
---------

### remove_redundent_lines.py



### delete_chains.py

```
usage: Delete chains from a PDB (not cif) file. Only works with ATOM records.  
       [-h] -s S [-c CHAINS] [-k KEEP_CHAINS] [--suffix SUFFIX]

optional arguments:
  -h, --help            show this help message and exit
  -s S                  PDB file
  -c CHAINS, --chains CHAINS
                        Comma-separated list of chains to remove
  -k KEEP_CHAINS, --keep_chains KEEP_CHAINS
                        Chains to keep. Use this instead of the chains option
  --suffix SUFFIX       Suffix to add to output file
```


### place_TERs.py

```
usage: place_TERs.py [-h] [pdb_files [pdb_files ...]]

This script places ters between ATOM/HETATM columns. This is currently needed
to reload symmetrized glycan posescreated by the god aweful make_symm_file.pl
Rosetta script. USE: place_TERs.py my_pdb - Does it in place.

positional arguments:
  pdb_files   Path to PDB files we will be stripping.

optional arguments:
  -h, --help  show this help message and exit
```

### strip_ANISOU.py

```
usage: strip_ANISOU.py [-h] [pdb_files [pdb_files ...]]

Strips ANISOU lines out of PDBs.

positional arguments:
  pdb_files   Path to PDB file we will be stripping.

optional arguments:
  -h, --help  show this help message and exit
```

### strip_ter.py



### fix_space_chain.py




## Antibody_benchmark_utils
------------------------

### bm-RAbD_Jade.py

```
usage: bm-RAbD_Jade.py [-h] [--main_dir MAIN_DIR] [--out_dir OUT_DIR] --jsons
                       [JSONS [JSONS ...]]

This program is a GUI used for benchmarking Rosetta Antibody Design.Before
running this application, you will probably want to run
'run_rabd_features_for_benchmarks.py to create the databases required.

optional arguments:
  -h, --help            show this help message and exit
  --main_dir MAIN_DIR   Main working directory. Not Required. Default = PWD
  --out_dir OUT_DIR     Output data directory. Not Required. Default =
                        pooled_data
  --jsons [JSONS [JSONS ...]], -j [JSONS [JSONS ...]]
                        Analysis JSONs to use. See RAbD_MB.AnalysisInfo for
                        more on what is in the JSON.The JSON allows us to
                        specify the final name, decoy directory, and features
                        db associated with the benchmark as well as all
                        options that went into it.
```

### bm-calculate_plot_mc_acceptance_rabd.py

```
usage: bm-calculate_plot_mc_acceptance_rabd.py [-h] --jsons
                                               [JSONS [JSONS ...]]
                                               [--data_outdir DATA_OUTDIR]
                                               [--plot_outdir PLOT_OUTDIR]
                                               [--root_dataset_dir ROOT_DATASET_DIR]

Calculates and plots monte carlo acceptance values for antibody design
benchmarking.

optional arguments:
  -h, --help            show this help message and exit
  --jsons [JSONS [JSONS ...]], -j [JSONS [JSONS ...]]
                        Analysis JSONs to use. See RAbD_MB.AnalysisInfo for
                        more on what is in the JSON.The JSON allows us to
                        specify the final name, decoy directory, and features
                        db associated with the benchmark as well as all
                        options that went into it.
  --data_outdir DATA_OUTDIR, -o DATA_OUTDIR
                        Path to outfile. DEFAULT = data
  --plot_outdir PLOT_OUTDIR, -p PLOT_OUTDIR
                        DIR for plots. DEFAULT = plots/mc_benchmarks
  --root_dataset_dir ROOT_DATASET_DIR
                        List of PDBIds to use for individual PDB output.
                        DEFAULT = datasets/pdblists
```


### bm-output_all_clusters.py

```
usage: bm-output_all_clusters.py [-h] --jsons [JSONS [JSONS ...]]
                                 [--data_outdir DATA_OUTDIR]

Calculates and plots monte carlo acceptance values for antibody design
benchmarking.

optional arguments:
  -h, --help            show this help message and exit
  --jsons [JSONS [JSONS ...]], -j [JSONS [JSONS ...]]
                        Analysis JSONs to use. See RAbD_MB.AnalysisInfo for
                        more on what is in the JSON.The JSON allows us to
                        specify the final name, decoy directory, and features
                        db associated with the benchmark as well as all
                        options that went into it.
  --data_outdir DATA_OUTDIR, -o DATA_OUTDIR
                        Path to outfile. DEFAULT = data
```


### RunRosettaBenchmarksMPI.py

```
usage: This program runs Rosetta MPI locally or on a cluster using slurm or qsub.  Relative paths are accepted.
       [-h] [-s S] [-l L] [--np NP] [--nstruct NSTRUCT] [--job_name JOB_NAME]
       [--outdir OUTDIR] [--json_run JSON_RUN] [--extra_options EXTRA_OPTIONS]
       [--script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]] [--jd3]
       [--program PROGRAM] [--print_only] [--local_test] [--one_file_mpi]
       [--job_manager {slurm,qsub,local,local_test}]
       [--job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]]
       [--json_base JSON_BASE] [--compiler {gcc,clang}] [--mpiexec MPIEXEC]
       [--machine_file MACHINE_FILE] [--json_benchmark JSON_BENCHMARK]
       [--separate_job_per_pdb]

optional arguments:
  -h, --help            show this help message and exit

Common Options:
  -s S                  Path to a pdb file
  -l L                  Path to a list of pdb files
  --np NP               Number of processors to use for MPI. Default = 101
  --nstruct NSTRUCT     The number of structures/parallel runs. Can also set
                        this in any JSON file.
  --job_name JOB_NAME   Set the job name used for mpi_tracer_to_file dir and
                        queue. Default = 'rosetta_run'. (Benchmarking:
                        Override any set in json_base.)
  --outdir OUTDIR, -o OUTDIR
                        Outpath. Default = 'pwd/decoys'
  --json_run JSON_RUN   JSON file for specific Rosetta run. Not required. Pre-
                        Configured JSONS include:
                        ['antibody_designer_even_clus_dock.json',
                        'relax.json', 'remodel.json', 'cluster_features.json',
                        'NGK_smooth.json',
                        'antibody_designer_even_len_clus_dock.json',
                        'pareto_optimal_relax.json', 'relaxed_design.json',
                        'antibody_H3.json', 'antibody_features.json',
                        'antibody_designer_even_len_clus.json',
                        'glycosylate_relax.json', 'dualspace_relax.json',
                        'interface_analyzer.json', 'common_flags.json',
                        'blank.json', 'relaxed_design_ds.json',
                        'antibody_designer_even_clus.json', 'NGK.json',
                        'antibody_designer_dock.json', 'snugdock.json',
                        'antibody_designer.json', 'rosetta_scripts.json',
                        'glycan_clash_check.json', 'NGK_smooth_shap.json']
  --extra_options EXTRA_OPTIONS
                        Extra Rosetta options. Specify in quotes!
  --script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]
                        Any script vars for XML scripts.Specify as you would
                        in Rosetta. like: glycosylation=137A,136A
  --jd3                 Is this app JD3? Must build with
                        extras=mpi,serialization.
  --program PROGRAM     Define the Rosetta program to use if not set in
                        json_run

Testing and Debugging:
  --print_only          Do not actually run anything. Just print setup for
                        review.
  --local_test          Is this a local test? Will change nstruct to 1 and run
                        on 2 processors
  --one_file_mpi        Output all MPI std::out to a single file instead of
                        splitting it.

Special Options for controlling execution:
  --job_manager {slurm,qsub,local,local_test}
                        Job Manager to launch job. (Or none if local or
                        local_test)Default = 'slurm '
  --job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]
                        Extra options for the job manager, such as queue or
                        processor requestsRemove double dashes. Exclusive is
                        on by default. Specify like: -p imperial exclusive.
  --json_base JSON_BASE
                        JSON file for setting up base paths/etc. for the
                        cluster.Default =
                        'database/rosetta/jsons/common_flags.json'
  --compiler {gcc,clang}
                        Set the compiler used. Will set clang automatically
                        for macos. Default = 'gcc'
  --mpiexec MPIEXEC     Specify a particular path (or type of) MPI exec.
                        Default is srun (due to vax). If local or local test,
                        will use mpiexex
  --machine_file MACHINE_FILE
                        Optional machine file for passing to MPI

Benchmark Options:
  Options specific for Benchmarking

  --json_benchmark JSON_BENCHMARK
                        JSON file for setting up specific benchmark
  --separate_job_per_pdb
                        Separate each PDB in any PDB list given (to python
                        app) into a separate Job and Directory
```


### bm-calculate_recoveries_and_risk_ratios.py

```
usage: bm-calculate_recoveries_and_risk_ratios.py [-h] --jsons
                                                  [JSONS [JSONS ...]]
                                                  [--data_outdir DATA_OUTDIR]

Calculates and plots monte carlo acceptance values for antibody design
benchmarking.

optional arguments:
  -h, --help            show this help message and exit
  --jsons [JSONS [JSONS ...]], -j [JSONS [JSONS ...]]
                        Analysis JSONs to use. See RAbD_MB.AnalysisInfo for
                        more on what is in the JSON.The JSON allows us to
                        specify the final name, decoy directory, and features
                        db associated with the benchmark as well as all
                        options that went into it.
  --data_outdir DATA_OUTDIR, -o DATA_OUTDIR
                        Path to outfile. DEFAULT = data
```


### bm-calculate_graft_closure_rabd.py

```
usage: bm-calculate_graft_closure_rabd.py [-h] [--dir DIR] [--outfile OUTFILE]
                                          [--use_ensemble]
                                          [--match_name MATCH_NAME]

Calculate the frequence of graft closures.

optional arguments:
  -h, --help            show this help message and exit
  --dir DIR, -i DIR     Input directory
  --outfile OUTFILE, -o OUTFILE
                        Path to outfile
  --use_ensemble        Use ensembles in calculation
  --match_name MATCH_NAME
                        Match a subexperiment in the file name such as relax
```


### bm-plot_features.py



### bm-run_rabd_benchmarks.py

```
usage: This program runs Rosetta MPI locally or on a cluster using slurm or qsub.  Relative paths are accepted.
       [-h] [-s S] [-l L] [--np NP] [--nstruct NSTRUCT] [--job_name JOB_NAME]
       [--outdir OUTDIR] [--json_run JSON_RUN] [--extra_options EXTRA_OPTIONS]
       [--script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]] [--jd3] [--print_only]
       [--local_test] [--one_file_mpi]
       [--job_manager {slurm,qsub,local,local_test}]
       [--job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]]
       [--json_base JSON_BASE] [--compiler {gcc,clang}] [--mpiexec MPIEXEC]
       [--machine_file MACHINE_FILE] [--json_benchmark JSON_BENCHMARK]
       [--separate_job_per_pdb]

optional arguments:
  -h, --help            show this help message and exit

Common Options:
  -s S                  Path to a pdb file
  -l L                  Path to a list of pdb files
  --np NP               Number of processors to use for MPI. Default = 101
  --nstruct NSTRUCT     The number of structures/parallel runs. Can also set
                        this in any JSON file.
  --job_name JOB_NAME   Set the job name used for mpi_tracer_to_file dir and
                        queue. Default = 'rosetta_run'. (Benchmarking:
                        Override any set in json_base.)
  --outdir OUTDIR, -o OUTDIR
                        Outpath. Default = 'pwd/decoys'
  --json_run JSON_RUN   JSON file for specific Rosetta run. Not required. Pre-
                        Configured JSONS include:
                        ['antibody_designer_even_clus_dock.json',
                        'relax.json', 'remodel.json', 'cluster_features.json',
                        'NGK_smooth.json',
                        'antibody_designer_even_len_clus_dock.json',
                        'pareto_optimal_relax.json', 'relaxed_design.json',
                        'antibody_H3.json', 'antibody_features.json',
                        'antibody_designer_even_len_clus.json',
                        'glycosylate_relax.json', 'dualspace_relax.json',
                        'interface_analyzer.json', 'common_flags.json',
                        'blank.json', 'relaxed_design_ds.json',
                        'antibody_designer_even_clus.json', 'NGK.json',
                        'antibody_designer_dock.json', 'snugdock.json',
                        'antibody_designer.json', 'rosetta_scripts.json',
                        'glycan_clash_check.json', 'NGK_smooth_shap.json']
  --extra_options EXTRA_OPTIONS
                        Extra Rosetta options. Specify in quotes!
  --script_vars [SCRIPT_VARS [SCRIPT_VARS ...]]
                        Any script vars for XML scripts.Specify as you would
                        in Rosetta. like: glycosylation=137A,136A
  --jd3                 Is this app JD3? Must build with
                        extras=mpi,serialization.

Testing and Debugging:
  --print_only          Do not actually run anything. Just print setup for
                        review.
  --local_test          Is this a local test? Will change nstruct to 1 and run
                        on 2 processors
  --one_file_mpi        Output all MPI std::out to a single file instead of
                        splitting it.

Special Options for controlling execution:
  --job_manager {slurm,qsub,local,local_test}
                        Job Manager to launch job. (Or none if local or
                        local_test)Default = 'slurm '
  --job_manager_opts [JOB_MANAGER_OPTS [JOB_MANAGER_OPTS ...]]
                        Extra options for the job manager, such as queue or
                        processor requestsRemove double dashes. Exclusive is
                        on by default. Specify like: -p imperial exclusive.
  --json_base JSON_BASE
                        JSON file for setting up base paths/etc. for the
                        cluster.Default =
                        'database/rosetta/jsons/common_flags.json'
  --compiler {gcc,clang}
                        Set the compiler used. Will set clang automatically
                        for macos. Default = 'gcc'
  --mpiexec MPIEXEC     Specify a particular path (or type of) MPI exec.
                        Default is srun (due to vax). If local or local test,
                        will use mpiexex
  --machine_file MACHINE_FILE
                        Optional machine file for passing to MPI

Benchmark Options:
  Options specific for Benchmarking

  --json_benchmark JSON_BENCHMARK
                        JSON file for setting up specific benchmark
  --separate_job_per_pdb
                        Separate each PDB in any PDB list given (to python
                        app) into a separate Job and Directory

```
