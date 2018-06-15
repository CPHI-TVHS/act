min_len=2
max_len=6
#indir=/home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files/2002/
indir=/home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files

base_outfile=ngrams


# outdir must exist!
#outdir=/home/j/anick/tw/roles/data/corpora/SignalProcessing/data/nc/2002
outdir=/home/j/anick/tw/roles/data/corpora/SignalProcessing/data/nc/9999
outfile=$outdir/$base_outfile
logfile=$outfile.log

###omitted if already created
echo "[ngram_extract.sh] Creating file: ngrams"
###python2.7 ngram_extract.py $indir $outfile $min_len $max_len > $logfile
  
# create subset files (bigrams.inst.filt and trigrams.inst.filt)
bi_outfile=$outdir/bigrams.inst.filt
tri_outfile=$outdir/trigrams.inst.filt



# output separate bigram and trigram files with canonical form, doc_id, pos_sig 
###cat $outfile | egrep '^2	' | cut -f2,4,5 > $bi_outfile
###cat $outfile | egrep '^3	' | cut -f2,4,5 > $tri_outfile

echo "[ngram_extract.sh]Calling nc_bracket.py"
python2.7 nc_bracket.py $outdir

echo "[ngram_extract.sh]Completed nc_bracket.py"
