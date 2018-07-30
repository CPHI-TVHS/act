# -*- coding: utf-8 -*-

"""
tw_es.py Finding related terms using elasticsearch
DocTerms is a document made up of the first 500 terms found in a document, with fields for (1) all terms
(including duplicates) in the form of a single text blob, and 
(2) a set of terms (without duplicates) as an 
array of keywords.

NOTE: It appears that the document type must be named "doc".  
Whenever I gave the doc_type a different
name, I got an error.  I could not add a different doc_type 
in the meta section of the class definition.

"""

import pdb
import re
import glob
import os
import sys
import log
import math
import collections
from collections import defaultdict
import codecs
import putils
import act_pnames

# imports for elasticsearch
import json
import time
import csv
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, DocType, Text, Keyword, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import tokenizer, analyzer
from elasticsearch_dsl.query import MultiMatch, Match

#import shelve
# NOTE: shelve in python 2.7 does not support unicode keys. So, instead of
# using shelve, the demo uses a dictionary that must be loaded into 
# memory when the python code is started.  To support larger databases,
# the code should migrate to python 3 and use shelve or else adopt some
# other stable storage solution (e.g., sqlite).

# !! DocTerms meta information contains the name of the elasticsearch index.
# Currently this is hard_coded into the class, so make sure the index you
# want to query is set within that file before running tw_query.py
from tw_es import DocTerms
import roles_config

search = DocTerms.search()

# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Establish elasticsearch instance
es = Elasticsearch()

# dictionary mapping terms to information (head, cat, freq)
d_ti = {}
CORPUS_SIZE = 0
def make_term_dict(corpus_root, corpus, sections, classifier_type, context_type, year):
    """
    Read in the file created by run_make_term_info and create a dictionary 
    for use in elasticsearch runtime
    """

    print "[act_term_info.py]Starting run_make_term_shelf"
    sections_path = act_pnames.sections_root(corpus_root, corpus, sections)
    term_info_path = sections_path + "/" + year + ".term_info"
    cs_path = sections_path + "/" + year + ".cs"
    term_shelf_path = sections_path + "/" + year + "_cache.term_info"

    s_term_info = codecs.open(term_info_path, encoding='utf-8')

    class TermInfo:
        def __init__(self, term, head, cat, df):
            self.term = term
            self.head = head
            self.cat = cat
            self.df = df
    
    # dictionary implementation of term_info database
    d_ti = {}

    # first populate dict of terms to doc freq
    # Note that this file will contain terms that are not in .classes, since
    # we do not label terms that have no relevant features.
    
    # store the corpus_size as a special entry under term "|corpus_size|"
    with open(cs_path) as f:

        corpus_size = int(f.readline().strip())
        print "[act_term_info.py]corpus_size: %i" % corpus_size

    # Persistent storage of term_info has not been implemented
    # shelve does not allow unicode keys in python 2.7 (fixed in 3.x)
    # fcache gives a "Permission denied" error when we try to populate a cache
    #term_shelf = shelve.open(term_shelf_path)
    #term_shelf = FileCache(term_shelf_path)

    
    # store the corpus_size as special term
    d_ti["|corpus_size|"] = TermInfo("|corpus_size|", "", "", corpus_size)

    for line in s_term_info:
        line = line.strip("\n")

        (term, head, cat, df) = line.split("\t")
        df = int(df)
        #pdb.set_trace()
        #term_shelf[term] = TermInfo(term, head, cat, df)
        d_ti[term] = TermInfo(term, head, cat, df)

    #term_shelf.close()
    s_term_info.close()
    #print "[act_term_info.py]Shelf %s populated" % term_shelf_path
    print "[act_term_info.py]d_ti term_info dictionary populated" 
    return(d_ti)


# load the term_info dictionary ///
# tw_query.run_make_term_dict("sp3", "ta", "9999")
def run_make_term_dict(corpus, sections, year):
    corpus_root = roles_config.CORPUS_ROOT
    classifier_type = roles_config.CLASSIFIER_TYPE
    context_type = roles_config.CONTEXT_TYPE

    d_ti = make_term_dict(corpus_root, corpus, sections, classifier_type, context_type, year)
    return(d_ti)

# r = tw_query.mquery("support vector", 200)
def mquery(query, max_hits=100, operator='or', sort_by="r", df_factor=1):

    d_term2freq = defaultdict(int)
    d_term2idf = defaultdict(int)

    #s = search.query("match", text=query, operator="and")
    #s = search.query("match", text=query)
    s = search.query("match", text={'query': query, 'operator': operator})
    # using slice on s gives up to specified number of results.
    # otherwise, you will get the default match size of 10
    response = s[0:max_hits].execute()
    print "Number hits: %i, operator: %s" % (len(response), operator)
    # sum up the number of occurrences of terms in top max_hits restults
    #pdb.set_trace()
    for hit in response[0:max_hits]:
        for term in hit.term:
            d_term2freq[term] += 1
    sorted_keys = []

    # Now we have the "tf" (actually the number of docs a term 
    # occurs in within the result set for the current query.)
    # Next we compute idf for each term in the results.
    for (term, df) in d_term2freq.iteritems():
        # A higher df_factor will give greater weight to df
        df = df * df_factor
        idf = (1 + math.log(df)) * math.log(CORPUS_SIZE / (d_ti[term].df * 1.0))
        # store idf 
        d_term2idf[term] = idf

    for key, value in sorted(d_term2idf.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        #print "%s: %s" % (key, value)
        sorted_keys.append((key, value))
        
    return(sorted_keys)

# tw_query.psk(r, 10, True)
# tw_query.psk(r)
# sort by relevance (r) or alphabetic (a)

def psk(sorted_keys, max=20, cat_p=True, sort_by="r"):
    """
    Print a subset of sorted keys from the list sorted_keys, 
    classified into ACT categories (attribute, component, task).
    Also return a dictionary containing the same info.
    Sort is by relevance to a query.
    Max is the maximum number of terms to keep for each category.
    cat_p: If true, sort results by category.  If false, just 
    return top uncategorized terms sorted by relevance.
    sort_by: If "r", sort max top relevant terms by relevance.
    If "a", sort alphabetically.
    
    NOTE: The printing of terms to the terminal can be removed.
    """
    result_max = 1000
    # dictionary for returning results
    d_qresult = {}
    if cat_p:
        # display by category
        l_a = []
        l_c = []
        l_t = []
        for key, value in sorted_keys[0:result_max]:
            if d_ti[key].cat == "c":
                l_c.append(key)
            elif d_ti[key].cat == "a":
                if len(key.split(" ")) >= 2:
                    l_a.append(key)
            elif d_ti[key].cat == "t":
                if len(key.split(" ")) >= 2:
                    l_t.append(key)
                    
                    
                    
        # create a dictionary in which to return the result of the query
        d_qresult = { "tasks" : l_t[0:max],
                      "attributes" : l_a[0:max],
                      "components" : l_c[0:max] }
        if sort_by == "a":
            print "Sorted alphabetically"
            print "\n***TASKS:\n%s" % "\n".join(sorted(l_t[0:max]))
            print "\n***ATTRIBUTES:\n%s" % "\n".join(sorted(l_a[0:max]))
            print "\n***COMPONENTS:\n%s" % "\n".join(sorted(l_c[0:max]))
        else:
            print "Sorted by relevance"
            print "\n***terminology related to COMPONENTS:\n%s" % "\n".join(l_c[0:max])
            print "\n***terminology related to TASKS:\n%s" % "\n".join(l_t[0:max])
            print "\n***terminology related to ATTRIBUTES:\n%s" % "\n".join(l_a[0:max])

            

    else:
        
        # just print out terms in sorted order
        for key, value in sorted_keys[0:max]:
            print "%s: %d" % (key, value)

    print "\n"
    print "d_qresult: %s" % d_qresult
    return(d_qresult)


# query and printed results (up to 20 in each cat)
# tw_query.pquery("support vectors")
# tw_query.pquery("signal processing")
# tw_query.pquery("signal processing", 50, "or", "r", 10)

def pquery(query, max_hits=50, operator='or', sort_by="r", df_factor=1):
    sorted_keys = mquery(query, max_hits, operator, sort_by, df_factor)
    
    d_qresult = psk(sorted_keys)
    return(d_qresult)

def fquery(query):
    """
    Simple top level function that takes a query and uses default parameters
    to return a dictionary of related terms sorted by relevance.
    It uses the top 50 results returned by the elasticsearch search.  
    The query is treated as a Boolean conjunction (all terms must match).
    Results are ACT classified and returned in relevance order.  df_factor 
    of 1 means simple tf*idf weighting without adding bias.
    """

    # use query length to determine if query should be conjunctive or
    # disjunctive
    boolean_op = "and"
    query_length = len(query.split(" "))
    if len > 3:
        boolean_op = "or"
    d_qresult = pquery(query, 50, boolean_op, "r", 1)
    return(d_qresult)

# NOTE:  Since we cannot use shelve, we build a dictionary d_ti
# of term_info records on the fly when this module is imported.  The d_ti
# data is used compute tfidf weights from term vectors of 
# documents matching a query.
# We will read in doc freq, act category, and corpus size (# docs)

d_ti = run_make_term_dict("sp3", "ta", "9999")
CORPUS_SIZE = d_ti["|corpus_size|"].df
print "corpus size: %i" % CORPUS_SIZE
