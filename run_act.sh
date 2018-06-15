# sh run_act.sh uspto/2018/ipa180104/data/d3_feats/01/files/0001 sp2 tas 9999 9999 100
# sh run_act.sh uspto/2018/ipa180104/data/d3_feats/01/files/0001 u1 tas 9999 9999 100
# nohup sh run_act.sh uspto/2018/ipa180104/data/d3_feats/01/files uspto_2018 tas 9999 9999 500 &


# BEFORE RUNNING THIS SCRIPT:
# Modify roles_config.py to provide paths for CORPUS_ROOT, CODE_ROOT, and TW_CORPUS_ROOT
# Modify act_config.sh to provide paths for python2.7, CORPUS_ROOT, CODEDIR, and TW_CORPUS_ROOT
# modify mallet_config.py to provide path for MALLET_DIR

# args:

# SOURCE_SUBDIR: subpath from TW_CORPUS_ROOT to the directory under which 
#    all <d3_feats>.xml files to be processed are located
# CORPUS_NAME: A name for your corpus.  Output will be written to CORPUS_ROOT/CORPUS_NAME 
# SECTIONS: This arg should always be set to tas (process all sections of a document).
#    Eventually, we may support the option ta (limit processing to title and abstract only)
# START_YEAR: This should be set to 9999.  Eventually, we may support processing of documents 
#    within a range of years.
# END_YEAR: This should be set to 9999.  Eventually, we may support processing of documents 
#    within a range of years.
# MAX_DOC_TERMS: The number of terms to extract from each document for construction of
#    an elasticsearch index mapping documents to terms.  A number between 100 and 1000 is reasonable.
#    Ideally, we would avoid the claims and reference sections of a patent, which contain many repeat
#    and irrelevent terms.

#NOTE: Porter stemmer "Unicode warning" messages in output to screen can be ignored.

# import variable names and aliases
source ./act_config.sh

SOURCE_SUBDIR=$1
CORPUS_NAME=$2
SECTIONS=$3
START_YEAR=$4
END_YEAR=$5
MAX_DOC_TERMS=$6

XML_SOURCE_DIR=$TW_CORPUS_ROOT/$SOURCE_SUBDIR
TARGET_DIR=$LOCAL_CORPUS_ROOT/$CORPUS_NAME
FILELISTS=$TARGET_DIR/filelists

python2.7 act_make_filelist.py $XML_SOURCE_DIR $LOCAL_CORPUS_ROOT $CORPUS_NAME $START_YEAR 

python2.7 act_tf.py $FILELISTS $TARGET_DIR $SECTIONS $START_YEAR $END_YEAR True $MAX_DOC_TERMS

python2.7 act_role.py $LOCAL_CORPUS_ROOT $CORPUS_NAME $SECTIONS $START_YEAR $START_YEAR act

# Run using Naive Bayes classifier (NB)
python2.7 act_run_mallet.py $LOCAL_CORPUS_ROOT $CORPUS_NAME $SECTIONS NB woc $START_YEAR 1
