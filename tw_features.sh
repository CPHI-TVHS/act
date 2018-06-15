#tw_features.sh

# Create a local directory of d3_feats info organized by year



# based on fuse script:
# term_features.sh
# Given the phr_feats files on FUSE net, create a file for each patent containing
# term feature-value count
# for features of interest: head, prev_V, prev_Npr, prev_Jpr, prev_J

# get code path info
source ./roles_config.sh


#TW_YEARS_ROOT="$TW_CORPUS_ROOT/$CORPUS/data/d3_feats/01/files"
# e.g. /home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files/
# subdir: 2002/000179
#LOCAL_YEARS_ROOT="$LOCAL_CORPUS_ROOT/$CORPUS"
# e.g. /home/j/anick/tw/roles/data/corpora/SignalProcessing



INROOT=$1
# $TW_ROOT/data/d3_feats/01/files/2002
OUTROOT=$2
# LOCAL_ROOT/data/term_features
YEAR=$3
# SECTIONS should be ta (title abstract) or tas (title abstract summary)
SECTIONS=$4

# for title and abstract data only, we output to term_features_ta directory
# Otherwise we write to term_features directory
if [ $SECTIONS == "ta" ]
    then 
    OUTROOT+=_ta
fi

echo [term_features.sh]Writing to outroot: $OUTROOT
#exit

# 4/4/18 moved code_dir defintion into roles.config
#CODEDIR="/home/j/anick/patent-classifier/ontology/creation"

file_no=0
# read three tab separated fields from the FILELIST file
#while read YEAR SOURCE YEAR_FILE; do
    #echo "input: $YEAR, $YEAR_FILE"

# The input dir has extra level of subdirectory between year and actual data file
# for p in */*; do echo $p; done
for p in $INROOT/*/*; do
    input_file_path=$p
    # remove .gz from the output file name
    output_file_path=${p%.gz}

    
    file_no=`expr $file_no + 1`
    # remove intermediate path from output_file_path
    outfile=$(basename $output_file_path)
    outdir=$OUTROOT/$YEAR
    # make sure outdir exists before using it
    mkdir -p $outdir
    # output file fully specified
    outpath=$outdir/$outfile

    # if output file already exists, do not overwrite
    if [ -f $outpath ];
    then
	#echo "File $outpath exists.  NOT overwriting!"
	# no op
	:
    else
	#echo "Creating $outpath."

    # assume input file is compressed
    infile=$input_file_path

    #echo "output: $outfile, $outpath, $infile"
    #echo "file $file_no: $outpath"

    if [ $SECTIONS == "ta" ]
	then 
	#echo "running: gunzip -c  $infile |  egrep 'ABSTRACT|TITLE' | cut -f3 | sort | uniq -c | sort -nr | python $CODEDIR/filter_uc2.py 1 > $outpath   "
	gunzip -c  $infile |  egrep 'ABSTRACT|TITLE' | python $CODEDIR/term_features.py | sort | uniq -c | sort -nr | python $CODEDIR/reformat_uc2.py > $outpath

    elif [ $SECTIONS == "tas" ]
	then
	gunzip -c  $infile |  egrep 'ABSTRACT|TITLE|SUMMARY' | python $CODEDIR/term_features.py | sort | uniq -c | sort -nr | python $CODEDIR/reformat_uc2.py > $outpath

    else
	echo "missing SECTIONS parameter (ta or tas)"
	
    # end loop for section option
    fi

    # end the loop for each individual file
    fi

#done < $FILELIST
done
