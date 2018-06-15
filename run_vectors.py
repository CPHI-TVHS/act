# This file is designed to keep a record of mallet runs

#import run_mallet
import vectors_helpers
import pdb
import roles_config

"""
# pa_runs.run_health_2002_inst_all()
def run_health_2002_inst_all():
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/tv/2002.cand_bigrams.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/tv/inst_all/2002.cand_bigrams.mtf.m.0.8.2.tcs"
    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_2002.inst_all.ssi.0.8.2.bi" 
    output_file_prefix = "NB.IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features)

# pa_runs.run_bio_abs_inst_all("ME")
# pa_runs.run_bio_abs_inst_all_bi("NB")
def run_bio_abs_inst_all_bi(classifier_type):
    # bigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A27-molecular-biology/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A27-molecular-biology/data/tv/inst_all/i_bio_abs.cand_bigrams.bigram.mtf.i.0.8.2.tcs"
    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A27-molecular-biology/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "bio_abs.inst_all.ssi.0.8.2.bi" 
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features)


# pa_runs.run_bio_abs_inst_all_uni("ME")
# pa_runs.run_bio_abs_inst_all_uni("NB")
def run_bio_abs_inst_all_uni(classifier_type):
    # unigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A27-molecular-biology/data/tv/i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A27-molecular-biology/data/tv/inst_all/i_bio_abs.attrs.k2.f10.unigram.mtf.i.0.8.2.tcs"
    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A27-molecular-biology/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "bio_abs.inst_all.ssi.0.8.2.uni" 
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features)

########################## health_bio_abs ###################
# pa_runs.run_health_bio_abs_inst_all_uni("ME")
# pa_runs.run_health_bio_abs_inst_all_uni("NB", feat_info=True)
def run_health_bio_abs_inst_all_uni(classifier_type, feat_info=False):
    # unigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.attrs.k2.f10.unigram.mtf.i.0.8.2.tcs"
    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssi.0.8.2.uni" 
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info )


# pa_runs.run_health_bio_abs_inst_all("ME")
# pa_runs.run_health_bio_abs_inst_all_bi("NB", feat_info=True)
def run_health_bio_abs_inst_all_bi(classifier_type, feat_info=False):
    # bigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.cand_bigrams.bigram.mtf.i.0.8.2.tcs"
    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssi.0.8.2.bi" 
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)

# use minimal seedset
# pa_runs.run_health_bio_abs_inst_all_bi_min("NB")
def run_health_bio_abs_inst_all_bi_min(classifier_type, feat_info=False):
    # bigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.cand_bigrams.bigram.mtf.m.0.8.2.tcs"
    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssm.0.8.2.bi" 
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)


# use feng seedset
# pa_runs.run_health_bio_abs_inst_all_bi_feng("NB")
def run_health_bio_abs_inst_all_bi_feng(classifier_type, feat_info=False):
    # bigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.cand_bigrams.bigram.mtf.f.0.8.2.tcs"
    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssf.0.8.2.bi" 
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)

# use feng seedset
# pa_runs.run_health_bio_abs_inst_all_uni_feng("NB")
def run_health_bio_abs_inst_all_uni_feng(classifier_type, feat_info=False):
    # unigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.attrs.k2.f10.unigram.mtf.f.0.8.2.tcs"

    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssf.0.8.2.uni" 
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)

#### seedset increase (u)

# pa_runs.run_health_bio_abs_inst_all_uni_increase("NB", 50)
def run_health_bio_abs_inst_all_uni_increase(classifier_type, num_infogain_features=50, feat_info=False):
    # unigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.attrs.k2.f10.unigram.mtf.u.0.8.2.tcs"

    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    #num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssu.0.8.2.uni" 
    output_file_prefix = classifier_type + ".IG" + str(num_infogain_features) + "." +  output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)

# pa_runs.run_health_bio_abs_inst_all_bi_increase("NB", 50)
def run_health_bio_abs_inst_all_bi_increase(classifier_type, num_infogain_features=50, feat_info=False):
    # bigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.cand_bigrams.bigram.mtf.u.0.8.2.tcs"

    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    #num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssu.0.8.2.bi" 
    output_file_prefix = classifier_type + ".IG" + str(num_infogain_features) + "." + output_file_scheme

    print "num_infogain_features: %i" % (num_infogain_features)
    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)

##### seedset promote (p)
# pa_runs.run_health_bio_abs_inst_all_uni_promote("NB", 25)
def run_health_bio_abs_inst_all_uni_promote(classifier_type, num_infogain_features=50, feat_info=False):
    # unigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.attrs.k2.f10.unigram.mtf.p.0.8.2.tcs"

    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    #num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssp.0.8.2.uni" 
    output_file_prefix = classifier_type + ".IG" + str(num_infogain_features) + "." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)

# pa_runs.run_health_bio_abs_inst_all_bi_promote("NB", 25)
def run_health_bio_abs_inst_all_bi_promote(classifier_type, num_infogain_features=50, feat_info=False):
    # bigrams
    tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all"
    tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.cand_bigrams.bigram.mtf.p.0.8.2.tcs"

    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    #num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = "health_bio_abs.inst_all.ssp.0.8.2.bi" 
    output_file_prefix = classifier_type + ".IG" + str(num_infogain_features) + "." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)




### gold
# pa_runs.run_health_bio_abs_inst_all("ME")
# pa_runs.run_health_bio_abs_inst_all_gold("NB", "bi", "woc")
def run_health_bio_abs_inst_all_gold(classifier_type, gram_type, context_type, feat_info=False):
    # bigrams
    if gram_type == "bi":
        tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all"
    elif gram_type == "uni":
        tf_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all"
    #tcs_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/i_bio_abs.cand_bigrams.bigram.mtf.i.0.8.2.tcs"
    tcs_path = ".".join(["/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/inst_all/dja", gram_type, context_type] )
    feature_file_path = None
    output_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/eval/mallet/"
    num_infogain_features = 50
    # output file prefix should contain: ML_type (NB, ME), feature_source (PR, IG)+Number, seedset_identifier (ssi), 
    # index_source (health_2002), sections (inst_all, inst_abs), pn ratio (0.8), min_freq (5), gram_type (uni, bi)
    # eg. NB.IG50.ssi.health_2002.inst_all.bi
    output_file_scheme = ".".join(["health_bio_abs.inst_all.dja", gram_type, context_type] )
    output_file_prefix = classifier_type + ".IG50." + output_file_scheme

    run_mallet.run_classify(tf_path, tcs_path, output_dir, output_file_prefix, feature_file_path=feature_file_path, num_infogain_features=num_infogain_features, feat_info=feat_info)


"""
###############################
# 10/5/15 

# create svm_format files                                                                                                                   
# run_vectors.run_tf2svm("computers_abs", "i_computers_abs.attrs.k2.f10.unigram.mtf.inst_all")                                              
# run_vectors.run_tf2svm("computers_abs", "i_computers_abs.cand_bigrams.bigram.mtf.inst_all")

# run_vectors.run_tf2svm("health_bio_abs", "i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all")  
# run_vectors.run_tf2svm("health_bio_abs", "i_bio_abs.cand_bigrams.bigram.mtf.inst_all")      
# run_vectors.run_tf2svm("health_bio_abs", "i_bio_abs.cand_bigrams.bigram.mtf.inst_all")

# 4/25/18
# run_vectors.run_tf2svm("SignalProcessing", "2013.tf")  
      
corpus_root = roles_config.CORPUS_ROOT

def run_tf2svm(corpus, tf_filename ):

    #dir_path = "/home/j/anick/patent-classifier/ontology/roles/data/patents/" + corpus + "/data/tv/" 
    dir_path = corpus_root + "/" + corpus + "/data/tv/" 
    tf_file = dir_path + tf_filename
    file_name_prefix = tf_filename
    output_path = tf_file + ".svm_format"
    vectors_helpers.tf2svm_format(tf_file, dir_path, file_name_prefix)
    print("Writing to %s" % output_path)

# pa_runs.run_tcs2infogain_scores("i_computers_abs.cand_bigrams.bigram.mtf.i.0.8.2.tcs", "computers_abs", "i_computers_abs.cand_bigrams.bigram.mtf.inst_all")
# pa_runs.run_tcs2infogain_scores("i_computers_abs.attrs.k2.f10.unigram.mtf.i.0.5.5.tcs", "computers_abs", "i_computers_abs.attrs.k2.f10.unigram.mtf.inst_all")

# run_vectors.run_tcs2infogain_scores("dja.uni.tcs", "health_bio_abs", "i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all")
# run_vectors.run_tcs2infogain_scores("dja.bi.tcs", "health_bio_abs", "i_bio_abs.cand_bigrams.bigram.mtf.inst_all")

# 4/25/18 run_vectors.run_tcs2infogain_scores("2013.act.tcs", "SignalProcessing", "2013.tf")
# 6/11/18 run_vectors.run_tcs2infogain_scores("9999.act.tcs", "sp", "9999.tf")
def run_tcs2infogain_scores(tcs_filename, corpus, tf_file_name_prefix):
    #tcs_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/" + corpus + "/data/tv/inst_all/" 
    #tf_dir = "/home/j/anick/patent-classifier/ontology/roles/data/patents/" + corpus + "/data/tv/" 

    tcs_dir = corpus_root + "/" + corpus + "/ta/" 
    tf_dir = corpus_root + "/" + corpus + "/ta/" 


    #tcs_file = tcs_dir + tcs_filename
    #pdb.set_trace()
    vectors_helpers.tcs2infogain_scores(tcs_dir, tcs_filename, tf_dir, tf_file_name_prefix)

def run_abs_tcs_ft2infogain_scores(mtf_file_type, index, corpus, spec):
    file_prefix = ".".join([index, mtf_file_type, "mtf", spec])
    tcs_file = ".".join([file_prefix, "tcs"])
    tf_file = ".".join([index, mtf_file_type, "mtf.inst_all"])
    run_tcs2infogain_scores(tcs_file, corpus, tf_file)

# obsolete
def run_abs_tcs2infogain_scores(ngram, index, corpus, spec):
    if ngram == "bigram":
        file_prefix = index + ".cand_bigrams.bigram.mtf." + spec
    elif ngram == "unigram":
        file_prefix = index + ".attrs.k2.f10.unigram.mtf." + spec
    tcs_file = file_prefix + ".tcs"

    run_tcs2infogain_scores(tcs_file, corpus, tf_file)

#obsolete
# run_vectors.run_abs_tcs2infogain_scores_ngrams("i_computers_abs", "computers_abs", "i.0.9.5")
# run_vectors.run_abs_tcs2infogain_scores_ngrams("i_bio_abs", "health_bio_abs", "p.0.9.5")
# run_vectors.run_abs_tcs2infogain_scores_ngrams("i_bio_abs", "health_bio_abs", "u.0.9.5")
# spec is a string of the form <seedset id>.0<harmonic_mean threshold>.<polar freq threshold>

# run_vectors.run_abs_tcs2infogain_scores_ngrams("i_bio_abs", "health_bio_abs", "ue10.0.9.5")
def run_abs_tcs2infogain_scores_ngrams(index, corpus, spec):
    # tf_file is the prefix for the mtf file which an svm_format file was derived in run_tf2svm
    # The .svm_format file must already exist before running this function.
    tf_file = index + ".attrs.k2.f10.unigram.mtf.inst_all"
    run_abs_tcs2infogain_scores("unigram", index, corpus, spec, tf_file)

    tf_file = index + ".cand_bigrams.bigram.mtf.inst_all"
    run_abs_tcs2infogain_scores("bigram", index, corpus, spec, tf_file)
