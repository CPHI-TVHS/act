# functions for creating mallet compatible feature vector files
# moved from /home/j/llc/gititkeh/mallet-2.0.7/bin/ on 10/7/15 PGA

import os
import pdb
import mallet_config

# location of version of mallet modified by Gitit to use infogain-based feature subsets
#MALLET = "/home/j/llc/gititkeh/mallet-2.0.7/bin/./mallet"
MALLET = mallet_config.MALLET_DIR + "/mallet"
#MALLET = "./mallet"
#VECTORS2INFO = "/home/j/llc/gititkeh/mallet-2.0.7/bin/./vectors2info"
VECTORS2INFO = mallet_config.MALLET_DIR + "/vectors2info"
#VECTORS2INFO = "./vectors2info"

def tf2svm_format(tf_file, dir_path, file_name_prefix):
    with open(tf_file,'r') as tf:
        tf_lines = tf.readlines()
    tfDict = {}

    #Accumulate features and counts from tf
    for line in tf_lines:
        fields = line.split('\t')
        # replace spaces with "_" in terms since mallet parser uses spaces as separators
        term = '_'.join(fields[0].split())
        feature = fields[1].strip()
        count = fields[2].strip()
        #Skip bad features that cause bugs in Mallet
        if ':' in feature or '#' in feature or '<' in feature or '>' in feature:
            continue
        #Add feature:count to the term's list in tfDict
        if term in tfDict:
            tfDict[term].append(feature+":"+count)
        else:
            tfDict[term] = [feature+":"+count]

    svm_file = open(dir_path+file_name_prefix+".svm_format", 'w')
    for term in tfDict:
        svm_file.write(term+'\t')
        for f_v in tfDict[term]:
            svm_file.write(f_v+' ')
        svm_file.write('\n')
    svm_file.close()
        
# ///
#def tcs2infogain_scores(tcs_dir, tcs_file, dir_path, file_name_prefix):
def tcs2infogain_scores(tcs_dir, tcs_file, tf_dir, tf_file):
    tcs_path = tcs_dir + tcs_file
    tf_path = tf_dir + tf_file
    svm_format_path = tf_path + ".svm_format"
    train_path = tcs_path + ".train_input_svm"
    term_train_path = tcs_path + ".term_train_input_svm"
    train_vector_path = tcs_path + ".train.vectors"
    feature_path = tf_path + ".features"
    infogain_path = tcs_path + ".infogain_features"

    print "[tcs2infogain_scores] tcs_path: %s" % tcs_path
    print  "[tcs2infogain_scores] tf_path: %s" % tf_path
    print "[tcs2infogain_scores] svm_format_path: %s" % (svm_format_path)
    print "[tcs2infogain_scores] infogain_path: %s" % (infogain_path)
    print "[tcs2infogain_scores] feature_path: %s" % (feature_path)

    #pdb.set_trace()
    #with open(dir_path+file_name_prefix+".svm_format",'r') as svm:
    with open(svm_format_path, 'r') as svm:
        svm_lines = svm.readlines()
        
    tfDict = {}
    for line in svm_lines:
        line = line.strip()
        fields = line.split('\t')
        term = fields[0]
        fv_list = fields[1]
        tfDict[term] = fv_list
        
    with open(tcs_path,'r') as tcs:
        tcs_lines = tcs.readlines()


    tcsDict = {}

    for line in tcs_lines:
        line = line.strip()
        fields = line.split('\t')
        # replace spaces with "_" in terms
        term = '_'.join(fields[0].split())
        #pdb.set_trace()
        if term in tfDict:
            tcsDict[term] = [fields[1], tfDict[term]]
            
    #pdb.set_trace()
    #train_file = open(dir_path+file_name_prefix + ".train_input_svm", 'w')
    s_train_file = open(train_path, 'w')
    s_term_train_file = open(term_train_path, 'w')
    for term in tcsDict:
        s_train_file.write(tcsDict[term][0]+'\t'+tcsDict[term][1]+'\n')
        s_term_train_file.write(term+'\t'+tcsDict[term][0]+'\t'+tcsDict[term][1]+'\n')
    s_train_file.close()
    s_term_train_file.close()
    #import_svmlight_call = os.system(MALLET + " import-svmlight --input "+dir_path+file_name_prefix+\
    #                                 ".train_input_svm --output "+dir_path+file_name_prefix+".train.vectors")

    import_svmlight_call = os.system(MALLET + " import-svmlight --input " + train_path + " --output " + train_vector_path)

    if import_svmlight_call != 0:
        print "Could not create vectors file in directory."
        exit()
    vec2info_call1 = os.system(VECTORS2INFO + " --input " + train_vector_path + " --print-features > " + feature_path)
    #print infogain must get a number as input
    if vec2info_call1 != 0:
        print "Could not print feature list for vectors file."
        exit()
    
    with open(feature_path) as feat_list:
        lines = [line for line in feat_list.readlines() if line != '\n']
        num_features = len(lines)
    vec2info_call2 = os.system(VECTORS2INFO + " --input " + train_vector_path + " --print-infogain "+str(num_features)+" > "+ infogain_path)
    if vec2info_call2 != 0:
        print "Could not print infogain list for vectors file."
        exit()
    
"""def test1():
    tf1 = '/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.cand_bigrams.bigram.mtf.inst_all'
    tf2 = '/home/j/anick/patent-classifier/ontology/roles/data/patents/health_bio_abs/data/tv/i_bio_abs.attrs.k2.f10.unigram.mtf.inst_all'

    tf2svm_format(tf1, '/home/j/llc/gititkeh/malletex/new_mallet/', 'tf1')
    tf2svm_format(tf2, '/home/j/llc/gititkeh/malletex/new_mallet/', 'tf2')
def test2():
    tcs = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/tv/doc_all/2002.a.tf.f1.unigram.mtf.ssi.1.0.2.tcs"

    tcs2infogain_scores(tcs, '/home/j/llc/gititkeh/malletex/new_mallet/', 'tf2')
"""
#test1()
#test2()
    


