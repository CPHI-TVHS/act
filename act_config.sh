# act_config.sh

# These variables should match the values set in roles_config.py
TW_CORPUS_ROOT="/home/j/corpuswork/techwatch/corpora"
LOCAL_CORPUS_ROOT="/home/j/anick/tw/roles/data/corpora"
CODEDIR="/home/j/anick/tw/roles/code"

echo "[act_config.sh]TW_CORPUS_ROOT: $TW_CORPUS_ROOT, LOCAL_CORPUS_ROOT: $LOCAL_CORPUS_ROOT"

# Provide a location fot the mallet binary used for classification.
# Note that this version has been modified to fix a mallet bug in v2.0.7 
# so that svm  formatted data will be handled properly.
# (see /home/j/anick/tw/tools/mallet-2.0.7/mallet_changes.txt)
#MALLET_DIR="/home/j/anick/tw/tools/mallet-2.0.7/bin"

# scripts will invoke python v2.7 using the alias python2.7.  Set this alias to
# your local python 2.7 executable
alias python2.7='/usr/local/bin/python2.7'

# scripts utilize this pipe sequence to output count of unique lines in a file,
# sorted by count, and formatted as <count>\t<line>
alias sunr="sort | uniq -c | sort -nr | sed -e 's/^ *\([0-9]*\) /\1	/'" 
