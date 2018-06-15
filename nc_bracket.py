# pmi.py compute normalized pointwise mutual information

import roles_config
import pnames
import os
import sys
import re
import codecs
import pdb
import math
import copy
from collections import defaultdict

# pmi.gram_tuple2string(gtuple)
# convert a tuple into the equivalent string
def gram_tuple2string(gram_tuple):
    gram_string = " ".join(gram_tuple)
    return(gram_string)

# reduce a part of speech tag string to a single word made up
# of the fist letter of each tag.
# pmi.abbrev_pos("JJ NN NNS") => "JNN"
def abbrev_pos(pos_string):
    l_pos = pos_string.split(" ")
    return("".join(map(lambda x: x[0], l_pos)))

# convert number to string.  All else return as is.
def num2str(unknown):
    if isinstance(unknown, (int, long, float)):
        return(str(unknown))
    else:
        return(unknown)

# This sums up the instances of canonical n-grams to get a total frequency across corpus and docs.
# The frequency is instance frequency since the file data has one entry per gram occurrence.

# create a subset for testing:
# cat trigrams.inst.filt | sort > trigrams.inst.filt.sorted
# cat trigrams.inst.filt.sorted | head -100000 | tail -10000 > trigrams.inst.filt.sorted.test
# pmi.dump_canon_gram_freq("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/trigrams.inst.filt"
# creates a file .freq with fields: term, corpus_freq, doc_freq, pos  (term is canonical np) 
def dump_canon_gram_freq(gram_file):
    freq_file = gram_file + ".freq"
    s_gram = codecs.open(gram_file, encoding='utf-8') 
    s_freq = codecs.open(freq_file, "w", encoding='utf-8') 
    
    # sum instances to get corpus freq
    d_gram2freq = defaultdict(int)
    # keep the abbreviated part of speech signature
    d_gram2pos = {}
    # use the set of doc_ids to get doc freq
    d_gram2doc_ids = defaultdict(set)

    for line in s_gram:
        line = line.strip()
        l_line = line.split("\t")
        canonical_form = l_line[0]
        doc_id = l_line[1]
        # We have already abbreviated the pos_signature in earlier step
        #pos = abbrev_pos(l_line[3])
        pos = l_line[2]
        
        d_gram2freq[canonical_form] += 1
        d_gram2doc_ids[canonical_form].add(doc_id)
        d_gram2pos[canonical_form] = pos

    for term in d_gram2freq:
        corpus_freq = str(d_gram2freq[term])
        doc_freq = str(len(d_gram2doc_ids[term]))
        pos = d_gram2pos[term]
        output_string = "\t".join([term, corpus_freq, doc_freq, pos])
        s_freq.write("%s\n" % output_string)

    s_gram.close()
    s_freq.close()


class NCAssoc():
    """
    Class to compute all NC association measures.
    Subsumes class MI, which just computes mutual information variants.
    Measures come from Nakov:
    freq
    conditional_prob (Lauer)
    MI
    x2
    """

    def __init__(self):
        self.d_AB2freq = defaultdict(int)
        self.d_A2freq  = defaultdict(int)
        self.d_B2freq  = defaultdict(int)
        self.d_AB2cprob = defaultdict(float)
        self.d_AB2npmi = defaultdict(float)
        # note that d_AB2mi could return an empty list if AB does not occur in corpus
        self.d_AB2mi = defaultdict(list)
        self.d_AB2chi2 = defaultdict(float)
        # total doc_freq of all bigrams
        self.all_AB_freq = 0

    # external access to bigram raw data 
    # AB is a tuple with two words (comprising a bigram)
    # NOTE that because they are defaultdict, if a bigram does not exist 
    # the value returned will be 0.  
    def bg2freq(self, AB):
        return(self.d_AB2freq[AB])
    def bg2cprob(self, AB):
        return(self.d_AB2cprob[AB])
    def bg2npmi(self, AB):
        return(self.d_AB2npmi[AB])
    def bg2chi2(self, AB):
        return(self.d_AB2chi2[AB])

    # AB is a tuple containing two strings
    # input to load is a tuple and its frequency (typically the number of docs the pair appears in)
    # If the same tuple is loaded multiple times, we compute the sum of individual frequencies.
    # Note that we have to load all bigrams in the collection, even we are only interested in a subset, in
    # order to obtain the corpus statistics needed for denominators (e.g. freq(term_A, any_term_B)
    def load(self, AB, doc_freq):
        # AB term_tuple is a tuple containing two ordered terms A, B
        A = AB[0]
        B = AB[1]
        # increment freq count for tuple AB and its components
        self.d_AB2freq[AB] += doc_freq
        # note that the frequencies are based solely on bigrams
        # AX freq
        self.d_A2freq[A] += doc_freq
        # XB freq
        self.d_B2freq[B] += doc_freq

        # total # of pairs
        self.all_AB_freq += doc_freq

    # bigram file has: term corpus_freq doc_freq pos_signature (.freq file)
    def load_bigram_file(self, bigram_file):
        s_bigram_data = codecs.open(bigram_file, encoding='utf-8')
        for line in s_bigram_data:
            line = line.strip()
            l_fields = line.split("\t")
            corpus_freq = int(l_fields[1])
            doc_freq = int(l_fields[2])
            pos_sig = l_fields[3]
            # we split into a tuple so that the load method can index
            # by the tuple and also compute freq for AX and XB occurrences
            AB = tuple(l_fields[0].split(" "))
            # for now, we ignore the corpus_freq and pos_sig for bigrams and just keep the doc freq
            self.load(AB, doc_freq)
        s_bigram_data.close()

    # conditional prob of AB given XB (B as head of any bigram)
    def compute_cprob(self, AB):
        # freq(AB) / freq(B)
        # If AB is a phrase, then B should exist
        B = AB[1]
        AB_B_cprob = float(self.d_AB2freq[AB])/float(self.d_B2freq[B])
        return(AB_B_cprob)

    def compute_chi2(self, AB):
        # chi2 has four boxes:
        # a: freq(AB)
        # b: freq(A, !B) = freq(AX) - freq(AB)
        # c: freq(!A, B) = freq(XB) - freq(AB)
        # d: freq(!A, !B) = total bigrams -a -b -c
        # chi2 = N(a*d - b*c)^2 / (a + c) (b + d) (a + b) (c + d)
        A = AB[0]
        B = AB[1]
        N = self.all_AB_freq
        a = self.d_AB2freq[AB]
        b = self.d_A2freq[A] - a
        c = self.d_B2freq[B] - a
        d =  N - (a + b + c)
        chi2 = (N * math.pow( ((a * d)  - (b * c)), 2) ) / float( (a + c) * (b + d) * (a + b ) * (c + d))
        #pdb.set_trace()
        return(chi2)

    def compute_mi(self, AB, verbose_p=False):
        # default value in case the pmi cannot be computed due to 0 freq somewhere
        pmi = -1000
        mi = -1000
        norm_pmi = -1000  
        
        A = AB[0]
        B = AB[1]

        A_prob = float(self.d_A2freq[A])/self.all_AB_freq
        B_prob = float(self.d_B2freq[B])/self.all_AB_freq
        AB_prob = float(self.d_AB2freq[AB])/self.all_AB_freq

        # compute normalized pmi
        # Check for odd cases where a term prob of 0 arises
        # It shouldn't happen but it does
        denom = A_prob * B_prob

        if denom == 0:
            if verbose_p:
                print "0 probability for term A: [%s, %f] or term B: [%s, %s]" % (A, A_prob, B, B_prob)
            pass
        elif AB_prob == 0:
            if verbose_p:
                print "0 probability for pair AB: %s, %s" % (A, B)
            pass
        else:
            pmi = math.log(AB_prob/(A_prob * B_prob),2)
            mi = AB_prob * pmi
            norm_pmi = pmi / (-1 * math.log(AB_prob, 2))

            if verbose_p:
                print "[pmi]npmi for %s %s: %f, freq/probs: %i/%f, %i/%f, %i/%f" % (A, B, norm_pmi, self.d_A2freq[A], A_prob, self.d_B2freq[B], self.B_prob, self.d_AB2freq[AB], AB_prob)

        return([pmi, norm_pmi, mi])
    
    # compute and store association metrics
    def compute_assoc(self):
        for AB in self.d_AB2freq.keys():
            AB_freq = self.d_AB2freq[AB]
            l_mi = self.compute_mi(AB)
            pmi = l_mi[0]
            npmi = l_mi[1]
            mi = l_mi[2]
            A = AB[0]
            B = AB[1]
            A_freq = self.d_A2freq[A]
            B_freq = self.d_B2freq[B]
            cprob = self.compute_cprob(AB)
            chi2 = self.compute_chi2(AB)
            # store the computed values in dicts
            self.d_AB2cprob[AB] = cprob
            self.d_AB2mi[AB] = l_mi
            # AB2npmi is redundant with AB2mi but will return 0 for a non-occurring AB
            # So for convenience, we keep an extra dict.
            self.d_AB2npmi[AB] = npmi
            self.d_AB2chi2[AB] = chi2

    # .assoc file format: AB_string, AB_freq, A_freq, B_freq, mi, pmi, npmi, cprob, chi2
    def dump_assoc(self, outfile):
        s_out = codecs.open(outfile, "w", encoding='utf-8')
        for AB in self.d_AB2freq.keys():
            AB_string = gram_tuple2string(AB)
            AB_freq = self.d_AB2freq[AB]
            l_mi = self.d_AB2mi[AB]
            pmi = l_mi[0]
            npmi = l_mi[1]
            mi = l_mi[2]
            A = AB[0]
            B = AB[1]
            A_freq = self.d_A2freq[A]
            B_freq = self.d_B2freq[B]
            cprob = self.compute_cprob(AB)
            chi2 = self.compute_chi2(AB)
            
            s_out.write("%s\t%i\t%i\t%i\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\n" % (AB_string, AB_freq, A_freq, B_freq, mi, pmi, npmi, cprob, chi2))
            
        s_out.close()

class Trigram():
    # pass in ncassoc containing all the bigram data for the corpus
    def __init__(self, ncassoc):
        self.ncassoc = ncassoc
        self.d_trigram2corpus_freq = {}
        self.d_trigram2doc_freq = {}
        self.d_trigram2pos_sig = {}
        self.d_trigram2predictions = {}
        self.d_trigram2bigram_data = {}
        self.d_trigram2summary = {}

    # trigram bracketing predictions
        
    def load_trigram_file(self, trigram_file):
        # file contains: trigram corpus_freq doc_freq pos_signature
        s_trigram_data = codecs.open(trigram_file, encoding='utf-8')
        for line in s_trigram_data:
            line = line.strip()
            l_fields = line.split("\t")
            trigram = l_fields[0]
            corpus_freq = int(l_fields[1])
            doc_freq = int(l_fields[2])
            pos_sig = l_fields[3]

            self.load_trigram(trigram, corpus_freq, doc_freq, pos_sig)
        s_trigram_data.close()


    # summary file contains: [trigram, pos_sig, doc_freq, fr_AB, fr_BC, fr_AC, pred_summary]
    def dump_trigram(self, output_file, verbose_p=False):
        s_output = codecs.open(output_file, "w", encoding='utf-8') 
        summary_file = output_file + ".sum"
        s_summary = codecs.open(summary_file, "w", encoding='utf-8') 
        for trigram in self.d_trigram2corpus_freq:
            cf = self.d_trigram2corpus_freq[trigram]
            df = self.d_trigram2doc_freq[trigram]
            ps = self.d_trigram2pos_sig[trigram]
            l_pred = self.d_trigram2predictions[trigram]
            l_bigram_data = self.d_trigram2bigram_data[trigram] 
            bigram_str = "\t".join(map(lambda x: num2str(x), l_bigram_data))
            pred_string = "\t".join(map(lambda x: num2str(x), l_pred))
            trigram_string = "\t".join(map(lambda x: num2str(x), [trigram, cf, df, ps]))
            s_output.write("%s\t%s\t%s\n" % (trigram_string, pred_string, bigram_str))
            
            s_summary.write("%s\n" % "\t".join(map(lambda x: num2str(x), self.d_trigram2summary[trigram])))
        s_output.close()
        s_summary.close()

    def load_trigram(self,trigram, corpus_freq, doc_freq, pos_sig, verbose_p=False):
        self.d_trigram2corpus_freq[trigram] = corpus_freq
        self.d_trigram2doc_freq[trigram] = doc_freq
        self.d_trigram2pos_sig[trigram] = pos_sig

        # bracketing predictions  based on Nakov thesis p. 49
        # given a triple (string), predict bracketing based on several association models
        ABC = trigram.split(" ")
        AB = tuple( ABC[0:2] )
        BC = tuple( ABC[1:3] )
        AC = tuple( [ABC[0], ABC[2] ] )
        #print "phrase: %s, AB: %s, BC: %s, AC: %s" % (ABC, AB, BC, AC)
        # compute assoc measures for AB, BC, AC
        fr_AB = self.ncassoc.bg2freq(AB)
        fr_BC = self.ncassoc.bg2freq(BC)
        fr_AC = self.ncassoc.bg2freq(AC)

        cp_AB = self.ncassoc.bg2cprob(AB)
        cp_BC = self.ncassoc.bg2cprob(BC)
        cp_AC = self.ncassoc.bg2cprob(AC)
        npmi_AB = self.ncassoc.bg2npmi(AB)
        npmi_BC = self.ncassoc.bg2npmi(BC)
        npmi_AC = self.ncassoc.bg2npmi(AC)
        x2_AB = self.ncassoc.bg2chi2(AB)
        x2_BC = self.ncassoc.bg2chi2(BC)
        x2_AC = self.ncassoc.bg2chi2(AC)

        # save bigram data as list and string
        l_bigram_data = [fr_AB, fr_BC, fr_AC, cp_AB, cp_BC, cp_AC, npmi_AB, npmi_BC, npmi_AC, x2_AB, x2_BC, x2_AC]
        str_bigram_data = "\t".join(map(lambda x: str(x), l_bigram_data))
        self.d_trigram2bigram_data[trigram] = l_bigram_data

        if verbose_p:
            print "for phrase: %s" % trigram
            print "[load_trigram]bigram_data: %s" % str_bigram_data
            #print "fr_AB\tfr_BC\tfr_AC\tcp_AB\tcp_BC\tcp_AC\tnpmi_AB\tnpmi_BC\tnpmi_AC\tx2_AB\tx2_BC\tx2_AC"
            #print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (fr_AB, fr_BC, fr_AC, cp_AB, cp_BC, cp_AC, npmi_AB, npmi_BC, npmi_AC, x2_AB, x2_BC, x2_AC)

        # set default predictions to "L"
        adj_fr = "L"
        adj_cp = "L"
        adj_npmi = "L"
        adj_x2 = "L"
        dep_fr = "L"
        dep_cp = "L"
        dep_npmi = "L"
        dep_x2 = "L"
        # for adjacency model, we compare AB to BC
        if fr_BC > fr_AB:
            adj_fr = "R"
        elif fr_BC == fr_AB:
            adj_fr = "U"
        if cp_BC > cp_AB:
            adj_cp = "R"
        elif cp_BC == cp_AB:
            adj_cp = "U"
        if npmi_BC > npmi_AB:
            adj_npmi = "R"
        elif npmi_BC == npmi_AB:
            adj_npmi = "U"
        if x2_BC > x2_AB:
            adj_x2 = "R"
        elif x2_BC == x2_AB:
            adj_x2 = "U"

        # for dependencency model, we compare AC to AB
        if fr_AC > fr_AB:
            dep_fr = "R"
        elif fr_AC == fr_AB:
            dep_fr = "U"
        if cp_AC > cp_AB:
            dep_cp = "R"
        elif cp_AC == cp_AB:
            dep_cp = "U"
        if npmi_AC > npmi_AB:
            dep_npmi = "R"
        elif npmi_AC == npmi_AB:
            dep_npmi = "U"
        if x2_AC > x2_AB:
            dep_x2 = "R"
        elif x2_AC == x2_AB:
            dep_x2 = "U"

        # a shortened set of useful predictions (to compare frequency based adj/dep, and chi2-based)
        # a field is created of the form fAD xAD   where A and D are the respective predictions of adj and dep models.
        pred_summary = "".join(["f", adj_fr, dep_fr, " x", adj_x2, dep_x2])
        l_summary = [trigram, pos_sig, doc_freq, fr_AB, fr_BC, fr_AC, pred_summary]
        self.d_trigram2summary[trigram] = l_summary
        l_prediction = [adj_fr, adj_cp, adj_npmi, adj_x2, dep_fr, dep_cp, dep_npmi, dep_x2]
        self.d_trigram2predictions[trigram] = l_prediction

        prediction_string = "\t".join([trigram, pos_sig, str(corpus_freq), str(doc_freq), str(fr_AB), str(fr_BC), adj_fr, adj_cp, adj_npmi, adj_x2, dep_fr, dep_cp, dep_npmi, dep_x2])
        
        #print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % ...
        return([prediction_string, l_prediction])


# l_assoc97 = pmi.run_assoc97()
# NOTE: Make sure each year uses a separate class instance or they will accumulate data from multiple years!
def run_assoc97():

    #"""
    # for 1997
    # full set of bigrams:
    assoc97 = NCAssoc()
    #assoc.load_bigram_file("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/bigrams.inst.filt.su.f1.uc1.nr")
    assoc97.load_bigram_file("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/bigrams.inst.filt.freq")
    assoc97.compute_assoc()
    #assoc97.dump_assoc("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/bigrams.assoc")

    tg97 = Trigram(assoc97)
    tg97.load_trigram_file("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/trigrams.inst.filt.freq")
    tg97.dump_trigram("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/trigrams.pred")

    return([assoc97, tg97])
    #"""

# l_assoc03 = pmi.run_assoc03()
# NOTE: Make sure each year uses a separate class instance or they will accumulate data from multiple years!
def run_assoc03():

    # for 2003
    assoc03 = NCAssoc()
    assoc03.load_bigram_file("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_2003/bigrams.inst.filt.freq")
    assoc03.compute_assoc()
    #assoc03.dump_assoc("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_2003/bigrams.assoc")

    tg03 = Trigram(assoc03)
    tg03.load_trigram_file("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_2003/trigrams.inst.filt.freq")
    tg03.dump_trigram("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_2003/trigrams.pred")

    return([assoc03, tg03])

# test loading trigrams individually using load_trigram.
# cass = pmi.test_assoc_cell()
# cat bigrams.inst.filt.freq | grep cell > bigrams.inst.filt.freq.cell
def test_assoc_cell():
    assoc = NCAssoc()
    assoc.load_bigram_file("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/bigrams.inst.filt.freq.cell")
    assoc.compute_assoc()
    assoc.dump_assoc("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/bigrams.assoc.cell")

    tg = Trigram(assoc)
    #tg.load_trigram_file("trigrams.inst.filt.freq.cell")
    tg.load_trigram("human cell line", 357, 234, "JNN")
    tg.load_trigram("stem cell line", 6, 6, "NNN")
    tg.load_trigram("ceramide treated cell",   2,      2,       "NJN")
    tg.load_trigram("cell structure test",     1,       1,       "NNN")
    tg.load_trigram("cerebellar purkinje cell",        13,      13,      "NNN")
    tg.dump_trigram("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/trigrams.test.cell.pred")
    
    return(assoc)

# l_cass = pmi.test_assoc_cell_file()
# cat bigrams.inst.filt.freq | grep cell > bigrams.inst.filt.freq.cell
# cat trigrams.inst.filt.freq | grep " cell" > trigrams.inst.filt.freq.cell
# test loading from a trigram file
def test_assoc_cell_file():
    assoc = NCAssoc()
    assoc.load_bigram_file("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/bigrams.inst.filt.freq.cell")
    assoc.compute_assoc()
    assoc.dump_assoc("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/bigrams.assoc.cell")

    tg = Trigram(assoc)
    tg.load_trigram_file("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/trigrams.inst.filt.freq.cell")
    tg.dump_trigram("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/trigrams.test.cell.pred")
    
    return([assoc, tg])


# pmi.pred_cprobs("/home/j/anick/patent-classifier/ontology/roles/data/nc/bio_1997/trigrams.pred.sum")
# example input line: pooled peak fraction    JNN     3       5       89      104     fRR xRR
def pred_cprobs(sum_file):

    cprob_file = sum_file + ".cprob"
    s_sum = codecs.open(sum_file, encoding='utf-8') 
    s_cprob = codecs.open(cprob_file, "w", encoding='utf-8') 
    
    # count the number of different phrases containing term as word1,2,3
    # key is tuple of word, word_position (1,2,3) and initial pos (N, J)
    d_w2freq = defaultdict(int)

    # key is a tuple of word, word_position (1,2,3) initial pos and prediction where prediction is one of (fXX, xXX)
    d_w_pred2freq = defaultdict(int)
    # key is initial_POS and pred (fXX or xXX)
    d_pred2freq  = defaultdict(int)

    for line in s_sum:
        line = line.strip()
        l_line = line.split("\t")
        trigram = l_line[0]
        initial_pos = l_line[1][0]
        trigram_freq = int(l_line[2])
        (fpred, xpred) = l_line[6].split(" ")
        l_words = trigram.split(" ")

        # update dictionaries
        for word_index in [0, 1, 2]:
            word = l_words[word_index] 
            # key is tuple of word, word_index (0,1,2) and initial pos (N, J)
            d_w2freq[(word, word_index, initial_pos)] += 1
            # add prediction to key
            # for frequency based prediction
            d_w_pred2freq[(word, word_index, initial_pos, fpred)] += 1
            # for chi2 based prediction
            d_w_pred2freq[(word, word_index, initial_pos, xpred)] += 1

        # count number of predictions given the initial_pos and pred
        d_pred2freq[(initial_pos, fpred)] += 1
        d_pred2freq[(initial_pos, xpred)] += 1

    # generate output (prob prediction given word index and initial pos of trigram
    for key in d_w_pred2freq.keys():
        word = key[0]
        word_index = key[1]
        initial_pos = key[2]
        pred = key[3]
        word_freq = d_w2freq[(word, word_index, initial_pos)]
        w_pred_freq = d_w_pred2freq[key]
        cprob = w_pred_freq / float(word_freq) 
        output_list = [word, "P" + str(word_index), initial_pos, pred, str(w_pred_freq), str(word_freq), str(cprob)]
        output_string = "\t".join(output_list)
        s_cprob.write("%s\n" % output_string)

    s_sum.close()
    s_cprob.close()


# ncDir should not contain trailing slash
if __name__ == "__main__":

    args = sys.argv
    ncDir = args[1]
    bigram_file = ncDir + "/bigrams.inst.filt"
    bigram_freq_file = bigram_file + ".freq" 
    trigram_file = ncDir + "/trigrams.inst.filt"
    trigram_freq_file = trigram_file + ".freq" 
    trigram_pred_file = ncDir + "/trigrams.pred"
    dump_canon_gram_freq(bigram_file)
    dump_canon_gram_freq(trigram_file)

    # This created the .freq files
    # Now we compute the NC metrics

    assoc = NCAssoc()
    assoc.load_bigram_file(bigram_freq_file)
    trigrams = Trigram(assoc)
    trigrams.load_trigram_file(trigram_freq_file)
    trigrams.dump_trigram(trigram_pred_file)

