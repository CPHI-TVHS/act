# run_tf.sh
# convenience script to run tf.py
# sh run_tf.sh
# NOTE: Use run_act_tf.sh to invoke act_tf.py


CORPUS=SignalProcessing


corpus_root=/home/j/anick/tw/roles/data/corpora

#python2.7 tf.py $corpus_root/$CORPUS/data/term_features_ta/ $corpus_root/$CORPUS/data/tv/ 2002 2002
python2.7 tf.py $corpus_root/$CORPUS/data/term_features_ta/ $corpus_root/$CORPUS/data/tv/ 2003 2016


