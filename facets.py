#
"""
look for terms with similar  prev_Np phrases to cluster prev_Np phrases into facets

Take a prev_Npr, find all terms that share it.  From those sum up the most common co-coccuring prev_Np's.
These may be synonyms (facets)?

We will use file:
cat ngrams | cut -f2,6 | egrep -v '        $' | sunr > ngrams.f26.sunr
which has count term npr

Different term Frequency of npr is here:
cat ngrams.f26.sunr | cut -f3 | sunr > ngrams.f26.sunr.f3.sunr
"""

from collections import defaultdict
import codecs
import operator
import sys

def npr_facets(basedir, min_count_str):
    # for each prev_Npr, keep a list of terms it dominates
    d_npr2terms = defaultdict(list) 

    # for each term, keep a list of those prev_Npr that dominate the term
    d_term2nprs = defaultdict(list) 

    # Given an npr, get all the terms that co-occur with it
    # for each such term, gets its set of nprs and add 1 to the npr's score 
    # output the npr's sorted by score as related nprs.
    # To start with a smaller set, let's use a threshold of 3 co-occurrences

    infile_name = "ngrams.f26.sunr"
    outfile_wo_count = "npr.rel"

    infile = basedir + infile_name
    outfile = basedir + outfile_wo_count + "." + min_count_str

    # threshold on freq of term and npr to include in computation
    min_count = int(min_count_str)

    s_infile = codecs.open(infile, encoding='utf-8')
    s_outfile = codecs.open(outfile, "w", encoding='utf-8')

    for line in s_infile:
        line = line.strip()
        l_fields = line.split("\t")
        count = int(l_fields[0])
        term = l_fields[1]
        npr = l_fields[2]
        if count >= min_count:
            d_npr2terms[npr].append(term)
            d_term2nprs[term].append(npr)

    for (npr, terms) in d_npr2terms.iteritems():

        # we will sum up the counts of other nprs occurring with terms associated with each npr
        d_cnpr2sum = defaultdict(int)
        for term in terms:
            cnprs = d_term2nprs[term]
            for cnpr in cnprs:
                d_cnpr2sum[cnpr] += 1

        # sort d_cnpr2sum by value
        sorted_cnprs = sorted(d_cnpr2sum.items(), key=operator.itemgetter(1), reverse=True)
        #print("%i\t%s\t%s" % (sorted_cnprs[0][1], npr, sorted_cnprs))

        s_outfile.write("%i\t%s\t%s\n" % (sorted_cnprs[0][1], npr, sorted_cnprs[:10]))
    s_infile.close()
    s_outfile.close()


# python27 facets.py "/home/j/anick/tw/roles/data/corpora/SignalProcessing/data/nc/9999/" 10

# use trailing slash on basedir name
if __name__ == "__main__":
    args = sys.argv
    basedir = args[1]
    min_count_str = args[2]
    npr_facets(basedir, min_count_str)


