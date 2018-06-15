"""
# tf_summary.py
# create a summary .tf file from data across a range of dates
# This allows us to work with data sets larger than a single year

# Before running tf_summary, you must run tf.py, which populates the .tf files 
# for a set of years.  This code uses those files as input to create a .tf file
# for an imaginary year (e.g. 9999) which sums ovet a range of years.

# The .tf file contains 4 fields:
# term


# The directory structure expects that tf.py has created 4 files for each year
# /home/j/anick/tw/roles/data/corpora/SignalProcessing/data/tv
#-rw-r--r--. 1 anick grad  8886540 Apr  8 23:49 2002.tf
#-rw-r--r--. 1 anick grad  1267582 Apr  8 23:49 2002.terms
#-rw-r--r--. 1 anick grad   883806 Apr  8 23:49 2002.feats
#-rw-r--r--. 1 anick grad        5 Apr  8 23:49 2002.cs

# .cs contains the # of docs for the year, needed to compute probabilities
# .tf contains:
# requirement     prev_V=discuss  1       0.000271        0.037037        0.010989        27      91      0.405872        0.049421

We need three dictionaies to accumulate totals across annual data for
pair_freq
term_freq
feat_freq

We also need the total number of docs by summing across annual .cs files
From this data we can recompute all the fields needed for summary .tf file.


# These functions were originally part of role.py but separated out to separate
# generic feature processing from the ACT/PN task.

 NOTE: We assume we are running on UNIX, where directories are separated by "/"

"""

import pdb
import sys
import collections
import os
import glob
import codecs
import roles_config
import math

# subname is a placeholder in case we want to subtype files within the tv subdirectory
# for now assume it is empty ("")  as in <year><.subname>.tf
def dir2features_summary(inroot, year, subname, d_pair2freq, d_term2freq, d_feat2freq):

    tf_file = inroot + year + subname + ".tf"
    cs_file = inroot + year + subname + ".cs"

    # Note that the doc freq of a term and the doc freq of a feature occuring in a given year
    # is redundantly stored in every line of the .tf file that contains the term or feature.
    # We will use this to sum up term and feat frequencies over the range of years, but we only
    # want to add the freq in once, not every time we come across a line with that term or feature.
    # So we'll keep track of whether we have already seen and recorded this info in d_term2seen_p and
    # d_feat2seen_p.  bool value defaults to False.
    d_term2seen_p = collections.defaultdict(bool)
    d_feat2seen_p = collections.defaultdict(bool)

    #pdb.set_trace()
    s_tf_file = codecs.open(tf_file, encoding='utf-8')
    i = 0
    for term_line in s_tf_file:
        i += 1
            
        term_line = term_line.strip("\n")
        l_fields = term_line.split("\t")
        term = l_fields[0]
        feature = l_fields[1]
        pair = term + "\t" + feature
        d_pair2freq[pair] += int(l_fields[2])
        # the following two fields are already totals for the year, so we do not need to add
        # values.  We just save them.
        if not d_term2seen_p[term]:
            d_term2freq[term] += int(l_fields[6])
            d_term2seen_p[term] = True
        if not d_feat2seen_p[feature]:
            d_feat2freq[feature] += int(l_fields[7])
            d_feat2seen_p[feature] = True
        #print "term: %s, feature: %s" % (term, feature)

    s_tf_file.close()

    s_cs_file = codecs.open(cs_file, encoding='utf-8')
    corpus_size = s_cs_file.readline()
    corpus_size = int(corpus_size.strip("\n"))

    return(corpus_size)


#---
# Create a single file of term feature count for each year (from the .xml extracts of phr_feats data)
# role.run_dir2features_count()
# modified 3/3/14 to take parameters from run_tf_steps
def run_dir2features_summary(inroot, outroot, subname, start_range, end_range, pseudo_year):
    print "Output dir: %s" % outroot

    # dictionaries to hold data summed across years
    # pair2freq key is term|feat
    d_pair2freq = collections.defaultdict(int)
    # number docs containing the term
    d_term2freq = collections.defaultdict(int)
    # number docs containing the feature
    d_feat2freq = collections.defaultdict(int)
    # total corpus size (num documents in oorpus)
    doc_count = 0

    # range should be start_year and end_year + 1
    for int_year in range(start_range, end_range):
    
        year = str(int_year)
        print "Processing dir: %s" % inroot

        # update the dictionaries and return the annual doc count (from .cs file)
        yearly_doc_count = dir2features_summary(inroot, year, subname, d_pair2freq, d_term2freq, d_feat2freq)
        print "Completed: %s" % year
        doc_count += yearly_doc_count
        
    # output accumulated data
    # total corpus size (# docs)

    cs_file = outroot + pseudo_year + subname + ".cs"
    s_cs_file = codecs.open(cs_file, "w", encoding='utf-8')
    s_cs_file.write("%i\n" % (doc_count))
    s_cs_file.close()

    # tf_file stats
    # This section is equivalent to a section in tf.py 

    tf_outfile = outroot + pseudo_year + subname + ".tf"
    s_tf_outfile = codecs.open(tf_outfile, "w", encoding='utf-8')

    for pair in d_pair2freq.keys():
        freq_pair = d_pair2freq[pair]
        prob_pair = float(freq_pair)/doc_count
        l_pair = pair.split("\t")
        term = l_pair[0]
        #print "term after split: %s, pair is: %s" % (term, pair)
        feature = l_pair[1]
        freq_term = d_term2freq[term]
        freq_feat = d_feat2freq[feature]
        
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
            s_tf_outfile.write( "%s\t%s\t%i\t%f\t%f\t%f\t%i\t%i\t%f\t%f\n" % (term, feature, freq_pair, prob_pair, prob_fgt, prob_tgf, freq_term, freq_feat, mi, npmi))

        else:
            # print out a warning about terms with 0 freq.
            print "[tf.py]WARNING: term-feature pair: %s has term or feat freq = 0. Ignored." % l_pair

    s_tf_outfile.close()

# 4/26/18 ta for SignalProcessing

# python tf_summary.py /home/j/anick/tw/roles/data/corpora/SignalProcessing/data/tv/ "" 2002 2003 9992
if __name__ == "__main__":
    args = sys.argv
    inroot = args[1]
    # check for "/" at end of inroot
    if inroot[-1] != "/":
        inroot = inroot + "/"
    outroot = args[1]
    subname = args[2]
    start_range = int(args[3])
    # note that for python the end range is not included in the iteration, so
    # we add 1 here to the end_year to make sure the last year is included in the range.
    end_range = int(args[4]) + 1

    # create a year-like name to stand in for the summary directory.
    # Since the rest of the code expects years, we'll simply treat this data as if it came
    # from a single year, e.g. 9999
    # We'll pass it on as a string
    pseudo_year = args[5]

    run_dir2features_summary(inroot, outroot, subname, start_range, end_range, pseudo_year)
