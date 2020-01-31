"""
The following directory paths should be modified to reflect the corresponding locations
in your environment.  Leave off the final "/" from these paths.

CORPUS_ROOT: Root of subdirectories to hold intermediate results of ACT analysis 
TW_CORPUS_ROOT: Root for xml texts and results of preprocessing/linguistic analysis
CODE_ROOT: Home of all ACT code except Mallet code (location specified in mallet_config.py).

"""
import os

CORPUS_ROOT = os.path.join('U:/', 'Workspaces', 'techknowledgist', 'thyme', 'output',
                           'corpus')  # "/home/j/anick/tw/roles/data/corpora"
CODE_ROOT = dirpath = os.getcwd()  # "/home/j/anick/tw/roles/code"
TW_CORPUS_ROOT = os.path.join('U:/', 'Workspaces', 'techknowledgist', 'thyme', 'output',
                              'corpus')  # "/home/j/corpuswork/techwatch/corpora"

# mallet parameters used in constructing file names
CLASSIFIER_TYPE = "NB"
CONTEXT_TYPE = "wos"
