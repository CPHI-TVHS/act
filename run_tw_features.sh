# run_tw_features.sh

# sh run_tw_features.sh SignalProcessing 2002 2002 ta
 

# script to run tw_features.sh with set parameters
# this populates the directory $TARGET/data/term_features/ with a subdirectory for each year
# specified, creating one file for each d3_feats file in the source corpus.  Each 
# file contains a term, a feature, and the count of appearances of the feature with the term.
# The option ta/tas indicates which source file sections to use (title, abstract, summary)

# uses tf.py and term_features.sh

# example calls
# modified to take three parameters corpus, start_year, end_year
# sh run_term_features.sh wos-cs-520k 1997 1997
# sh run_term_features.sh ln-us-all-600k 1997 2007

# sh run_term_features.sh ln-us-A30-electrical-circuits 2002 2002
# 
# sh run_term_features.sh ln-us-A27-molecular-biology 1997 2007
# sh run_term_features.sh ln-us-A22-communications 1997 2007
# sh run_term_features.sh ln-us-A30-electrical-circuits 1998 2007

# 4/7/15
# sh run_term_features.sh ln-us-A21-computers 2002 2002 ta

# 6/6/15
# sh run_term_features.sh ln-us-14-health 2002 2002 tas

# 4/4/18 techwatch
# sh run_term_features.sh SignalProcessing 2002 2002 ta

# PARAMETERS TO SET BEFORE RUNNING SCRIPT:
# FUSE_CORPUS_ROOT="/home/j/corpuswork/fuse/FUSEData/corpora"
# LOCAL_CORPUS_ROOT="/home/j/anick/patent-classifier/ontology/creation/data/patents"
# LOCAL_CORPUS_ROOT="/home/j/anick/patent-classifier/ontology/roles/data/patents"
# These should be set in roles.config.sh

# 10/2/14 PGA removed the creation of the tf.f file, which is redundant with the .terms file information.

# get start time to compute elapsed time
START_TIME=$(date +%s)

# get path info
source ./roles_config.sh


CORPUS=$1
START_YEAR=$2
END_YEAR=$3
#SECTIONS should be ta (title, abstract) or tas (t, a, summary)
SECTIONS=$4

#ROOT="/home/j/corpuswork/fuse/FUSEData/corpora/$CORPUS"
TW_ROOT=$TW_CORPUS_ROOT/$CORPUS
#TARGET="/home/j/anick/patent-classifier/ontology/creation/data/patents/$CORPUS"
LOCAL_ROOT="$LOCAL_CORPUS_ROOT/$CORPUS"

#sh run_term_features.sh

# Peter's cs_2002_subset of 100 patents
#sh term_verb.sh /home/j/anick/patent-classifier/ontology/creation/data/patents/cs_2002_subset/config/files.txt /home/j/anick/patent-classifier/ontology/creation/data/patents/cs_2002_subset/data/d3_phr_feats/01/files /home/j/anick/patent-classifier/ontology/creation/data/patents/cs_2002_subset/data/m1_term_verb tas

# Marc cs 284k files from 1980 to 2007
#sh term_verb.sh /home/j/marc/Desktop/fuse/code/patent-classifier/ontology/creation/data/patents/201306-computer-science/config/files.txt /home/j/marc/Desktop/fuse/code/patent-classifier/ontology/creation/data/patents/201306-computer-science/data/d3_phr_feats/01/files /home/j/anick/patent-classifier/ontology/creation/data/patents/cs_284k/data/m1_term_verb tas

# This uses a larger set of cs files from BAE with application year in first column of files.txt file.  This will
# give more accurate time series information.
#sh term_verb.sh /home/j/corpuswork/fuse/FUSEData/corpora/ln-cs-500k/subcorpora/1995/config/files.txt /home/j/corpuswork/fuse/FUSEData/corpora/ln-cs-500k/subcorpora/1995/data/d3_phr_feats/01/files /home/j/anick/patent-classifier/ontology/creation/data/patents/cs_500k/data/m1_term_verb tas

# output in the form: <term> <verb> <count>
# influence       has     2

# setting this script up to loop over files from year 1995 - 2007.

#ROOT=/home/j/corpuswork/fuse/FUSEData/corpora/ln-us-all-600k
#TARGET=/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-all-600k

# Make sure target directory tree exists:
#bash-4.1$ mkdir ln-us-all-600k
#bash-4.1$ cd ln-us-all-600k
#bash-4.1$ mkdir data
#bash-4.1$ cd data
#bash-4.1$ mkdir term_features

# These variables out of date.  Corpus now passed in as parameter.
# web of science
#ROOT="/home/j/corpuswork/fuse/FUSEData/corpora/wos-cs-520k"                                                       
#TARGET="/home/j/anick/patent-classifier/ontology/creation/data/patents/wos-cs-520k"                             
# cs patents (1997 - 2007)
#ROOT="/home/j/corpuswork/fuse/FUSEData/corpora/ln-us-cs-500k"                                                       
#TARGET="/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-cs-500k"                             

# random us patent subset 600k
#ROOT="/home/j/corpuswork/fuse/FUSEData/corpora/ln-us-all-600k"
#TARGET="/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-all-600k"

# chinese general patents
#ROOT="/home/j/corpuswork/fuse/FUSEData/corpora/ln-cn-all-600k"
#TARGET="/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-cn-all-600k"

# chemistry
#ROOT="/home/j/corpuswork/fuse/FUSEData/corpora/ln-us-12-chemical"                                                       
#TARGET="/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-12-chemical"                             

# health
#ROOT="/home/j/corpuswork/fuse/FUSEData/corpora/ln-us-14-health"
#TARGET="/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-14-health"

# Make sure target directory tree exists before running this script

# 4/4/18 techwatch


echo "[run_term_features.sh]LOCAT_ROOT: $LOCAL_ROOT, LOCAL_CORPUS_ROOT: $LOCAL_CORPUS_ROOT" 

mkdir $LOCAL_ROOT
mkdir $LOCAL_ROOT/data
mkdir $LOCAL_ROOT/data/term_features
# 4/7/15 PGA added a dir for title-abstract only data
# If the sections parameter to this script is set to "ta", then only title/abstracts are 
# used and output is placed in term_features_ta subdirectory by term_features.sh
mkdir $LOCAL_ROOT/data/term_features_ta
mkdir $LOCAL_ROOT/data/tv
# create a directory for ACT specific files
mkdir $LOCAL_ROOT/data/act

# we use final "/" for the parameters to run_dir2features_count

TF_DIR=$LOCAL_ROOT/data/term_features/
TV_DIR=$LOCAL_ROOT/data/tv/

echo "[run_term_features.sh]Created local_root directory: $LOCAL_ROOT"

#exit 
# loop over the years for which we have data

YEAR=$START_YEAR
#YEAR=1998
#YEAR=2003
#while [ $YEAR -le 1998 ] ; do
# populate the local term_features directory for the range of years specified

#<<"COMMENT"
echo "[run_term_features.sh]Populating term_features directory for each year in range"
#exit

while [ $YEAR -le $END_YEAR ] ; do

    echo "year: $YEAR"

    #sh term_features.sh $FUSE_ROOT/subcorpora/$YEAR/config/files.txt $FUSE_ROOT/subcorpora/$YEAR/data/d3_phr_feats/01/files $LOCAL_ROOT/data/term_features $SECTIONS


    # TW path: /home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files/2002/000179
    # Local path: "/home/j/anick/tw/roles/data/corpora/SignalProcessing/data/term_features

    sh tw_features.sh $TW_ROOT/data/d3_feats/01/files/$YEAR $LOCAL_ROOT/data/term_features $YEAR $SECTIONS
    # sh run_tw_features.sh 


    YEAR=$[ $YEAR + 1 ]
done
#COMMENT

: <<"COMMENT"

#Below is now handled by tf.py file

# Now populate the tv files
echo "Elaspsed time: $(date -d @$(($(date +%s)-$START_TIME)) +"%M minutes %S seconds")"
echo "[run_term_features.sh]populating tv files in $TV_ROOT ($START_YEAR - $END_YEAR)"

python tf.py $TF_DIR $TV_DIR $START_YEAR $END_YEAR

echo "[run_term_features.sh]Finished."
echo "Elaspsed time: $(date -d @$(($(date +%s)-$START_TIME)) +"%M minutes %S seconds")"


# Finally, create tf.f files from the tf files
# This replaces the separate file make_tf_f.sh
echo "[run_term_features.sh]Creating tf.f files"
TF_QUAL="tf"
#TFF_QUAL="tf.f"

while [ $YEAR -le $END_YEAR ] ; do
    
    echo "year: $YEAR"
    TF_FILE=$TV_DIR$YEAR.$TF_QUAL
    #TFF_FILE=$TV_DIR$YEAR.$TFF_QUAL
    # clear the output file in case it already exists
    #> $TFF_FILE
    #GREP_RESULT=$(grep "last_word" $TF_FILE | cut -f1,3)
    #grep "last_word" $TF_FILE | cut -f1,3 >> $TFF_FILE
    
    YEAR=$[ $YEAR + 1 ]

    echo "[run_term_features.sh]Finished year."
    echo "Elaspsed time: $(date -d @$(($(date +%s)-$START_TIME)) +"%M minutes %S seconds")"

done
echo "[run_term_features.sh]Finished creating tf.f files"
echo "Elaspsed time: $(date -d @$(($(date +%s)-$START_TIME)) +"%M minutes %S seconds")"

COMMENT

