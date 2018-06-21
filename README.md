# ACT

ACT Role detection attempts to classify a term as <b>A</b>ttribute, <b>C</b>omponent or <b>T</b>ask.  This is primarily to allow the user interface to present terms according to their function.  Most terms are components, so this allows the attributes and tasks to be identified more easily.  Role detection is performed in several steps.  An initial (seed) set of relatively unambiguous features is used to label terms into one of the three categories.  These labeled terms are then used to build a classifier.


### How to run the code


##### 1. Assumptions

We assume that documents are to be temporally labeled by application year (if patents) or by publication year (if research papers). We also assume that we have documents organized into subcorpora by domain and within year for each domain. As a prior step to running functions in this package, a corpus must be set up with a set of domains and a range of years. Each subcorpus must be processed to the point of creating feature files (d3_feats). See https://github.com/techknowledgist/tgist-features for documentation of the prerequisite steps.


##### 2. Install Mallet

Mallet can not be used out of the box. An adapted Mallet distribution will be made available for download, but for now there is a distribution on the Brandeis CS machines at `/home/j/anick/tw/tools/mallet-2.0.7`.

Once you have installed Mallet you need to edit a line in `mallet-config.py`:

```
# path to mallet bin (without a final slash)
MALLET_DIR = "/home/j/anick/tw/tools/mallet-2.0.7/bin"
```

Replace the directory with the one where you installed Mallet, note that the `bin` subdirectory is part of the path here.


##### 3. Edit the configuration files

Configuration settings are in two files (in addition to the mallet configuration file). One is `roles_config.py`, which has three variables that need to be set:

1. `CODE_ROOT` - the directory where your code (and this readme file) is installed.

2. `CORPUS_ROOT` - directories where intermediate and final results are written.

3. `TW_CORPUS_ROOT` - root for xml texts and results of preprocessing/linguistic analysis.

The other file is `act_config.sh`, with the following variables:

1. `python2.7` - path to the Python 2.7 executable, for example `/usr/local/bin/python2.7`.

2. `CODEDIR` - same as CODE_ROOT above.

3. `LOCAL_CORPUS_ROOT` - same as CORPUS_ROOT above.

4. `TW_CORPUS_ROOT` - same as TW_CORPUS_ROOT above.


##### 4. Run the main script

The main script is `run_act.sh`, here is an example of how to run it:

```
$  sh run_act.sh uspto/2018/ipa180104/data/d3_feats/01/files/0001 sp2 tas 9999 9999 100
```

This takes the data from a subdirectory of `TW_CORPUS_ROOT`, specified as the first argument. Results are written to `CORPUS_ROOT/sp2`. Two files are of interest:

- `NB.IG50.test1.woc.9999.results.classes` - the first two columns have the term and the top ranked class
- `9999.canon` - canonical forms for terms, mapping terms to lemmas
