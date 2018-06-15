# roles_config.sh
# contains paths for use by .sh routines

# modified 4/4/18 for techwatch roles use

#FUSE_CORPUS_ROOT="/home/j/corpuswork/fuse/FUSEData/corpora"
TW_CORPUS_ROOT="/home/j/corpuswork/techwatch/corpora"
#LOCAL_CORPUS_ROOT="/home/j/anick/patent-classifier/ontology/creation/data/patents"
#LOCAL_CORPUS_ROOT="/home/j/anick/patent-classifier/ontology/roles/data/patents"
LOCAL_CORPUS_ROOT="/home/j/anick/tw/roles/data/corpora"

# for techwatch, moved code_dir definition here from term_features.sh
CODEDIR="/home/j/anick/tw/roles/code"

echo "[roles_config.sh]TW_CORPUS_ROOT: $TW_CORPUS_ROOT, LOCAL_CORPUS_ROOT: $LOCAL_CORPUS_ROOT"

# for Techwatch testing, assume mallet is here:
# Note that this version has been modified to fix a mallet bug 
# (see /home/j/anick/tw/tools/mallet-2.0.7/mallet_changes.txt)
MALLET_DIR="/home/j/anick/tw/tools/mallet-2.0.7/bin"
