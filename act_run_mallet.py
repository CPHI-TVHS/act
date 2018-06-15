# generalized from pa_runs.py
# This file is designed to keep a record of mallet runs
#

import sys
import pdb
import act_pnames
import run_mallet
import vectors_helpers

# 4/25/18
# pa_runs.run_sig("NB", "woc", "9999", False)
def run_sig(classifier_type, context_type, year, feat_info=False):
    print "[act_run_mallet.py]starting run_sig"
    corpus_tv = "/home/j/anick/tw/roles/data/corpora/SignalProcessing/data/tv/" 
    num_infogain_features = 50

    #tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all"
    tf_path = corpus_tv + year + ".tf"

    #tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.cand_bigrams.bigram.mtf.i.0.8.2.tcs"
    #tcs_path = ".".join(["/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/dja", gram_type, context_type] )
    tcs_path = corpus_tv + year + ".act.tcs"

    feature_file_path = None
    #output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    output_dir = corpus_tv


    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = ".".join(["SignalProcessing", context_type, year] )
    # NOTE: the classifier type (NB, ME) has to be the first thing in the file name, since
    # that is how the info is passed on to mallet.
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)


def run_mallet_classifier(corpus_root, corpus, sections, classifier_type, context_type, year, num_infogain_features=50, feat_info=False):
    """
    sections: ta (text and abstract only), or tas (include summary as well)
    classifier_type: NB or ME (mallet classifier to use)
    context_type:  woc (without context)
    year: actual year or fictional number that looks like a year (e.g. 9999)
    feat_info: outputs another info file if True.
    num_infogain_features: how many features to use (sorted by infogain score)
    """
    print "[act_run_mallet.py]Starting run_mallet_classifier"
  
    sections_path = act_pnames.sections_root(corpus_root, corpus, sections)
    tf_path = sections_path + "/" + year + ".tf"
    tcs_path = sections_path + "/" + year + ".act.tcs"

    feature_file_path = None
    output_dir = sections_path
    output_file_scheme = ".".join([corpus, context_type, year] )
    # NOTE: the classifier type (NB, ME) has to be the first thing in the file name, since
    # that is how the info is passed on to mallet.
    output_file_prefix = classifier_type + ".IG" + str(num_infogain_features) + "." + output_file_scheme

    print("[act_run_mallet.py]tf_path:%s, tcs_path:%s, output_dir:%s, output_file_prefix:%s" % (tf_path, tcs_path, output_dir, output_file_prefix))


    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)

    
# python2.7 act_run_mallet.py /home/j/anick/tw/roles/data/corpora sp ta NB woc 9999 1
if __name__ == "__main__":
    args = sys.argv
    corpus_root = args[1]
    corpus = args[2]
    sections = args[3]
    classifier_type = args[4]
    context_type = args[5]
    year = args[6]
    feat_info = args[4]
    if feat_info == "0":
        feat_info_p = False
    else:
        feat_info_p = True
    
    run_mallet_classifier(corpus_root, corpus, sections, classifier_type, context_type, year, feat_info=feat_info_p)
    
