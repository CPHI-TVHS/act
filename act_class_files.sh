# From NB.IG50.sp3.woc.9999.results.classes
# produce files for each class, normalizing 's and \/ and removing _

# import variable names and aliases
source ./act_config.sh

SOURCE_SUBDIR=$1
CORPUS_NAME=$2
SECTIONS=$3
MALLET_METHOD=$4
CONTEXT=$5
START_YEAR=$6

# We will default the infogain feature number to 50, although
# we may parameterize this in the future
IG_NUM=50

TARGET_DIR=$LOCAL_CORPUS_ROOT/$CORPUS_NAME/$SECTIONS

# e.g. NB.IG50.sp3.woc.9999.results.classes
CLASSES_FILE=$TARGET_DIR/$MALLET_METHOD.IG$IG_NUM.$CORPUS_NAME.$CONTEXT.$START_YEAR.results.classes

echo "[run_act.sh]Running act_class_files.sh"

cat $CLASSES_FILE | cut -f1,2 | grep 'c$' | cut -f1 | sort | sed -e "s/_'s/'s/g" | sed -e "s/_'/'/g" | sed -e "s/_/ /g" | sed -e "s/\\\//g" > $CLASSES_FILE.c

cat $CLASSES_FILE | cut -f1,2 | grep 't$' | cut -f1 | sort | sed -e "s/_'s/'s/g" | sed -e "s/_'/'/g" | sed -e "s/_/ /g" | sed -e "s/\\\//g" > $CLASSES_FILE.t

cat $CLASSES_FILE | cut -f1,2 | grep 'a$' | cut -f1 | sort | sed -e "s/_'s/'s/g" | sed -e "s/_'/'/g" | sed -e "s/_/ /g" | sed -e "s/\\\//g" > $CLASSES_FILE.a

echo "[run_act.sh]Completed act_class_files.sh"

