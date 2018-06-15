# encoding=utf8  

"""
# act_tf.py
# modified from tf.py to take a list of .xml.gz files as input
# create .tf file from term_features directory files

# These functions were originally part of role.py but separated out to separate
# generic feature processing from the ACT/PN task.

# NOTE: We assume we are running on UNIX, where directories are separated by "/"

#----
# from individual term features files, create a summary file per year
# with the freq of the term feature combination  (.tf)
# NOTE: alpha filter does not apply to Chinese.  Removed for now.

# 2/27/14 PGA added code to count terms and feats and write out their counts 
# in separate files (.terms, .feats)

# inroot and outroot should terminate in a directory separator ("/")

# 4/4/15 added canonicalization and prob(term|feature) to .tf
# 4/18/15 added MI to .tf

 .tf file sample
program prev_VNP=performs|debugging|on  1       0.000022        0.000142
pre-paid card   prev_Npr=amount_of

Need to canonicalize term and feature separately
Remember that features in the seed set have to be consistent (e.g. canonicalized or not) with features here
for probabilities to be consistent.  For now, we will only canonicalize the terms (not the features)

The porter stemmer in nltk (called by canon) may generate unicode errors.  These can be ignored.  When this 
occurs, we don't apply stemming to the feature.

"""

import pdb
#import sys
#import collections
from collections import defaultdict
import os
import glob
import codecs
import roles_config
import canon
import math
import gzopen

# Next three lines are a hack from 
# https://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte
# to avoid the error: UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

# list of noise terms to omit from doc_terms_file
# The word "end" is a marker inserted in documents by our preprocessing.
# "claim" is a noise word in patents.
DOC_TERMS_NOISE = ["end", "fig", "figure", "claim"]

# canonicalizer object
can = canon.Canon()

#def dir2features_count(inroot, outroot, year, overwrite_p=False, canonicalize_p=True, filter_noise_p=True):
def dir2features_count(filelist_file, out_root, sections, year, overwrite_p,  max_doc_terms_count=1000, canonicalize_p=True, filter_noise_p=True):
    #pdb.set_trace()
    out_path = "/".join([out_root, sections])
    out_path_prefix = "/".join([out_path, year])
    # term-feature output file
    tf_file = out_path_prefix + ".tf"
    # remember the mapping between surface head nouns and their canonicalized forms
    canon_file = out_path_prefix + ".canon" 

    # create the outpath if it doesn't exist yet
    print("[act_tf.py]creating path: %s,\n[act_tf.py]writing to %s" % (out_path, tf_file))

    try:
        # create directory path for corpus, if it does not aleady exist
        os.makedirs(out_path)
    except:
        print("[act_tf.py]NOTE: Path already exists (or cannot be created).")

    # Do not continue if the .tf file already exists for this corpus and year
    if os.path.isfile(tf_file) and not overwrite_p:
        print "[tf.py]file already exists: %s.  No need to recompute." % tf_file 
    else:

        terms_file = out_path_prefix + ".terms"
        feats_file = out_path_prefix + ".feats"
        corpus_size_file = out_path_prefix + ".cs"
        doc_terms_file = out_path_prefix + ".doc_terms"
        # store each filename with a list of its terms
        s_doc_terms_file = codecs.open(doc_terms_file, "w", encoding='utf-8')

        # count of number of docs a term pair cooccurs in
        # dfreq is document freq, cfreq is corpus freq
        #d_pair_freq = defaultdict(int)
        d_pair2dfreq = defaultdict(int)
        # corpus count for the pair
        d_pair2cfreq = defaultdict(int)
        # count of number of docs a term occurs in
        #d_term_freq = defaultdict(int)
        d_term2dfreq = defaultdict(int)
        # count of number of instances of a term
        #d_term_instance_freq = defaultdict(int)
        d_term2cfreq = defaultdict(int)
        # count of number of instances of a feature
        #d_feat_instance_freq = defaultdict(int)
        d_feat2cfreq = defaultdict(int)
        # count of number of docs a feature occurs in
        #d_feat_freq = defaultdict(int)
        d_feat2dfreq = defaultdict(int)

        # doc_count needed for computing probs
        doc_count = 0

        # open list of all the files in the inroot directory
        s_filelist = open(filelist_file)

        #print "inroot: %s, filelist: %s" % (inroot, filelist)

        # iterate through files in filelist
        for infile in s_filelist:
            infile = infile.strip("\n")

            # Create a tab separated string containing the filename and all (legal) canonicalized terms, including
            # duplicates.  This will be used to populate a doc_term retrieval system in 
            # elasticsearch.
            # First field will be the filename.
            # At this point, we'll collect the filename and terms into a list.
            # The file without path or extensions should be a unique doc id.
            doc_id = os.path.basename(infile).split(".")[0]
            doc_terms_list = [doc_id]

            # dictionaries to sum up statistics
            # number of times a term appears in the doc
            d_term2count = defaultdict(int)
            d_feat2count = defaultdict(int)            
            # number of times a term appears with a specific feature in the doc
            d_pair2count = defaultdict(int)

            # process the dictionaries
            # for each file, create a set of all term-feature pairs in the file
            #/// dictionaries are functionally redundant with sets here.
            # Use sets to capture which terms, features, and pairs occur in the 
            # document.  We'll use this after processing each doc to update the
            # doc frequencies of terms, features, and pairs.
            pair_set = set()
            term_set = set()
            feature_set = set()
            #pdb.set_trace()

            s_infile = gzopen.gzopen(infile)
            # count number of lines in file
            i = 0

            # iterate through lines in d3_feats file
            for term_line in s_infile:
                i += 1
                term_line = term_line.strip("\n")
                l_fields = term_line.split("\t")
                
                term = l_fields[2]

                # Do not process noise (illegal) terms or features
                #  for cases where feat = "", need to filter!  todo
                #pdb.set_trace()
                if (filter_noise_p and canon.illegal_phrase_p(term)):
                    pass

                # NOTE: At the moment we don't test which sections of the doc should be included
                # as specified by the sections parameter (ta or tas).  We include every line.  If
                # we decide to add this functionality, this would be the place to add the filter.

                else:

                    if canonicalize_p:
                        # Do canonicalization of term before incrementing counts
                        #feature = can.get_canon_feature(feature)
                        term = can.get_canon_np(term)

                    # increment the within doc count for the term
                    ##d_term2count[term] += 1
                    term_set.add(term)
                    # increment the global corpus count for the term
                    d_term2cfreq[term] += 1


                    # Add the term to the list of terms for the current doc
                    # Ideally, we would like to ignore parts of a patent (e.g. the claims) and
                    # just use the title, abstract and summary.  However, there is no feature 
                    # indicating what section we are in beyond the abstract.  So instead, we
                    # will use a simple doc_terms_count cut off (e.g. 1000). Variable i counts 
                    # the number of lines so far.
                                
                    #pdb.set_trace()
                    if (i <= max_doc_terms_count) and (term not in DOC_TERMS_NOISE):
                        doc_terms_list.append(term)

                    # fields 3 and beyond are feature-value pairs
                    # look for features of interest using their prefixes
                    for feature in l_fields[3:]:
                        # Note that we use the prefixes of some feature names for convenience.
                        # The actual features are prev_V, prev_VNP, prev_J, prev_Jpr, prev_Npr, last_word
                        # first_word, if an adjective, may capture some indicators of dimensions (high, low), although
                        # many common adjectives are excluded from the chunk and would be matched by prev_J.
                        # we also pull out the sent and token locations to allow us to locate the full sentence for this
                        # term-feature instance.
                        if (feature[0:6] in ["prev_V", "prev_J", "prev_N", "last_w"]) and not canon.illegal_feature_p(feature):

                            if canonicalize_p:
                                # Do canonicalization of feature before incrementing counts
                                feature = can.get_canon_feature(feature)


                            # increment global corpus count for the feature
                            d_feat2cfreq[feature] += 1

                            feature_set.add(feature)
                            # increment global corpus count for the pair
                            d_pair2cfreq[(term, feature)] += 1
                            # increment the within doc count for the term feature pair
                            ##d_pair2count[(term, feature)] += 1
                            pair_set.add((term, feature))

            # construct a tab-separated string containing file_name and all terms
            doc_terms_str = "\t".join(doc_terms_list)
                
            s_doc_terms_file.write("%s\n" % doc_terms_str)

            s_infile.close()

            # Using the sets, increment the doc_freq for term-feature pairs in the doc.
            # By making the list a set, we know we are only counting each term-feature combo once
            # per document
            for pair in pair_set:
                d_pair2dfreq[pair] += 1

            # also increment doc_freq for features and terms

            for term in term_set:
                d_term2dfreq[term] +=1

            for feature in feature_set:
                d_feat2dfreq[feature] += 1

            # track total number of docs
            doc_count += 1

        s_filelist.close()

        s_tf_file = codecs.open(tf_file, "w", encoding='utf-8')
        s_terms_file = codecs.open(terms_file, "w", encoding='utf-8')
        s_feats_file = codecs.open(feats_file, "w", encoding='utf-8')
        print "[act_tf.py]Writing to %s" % tf_file

        # compute prob
        print "[act_tf.py]Processed %i files" % doc_count

        for pair in d_pair2dfreq.keys():
            freq_pair = d_pair2dfreq[pair]
            prob_pair = float(freq_pair)/doc_count

            term = pair[0]

            feature = pair[1]
            freq_term = d_term2dfreq[term]
            freq_feat = d_feat2dfreq[feature]

            # Occasionally, we come across a term in freq_pair which is not actually in 
            # the dictionary d_term2dfreq.  It returns a freq of 0.  We need to ignore these
            # cases, since they will create a divide by 0 error.
            if freq_term > 0 and freq_feat > 0:

                # probability of the feature occurring with the term in a doc, given that 
                # the term appears in the doc
                try:
                    prob_fgt = freq_pair/float(freq_term)
                except:
                    pdb.set_trace()

                # added 4/4/15: prob of the feature occurring with the term in a doc, given that 
                # the feature appears in the doc
                try:
                    prob_tgf = freq_pair/float(freq_feat)
                except:
                    pdb.set_trace()

                # 4/18/15 adding mutual information based on count of pairs, terms, feats (counted once per doc),
                # and corpus size (# docs)
                # MI = prob(pair) / prob(term) * prob(feature)
                #prob_term = float(d_term2dfreq[term])/doc_count
                #prob_feature = float(d_feat2dfreq[term])/doc_count
                mi_denom = (freq_term) * (freq_feat) / float(doc_count)
                mi = math.log(freq_pair / mi_denom)
                # normalize to -1 to 1
                # Note: if prob_pair == 1, then log is 0 and we risk dividing by 0
                # We'll prevent this by subtracting a small amt from prob_pair
                if prob_pair == 1:
                    prob_pair = prob_pair - .000000001
                npmi = mi / (-math.log(prob_pair))
                s_tf_file.write( "%s\t%s\t%i\t%f\t%f\t%f\t%i\t%i\t%f\t%f\n" % (term, feature, freq_pair, prob_pair, prob_fgt, prob_tgf, freq_term, freq_feat, mi, npmi))

            else:
                # print out a warning about terms with 0 freq.
                print "[act_tf.py]WARNING: term-feature pair: %s has freq = 0. Ignored." % l_pair

        for term in d_term2dfreq.keys():
            term_prob = float(d_term2dfreq[term])/doc_count
            s_terms_file.write( "%s\t%i\t%i\t%f\n" % (term, d_term2dfreq[term], d_term2cfreq[term], term_prob))

        for feat in d_feat2dfreq.keys():
            feat_prob = float(d_feat2dfreq[feat])/doc_count
            s_feats_file.write( "%s\t%i\t%i\t%f\n" % (feat, d_feat2dfreq[feat], d_feat2cfreq[feat], feat_prob))


        s_canon_file = codecs.open(canon_file, "w", encoding='utf-8')
        for key,value in can.d_n2canon.items():
            s_canon_file.write("%s\t%s\n" % (key, value))
        s_canon_file.close()

        s_tf_file.close()
        s_terms_file.close()
        s_feats_file.close()

        s_doc_terms_file.close()

        # Finally, create a file to store the corpus size (# docs in the source directory)
        cmd = "ls -1 " + filelist_file + " | wc -l > " + corpus_size_file

        s_corpus_size_file = open(corpus_size_file, "w")
        s_corpus_size_file.write("%i\n" % doc_count)
        s_corpus_size_file.close()
        print "[act_tf.py dir2features_count]Storing corpus size in %s " % corpus_size_file

#---
# Create a single file of term feature count for each year (from the .xml extracts of phr_feats data)
# role.run_dir2features_count()
# modified 3/3/14 to take parameters from run_tf_steps
# Set overwrite_p to True to overwrite output files if they already exist.

def run_dir2features_count(filelists_root, out_root, sections, start_year, end_year, overwrite_p=False, max_doc_terms_count=1000):
    #pdb.set_trace()
    int_start = int(start_year)
    int_end = int(end_year) + 1
    print "[act_tf.py]Output dir: %s" % out_root

    # range should be start_year and end_year + 1
    #for int_year in range(1981, 2008):
    #for int_year in range(1995, 2008):
    #for int_year in range(1997, 1998):
    for int_year in range(int_start, int_end):
    
        year = str(int_year)
        filelist_year = filelists_root + "/" + year + ".files"
        print "[act_tf.py]Processing files in: %s" % filelist_year

        dir2features_count(filelist_year, out_root, sections, year, overwrite_p, max_doc_terms_count)
        print "[act_tf.py]Completed: %s" % filelist_year

# python2.7 act_tf.py /home/j/anick/tw/roles/data/corpora/sp/filelists /home/j/anick/tw/roles/data/corpora/sp ta 9999 9999 True 1000
# for a range of dates, use start_year and end_year.  For a single file, make start_year and end_year the same file.
if __name__ == "__main__":
    args = sys.argv
    filelists_root = args[1]
    out_root = args[2]
    sections = args[3] # ta or tas
    start_year = args[4]
    end_year = args[5]
    overwrite_p = args[6]
    max_doc_terms_count = int(args[7])

    # take the defaults, including canonicalization
    run_dir2features_count(filelists_root, out_root, sections, start_year, end_year, overwrite_p=overwrite_p, max_doc_terms_count=max_doc_terms_count)
