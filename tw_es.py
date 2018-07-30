# -*- coding: utf-8 -*-

"""
tw_es.py 

Before using this module, please set the parameter in the line below identified as
### !!! APPLICATION DEPENDENT LINE

# example calls
# python2.7 tw_es.py "/home/j/anick/tw/roles/data/corpora" "uspto_mini" "tas" "2018" "uspto_mini"
# python2.7 tw_es.py "/home/j/anick/tw/roles/data/corpora" "sp3" "ta" "9999" "test1_index"

tw_es.py: Define an elasticsearch mapping and load the index for a database, which will be used for
finding related terms using elasticsearch in tw_query.py.  If the named index already exists,
it will be overwritten.

This module must be run on the machine (localhost) on which elasticsearch is running.

To create and populate index using bulk loading with a generator:
See example in https://github.com/elastic/elasticsearch-py/blob/master/example/load.py#L76-L130

Data is read from a tab separated csv file and converted into instances of the DocTerms class for
bulk loading.
The DocTerms ("document terms") class stores data about the first 500 terms found in a document,
It contains fields for:
 all terms (including duplicates) in the form of a single text blob (used for free text search of docs)
 a set of terms (without duplicates) as an array of keywords (used for keyword based search of docs)

NOTE: It appears that for the mapping to work,
the document type must be named "doc".  Whenever I gave the doc_type a different
name, I got an error.  I could not add a different doc_type in the meta section of the class definition.

TODO: make the index a parameter, so that we can create DocTerm objects connected to different indexes.
test1_index is built from the sp3/ta/9999.doc_terms data.

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
#import putils
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

### THE FOLLOWING LINE MUST BE MODIFIED TO CONTAIN YOUR INDEX NAME 
### This should be the same name that is passed in by run_tw_es.sh
# It is used in the meta class within DocType class definition.
# 
### e.g., 
###ES_INDEX_NAME = 'test1_index'
###ES_INDEX_NAME = 'uspto_mini'


# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Establish elasticsearch instance
es = Elasticsearch()

# Define analyzers
my_analyzer = analyzer('custom',
                       tokenizer='standard',
                       filter=['lowercase'])
# --- Add more analyzers here ---

# Define document mapping
# using example in https://github.com/elastic/elasticsearch-dsl-py/issues/600
class DocTerms(DocType):
    title = Keyword()
    text = Text(analyzer='simple')
    term = Keyword()
    # --- Add more fields here ---
    
    class Meta:
        ### !!! APPLICATION DEPENDENT LINE
        ### !!! This line defines which index you will be using to create your index
        ### It is also used by tw_query.py (called from the flask app tw_app.py) to 
        ### determine which index to query against.  So set this line to the correct
        ### index before starting tw_app.py
        index = 'test1_index'
        
        #/// index doc_type is defaulting to doc
        #doc_type = 'doc_terms'
        body = {
            'settings': {
                # just one shard, no replicas for testing
                'number_of_shards': 1,
                'number_of_replicas': 0
                }
            }

    ##def save(self, *args, **kwargs):
    ##    return super(DocTerms, self).save(*args, **kwargs)


# create a generator over the contents of a tab separated csv file
def docterms_document_stream(file_to_index, es_index_name):

    # type_name has to be "doc", it appears...
    type_name = "doc"
    with open(file_to_index, "rb") as csvfile:
        for row in csv.reader(csvfile, dialect='excel-tab'):
            yield {"_index": es_index_name,
                   "_type": type_name,
                   "_source": docterms_transform_row(row)
                   }

# row is a list of [doc_id {term}*]
# We will use the doc_id as the title.
def docterms_transform_row(row):
    title = row[0]
    # concatenate all terms into a text field
    terms_as_text = " ".join(row[1:])
    terms_as_keywords = row[1:]
    return( {"title": title,
             "text": terms_as_text,
             "term": terms_as_keywords
             }
            )

def main(es_index_name, file_to_index):
    """
    Build an elasticsearch index over the Docterms data using bulk load
    """
    start_time = time.time()
    #buildIndex()


    index = Index(es_index_name)
    print "[main]After index(es_index_name)"    

    if index.exists():
        index.delete()  # Overwrite any previous version

    #index.doc_type(DocTerms)
    index.doc_type(DocTerms)
    print "[main]After index.doc_type."

    #index.doc_type("doc_terms")
    index.create()

    print "[main]Created index."
    #exit()

    #docterms_create_index(es, es_index_name)
    stream = docterms_document_stream(file_to_index, es_index_name)
    print "[main]Calling bulk loader."
    helpers.bulk(es, stream)
    
    #for result in docterms_document_stream(file_to_index):
    #    print "result: %s" % (result)

    es.indices.refresh(index=es_index_name)
    print("[main]Built index in %s seconds ===" % (time.time() - start_time))


# example call
# python2.7 tw_es.py "/home/j/anick/tw/roles/data/corpora" "sp3" "ta" "9999" "test1_index"
        
if __name__ == '__main__':

    args = sys.argv
    corpus_root = args[1]
    corpus = args[2]
    sections = args[3]
    year = args[4]
    es_index_name = args[5]
    #es_index_name = "test1_index"   # doc_terms test
    # Construct the path for the csv file we will index (xxx.doc_terms)
    sections_path = act_pnames.sections_root(corpus_root, corpus, sections)
    file_to_index = sections_path + "/" + year + ".doc_terms"

    #file_to_index = "/home/j/anick/tw/roles/data/corpora/sp3/ta/9999.doc_terms"

    main(es_index_name, file_to_index)   


