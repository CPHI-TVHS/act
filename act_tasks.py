# -*- coding: utf-8 -*-

"""
act_tasks.py computes potential technology, technique, and method terms, based
on those head words.  The penultimate term in a phrase containing one of those
head words should itself be a nominal term (not an adjective) in order for the 
subphrase (phrase with head removed) to qualify as a ttm term.  We will also
put a minimal document frequency constraint on the penultimate term to better
ensure that it is a reasonable term to head a phrase.

Terms in the .term file require some normalization to deal with ' and \/.
We will remove the space before a ' and replace \/ with /.

We will use the normalized .term file to create 
(1) a dict d_head2cfreq of head terms and their corpus frequency
(2) a dict of d_task2cfreq of task phrases (without their heads) and 
the corpus frequency of their penultimate head.

"""

import sys
import pdb
import act_pnames
import codecs
from collections import defaultdict
from sets import Set

min_cfreq = 10

# set of phrases that could be tasks based on their head word and penultimate head frequency.
task_set = Set([])
tech_set = Set([])

# map of head terms to corpus frequency
# sum of corpus frequency of all phrases ending in a term
d_head2cfreq = defaultdict(int)

# task is phrase without its head.  cfreq is the corpus freq of the
# penultimate term in the original phrase (ie. the head term of the subphrase).
d_task2cfreq = defaultdict(int)

# head words for subphrases likely to be tasks
# !!! other words to consider: algorithm, strategy,  scheme
task_heads = ["method", "technique", "process", "methodology", "task"]
tech_heads = [ "technology" ]

def run_tasks(corpus_root, corpus, sections, classifier_type, context_type, year):
    print "[act_tasks.py]Starting run_tasks"
    sections_path = act_pnames.sections_root(corpus_root, corpus, sections)
    terms_path = sections_path + "/" + year + ".terms"
    tasks_path  = sections_path + "/" + year + ".tasks"
    tech_path  = sections_path + "/" + year + ".tech"

    s_terms = codecs.open(terms_path, encoding='utf-8')

    for line in s_terms:
        line = line.strip()
        l_fields = line.split("\t")
        term = l_fields[0]

        # fix " '" and "\/" 
        term = term.replace(" '", "'")
        term = term.replace("\\", "")
        
        l_term = term.split(" ")
        head = l_term[-1]
        cfreq = int(l_fields[2])

        # increment the corpus freq of the head term
        d_head2cfreq[head] = d_head2cfreq[head] + cfreq
        
        # If the phrase ends in a task_head, add the subphrase to the set of
        # candidate tasks.

        if head in task_heads:
            task = " ".join(term.split(" ")[:-1])
            task_set.add(task)

        if head in tech_heads:
            tech = " ".join(term.split(" ")[:-1])
            tech_set.add(task)

    s_terms.close()

    # Determine candidate tasks based on min freq of new head term
    # This is mainly to avoid calling adjectival subphrases nouns.
    # We assume adjectives will rarely show up as a head term.
    s_tasks = codecs.open(tasks_path, "w", encoding='utf-8')
    for task in task_set:
        l_term = task.split(" ")
        if len(l_term) > 1: 
            head_cfreq = d_head2cfreq[task.split(" ")[-1]]
            if head_cfreq >= min_cfreq:
                s_tasks.write("%s\t%i\n" % (task, head_cfreq))

    s_tasks.close()

    s_tech = codecs.open(tech_path, "w", encoding='utf-8')
    for tech in tech_set:
        l_term = tech.split(" ")
        if len(l_term) > 1: 
            head_cfreq = d_head2cfreq[tech.split(" ")[-1]]
            if head_cfreq >= min_cfreq:
                s_tech.write("%s\t%i\n" % (tech, head_cfreq))

    s_tech.close()


# python2.7 act_tasks.py "/home/j/anick/tw/roles/data/corpora" "sp3" "ta" "NB" "woc" "9999"

if __name__ == "__main__":
    args = sys.argv
    corpus_root = args[1]
    corpus = args[2]
    sections = args[3]
    classifier_type = args[4]
    context_type = args[5]
    year = args[6]
    
    run_tasks(corpus_root, corpus, sections, classifier_type, context_type, year)
    
# python2.7 act_tasks.py /home/j/anick/tw/roles/data/corpora sp3 ta NB woc 9999
