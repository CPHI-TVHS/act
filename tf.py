# tf.py
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
"""
 .tf file sample
program prev_VNP=performs|debugging|on  1       0.000022        0.000142
pre-paid card   prev_Npr=amount_of

Need to canonicalize term and feature separately
Remember that features in the seed set have to be consistent (e.g. canonicalized or not) with features here
for probabilities to be consistent.  For now, we will only canonicalize the terms (not the features)
"""

import pdb
import sys
import collections
import os
import glob
import codecs
import roles_config
import canon
import math

# canonicalizer object
can = canon.Canon()

def dir2features_count(inroot, outroot, year, overwrite_p=False, canonicalize_p=True, filter_noise_p=True):
    outfilename = str(year)
    # term-feature output file
    outfile = outroot + outfilename + ".tf"
    # remember the mapping between surface head nouns and their canonicalized forms
    canon_file = outroot + outfilename + ".canon"

    # Do not continue if the .tf file already exists for this corpus and year
    if os.path.isfile(outfile) and not overwrite_p:
        print "[tf.py]file already exists: %s.  No need to recompute." % outfile 
    else:

        terms_file = outroot + outfilename + ".terms"
        feats_file = outroot + outfilename + ".feats"
        corpus_size_file = outroot +  outfilename + ".cs"

        # count of number of docs a term pair cooccurs in
        d_pair_freq = collections.defaultdict(int)
        # count of number of docs a term occurs in
        d_term_freq = collections.defaultdict(int)
        # count of number of instances of a term
        d_term_instance_freq = collections.defaultdict(int)
        # count of number of instances of a feature
        d_feat_instance_freq = collections.defaultdict(int)
        # count of number of docs a feature occurs in
        d_feat_freq = collections.defaultdict(int)

        # Be safe, check if outroot path exists, and create it if not
        if not os.path.exists(outroot):
            os.makedirs(outroot)
            print "Created outroot dir: %s" % outroot

        # doc_count needed for computing probs
        doc_count = 0

        # make a list of all the files in the inroot directory
        filelist = glob.glob(inroot + "/*")

        #print "inroot: %s, filelist: %s" % (inroot, filelist)

        for infile in filelist:

            # process the term files
            # for each file, create a set of all term-feature pairs in the file
            pair_set = set()
            term_set = set()
            feature_set = set()
            #pdb.set_trace()
            s_infile = codecs.open(infile, encoding='utf-8')
            i = 0
            for term_line in s_infile:
                i += 1

                term_line = term_line.strip("\n")
                l_fields = term_line.split("\t")
                term = l_fields[0]
                feature = l_fields[1]
                term_feature_within_doc_count = int(l_fields[2])
                #print "term: %s, feature: %s" % (term, feature)

                """
                # filter out non alphabetic phrases, noise terms
                if alpha_phrase_p(term):
                    pair = term + "\t" + feature
                    print "term matches: %s, pair is: %s" % (term, pair)
                    pair_set.add(pair)
                """


                # if the feature field is "", then we use this line to count term
                # instances
                if feature == "":

                    if (filter_noise_p and canon.illegal_phrase_p(term)):
                        pass
                    else:
                        if canonicalize_p:
                            # Do canonicalization of term before incrementing counts
                            # note we don't canonicalize feature here since feature == ""
                            term = can.get_canon_np(term)

                        d_term_instance_freq[term] += term_feature_within_doc_count
                        # add term to set for this document to accumulate term-doc count
                        term_set.add(term)
                        # note:  In ln-us-cs-500k 1997.tf, it appears that one term (e.g. u'y \u2033')
                        # does not get added to the set.  Perhaps the special char is treated as the same
                        # as another term and therefore is excluded from the set add.  As a result
                        # the set of terms in d_term_freq may be missing some odd terms that occur in .tf.
                        # Later will will use terms from .tf as keys into d_term_freq, so we have to allow for
                        # an occasional missing key at that point (in nbayes.py)
                else:
                    # the line is a term_feature pair
                    # (filter_noise_p should be False to handle chinese)

                    # Do not process noise (illegal) terms or features
                    #///  for cases where feat = "", need to filter!  todo
                    #pdb.set_trace()
                    if (filter_noise_p and canon.illegal_phrase_p(term)) or canon.illegal_feature_p(feature):
                        pass

                    else:

                        if canonicalize_p:
                            # Do canonicalization of term and feature before incrementing counts
                            feature = can.get_canon_feature(feature)
                            term = can.get_canon_np(term)

                        #pdb.set_trace()
                        pair = term + "\t" + feature
                        ##print "term matches: %s, pair is: %s" % (term, pair)
                        pair_set.add(pair)
                        feature_set.add(feature)
                        d_feat_instance_freq[feature] += term_feature_within_doc_count

                        #print "pair: %s, term: %s, feature: %s" % (pair, term, feature)
                        #pdb.set_trace()

            s_infile.close()

            # increment the doc_freq for term-feature pairs in the doc
            # By making the list a set, we know we are only counting each term-feature combo once
            # per document
            for pair in pair_set:
                d_pair_freq[pair] += 1

            # also increment doc_freq for features and terms

            for term in term_set:
                d_term_freq[term] +=1

            for feature in feature_set:
                d_feat_freq[feature] += 1

            # track total number of docs
            doc_count += 1

        s_outfile = codecs.open(outfile, "w", encoding='utf-8')
        s_terms_file = codecs.open(terms_file, "w", encoding='utf-8')
        s_feats_file = codecs.open(feats_file, "w", encoding='utf-8')
        print "Writing to %s" % outfile

        # compute prob
        print "Processed %i files" % doc_count

        for pair in d_pair_freq.keys():
            freq_pair = d_pair_freq[pair]
            prob_pair = float(freq_pair)/doc_count
            l_pair = pair.split("\t")
            term = l_pair[0]
            #print "term after split: %s, pair is: %s" % (term, pair)
            feature = l_pair[1]
            freq_term = d_term_freq[term]
            freq_feat = d_feat_freq[feature]

            # Occasionally, we come across a term in freq_pair which is not actually in 
            # the dictionary d_term_freq.  It returns a freq of 0.  We need to ignore these
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
                #prob_term = float(d_term_freq[term])/doc_count
                #prob_feature = float(d_feat_freq[term])/doc_count
                mi_denom = (freq_term) * (freq_feat) / float(doc_count)
                mi = math.log(freq_pair / mi_denom)
                # normalize to -1 to 1
                # Note: if prob_pair == 1, then log is 0 and we risk dividing by 0
                # We'll prevent this by subtracting a small amt from prob_pair
                if prob_pair == 1:
                    prob_pair = prob_pair - .000000001
                npmi = mi / (-math.log(prob_pair))
                s_outfile.write( "%s\t%s\t%i\t%f\t%f\t%f\t%i\t%i\t%f\t%f\n" % (term, feature, freq_pair, prob_pair, prob_fgt, prob_tgf, freq_term, freq_feat, mi, npmi))

            else:
                # print out a warning about terms with 0 freq.
                print "[tf.py]WARNING: term-feature pair: %s has freq = 0. Ignored." % l_pair

        # /// TODO: this table makes tf.f file redundant!  Replace use of tf.f
        for term in d_term_freq.keys():
            term_prob = float(d_term_freq[term])/doc_count
            s_terms_file.write( "%s\t%i\t%i\t%f\n" % (term, d_term_freq[term], d_term_instance_freq[term], term_prob))

        for feat in d_feat_freq.keys():
            feat_prob = float(d_feat_freq[feat])/doc_count
            s_feats_file.write( "%s\t%i\t%i\t%f\n" % (feat, d_feat_freq[feat], d_feat_instance_freq[feat], feat_prob))


        s_canon_file = codecs.open(canon_file, "w", encoding='utf-8')
        for key,value in can.d_n2canon.items():
            s_canon_file.write("%s\t%s\n" % (key, value))
        s_canon_file.close()

        s_outfile.close()
        s_terms_file.close()
        s_feats_file.close()

        # Finally, create a file to store the corpus size (# docs in the source directory)
        cmd = "ls -1 " + inroot + " | wc -l > " + corpus_size_file
        print "[dir2features_count]Storing corpus size in %s " % corpus_size_file
        os.system(cmd)

#---
# Create a single file of term feature count for each year (from the .xml extracts of phr_feats data)
# role.run_dir2features_count()
# modified 3/3/14 to take parameters from run_tf_steps
# Set overwrite_p to True to overwrite output files if they already exist.

def run_dir2features_count(inroot, outroot, start_range, end_range, overwrite_p ):
    #inroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/cs_500k/data/m1_term_verb_tas/"
    #inroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-all-600k/data/term_features/"
    #outroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-all-600k/data/tv/"

    #inroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/wos-cs-520k/data/term_features/"
    #outroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/wos-cs-520k/data/tv/"

    # cs
    #inroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-cs-500k/data/term_features"
    #outroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-cs-500k/data/tv"

    # chemical
    #inroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-12-chemical/data/term_features"
    #outroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-12-chemical/data/tv"

    # health
    #inroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-14-health/data/term_features"
    #outroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-us-14-health/data/tv"

    # test (4 files from health 1997)
    #inroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/test/data/term_features"
    #outroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/test/data/tv"

    # Chinese cs
    #inroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-cn-all-600k/data/term_features"
    #outroot = "/home/j/anick/patent-classifier/ontology/creation/data/patents/ln-cn-all-600k/data/tv"



    print "Output dir: %s" % outroot

    # range should be start_year and end_year + 1
    #for int_year in range(1981, 2008):
    #for int_year in range(1995, 2008):
    #for int_year in range(1997, 1998):
    for int_year in range(start_range, end_range):
    
        year = str(int_year)
        inroot_year = inroot + year
        print "Processing dir: %s" % inroot_year

        dir2features_count(inroot_year, outroot, year, overwrite_p)
        print "Completed: %s" % year


# python tf.py /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A28-mechanical-engineering/data/term_features/ /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A28-mechanical-engineering/data/tv/ 1998 2007

# python tf.py /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A21-computers/data/term_features/ /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A21-computers/data/tv/ 1997 2007

# python tf.py /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A21-computers/data/term_features/ /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A21-computers/data/tv/ 2002 2002

# 4/7/15 title and abstract data
# python tf.py /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A21-computers/data/term_features_ta/ /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-A21-computers/data/tv/ 2002 2002

# 6/6/15 tas for health
# python tf.py /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/term_features/ /home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/tv/ 2002 2002

# 4/8/18 ta for SignalProcessing
# python tf.py /home/j/anick/tw/roles/data/corpora/SignalProcessing/data/term_features_ta/ /home/j/anick/tw/roles/data/corpora/SignalProcessing/data/tv/ 2002 2002 True


# python2.7 tf.py /home/j/anick/tw/roles/data/corpora/SignalProcessing/data/term_features_ta/ /home/j/anick/tw/roles/data/corpora/SignalProcessing/data/tv/ 2002 2016 True
if __name__ == "__main__":
    args = sys.argv
    inroot = args[1]
    outroot = args[2]
    start_range = int(args[3])
    overwrite_p = bool(args[4])
    # note that for python the end range is not included in the iteration, so
    # we add 1 here to the end_year to make sure the last year is included in the range.
    end_range = int(args[4]) + 1

    # take the defaults, including canonicalization
    run_dir2features_count(inroot, outroot, start_range, end_range, overwrite_p=overwrite_p)

# test using
# note: python2.7 needed for nltk. 
# python2.7 tf.py /home/j/anick/temp/term_features/ /home/j/anick/temp/tv/ 2002 2002 True

