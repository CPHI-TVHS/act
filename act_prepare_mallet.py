# Prepare training input for Mallet from .tf and .tcs files (either act or pn).

# NOTE: May not work for Chinese because of file i/o

import act_pnames
import roles_config
import mallet_config

# location of mallet scripts
MALLET_DIR = mallet_config.MALLET_DIR

# For ACT classification
def prepare_train(corpus_root, corpus, sections, year, cat_type, subset):
    tf_file = act_pnames.tv_filepath(corpus_root, corpus, sections, year, "tf", subset, "")
    seed_file= act_pnames.tv_filepath(corpus_root, corpus, sections, year, "tcs", subset, cat_type)
    
    #s_tf = open(tf_file)
    tf_lines = open(tf_file, 'r').readlines()
    print "[prepare_train]opening .tf file: %s " % tf_file
    s_tcs = open(seed_file)
    print "[prepare_train]opening .tcs (seed)file: %s" % seed_file

    termDict = {}

    for line in s_tcs:
        fields = line.split('\t')
        # replace spaces with "_" in terms since mallet parser uses spaces as separators
        term = '_'.join(fields[0].split())
        ##print term
        # A term has a label and a list of features
        termDict[term] = [fields[1], []]

    print "[prepare_train]Done creating term dictionary"
    print "[prepare_train]Building feature dictionary..."


    count1 = 0
    sortedKeys = sorted(termDict.keys())
    
    for line in tf_lines:
        if count1 % 100000 == 0:
            print count1
        count1 = count1 + 1
        fields = line.split('\t')
        term = '_'.join(fields[0].split())
        ##print term
        feat_val = (fields[1], fields[2])
        if termDict.has_key(term):
            termDict[term][1].append(feat_val)

    print "Finished building feature dictionary!"
    print "Writing to file..."
    #s_tf.close()
    s_tcs.close()
    
    mallet_in_file = act_pnames.tv_filepath(corpus_root, corpus, sections, year, "train", subset, cat_type)
    s_mallet_in = open(mallet_in_file, 'w')
    
    for term in termDict.keys():
        s_mallet_in.write(term+'\t'+termDict[term][0]+'\t')
        if len(termDict[term][1]) == 0:
            print "No features to term! Oh no!!!!"
        for f_v in termDict[term][1]:
            s_mallet_in.write(f_v[0]+":"+f_v[1])
            s_mallet_in.write(" ")
        s_mallet_in.write("\n")

    print "Created mallet_in file in directory!"

    # create mallet vectors file from .train data
    #/home/j/corpuswork/fuse/code/patent-classifier/tools/mallet/mallet-2.0.7/bin/csv2vectors --input myInput.train --output myInput.vectors

    # create classifier from .vectors
    # /home/j/corpuswork/fuse/code/patent-classifier/tools/mallet/mallet-2.0.7/bin/vectors2classify --input myInput.vectors --training-portion 0.9 --trainer NaiveBayes --output-classifier <file>.NBclassifier > <file>.mallet_stats

    s_mallet_in.close()
    
def run_prepare_train(corpus_root, corpus, sections, start_range, end_range, cat_type, subset):

    for int_year in range(start_range, end_range):
        year = str(int_year)
        print "[run_my_func]Processing dir: %s" % year
        prepare_train(corpus_root, corpus, sections, year, cat_type, subset)
        print "[run_my_func]Completed: %s.tc" % (year)


def run_prepare_classify(corpus_root, corpus, sections, start_range, end_range, cat_type, subset):

    for int_year in range(start_range, end_range):
        year = str(int_year)
        print "[run_prepare_classify]Processing dir: %s" % year
        prepare_classify(corpus_root, corpus, sections, year, cat_type, subset)
        print "[run_prepare_classify]Completed: %s.tc" % (year)


# NOTE: polarity classification has not been updated with sections arg for use with act_tole.py!
# For polarity classification
# Create a.tf file to be used later for training and classification of features classified as
# attributes in the ACT classification.
# Input: .tf file AND mallet classification output (.results) to check if "a".

def prepare_a_tf(corpus_root, corpus, year, mallet_act_results):

    tf_file = act_pnames.tv_filepath(corpus_root, corpus, sections, year, "tf", "", "")
    # subset and cat_type are fixed as "a" and "pn"
    a_tf_file = act_pnames.tv_filepath(corpus_root, corpus, sections, year, "tf", "a", "pn")
    res_lines = open(mallet_act_results, 'r').readlines()
    tf_lines = open(tf_file, 'r').readlines()
    s_a_tf = open(a_tf_file, 'w')

    attDict = {}

    print "building attributes dict..."
    for i in range(0, len(res_lines)):
        fields = res_lines[i].split()
        tuples = [('c',float(fields[2])), ('t',float(fields[4])), ('a',float(fields[6]))]
        num_tuples = [e[1] for e in tuples]
        max_list = [e[0] for e in tuples if e[1] == max(num_tuples)]
        if 'a' in max_list:
            attDict[fields[0]] = 1            
    count = 0
    #sortedKeys = sorted(attDict.keys())
    for line in tf_lines:

        count+=1
        if count % 100000 == 0:
            print count
        term = '_'.join(line.split('\t')[0].split())
        if term in attDict:
            s_a_tf.write(line)

    s_a_tf.close()


# Create Mallet classification input from .tf file

# subset parameter should be "" for ACT classification, "a" for Polarity classification
# cat_type is act or pn
def prepare_classify(corpus_root, corpus, sections, year, cat_type, subset):

    tf_file = act_pnames.tv_filepath(corpus_root, corpus, sections, year, "tf", subset, "")
    print "[prepare_classify]Preparing to open the .tf file: %s" % tf_file
    tf_lines = open(tf_file).readlines()
    print "[prepare_classify]Finished uploading .tf file!"
   

    termDict = {}

    print "Creating term dict..."

    count1 = 0

    for line in tf_lines:
        if count1 % 100000 == 0:
            print count1
        count1 += 1
        fields = line.split('\t')
        term = '_'.join(fields[0].split())
        feature = fields[1]
        count = fields[2]
        fc = feature+":"+count
        if term in termDict:
            termDict[term].append(fc)
        else:
            termDict[term] = [fc]
    
    class_input_file = act_pnames.tv_filepath(corpus_root, corpus, sections, year, "unlab", subset, cat_type)
    print "class_input_file: %s" % class_input_file
    class_input = open(class_input_file, 'w')

    print "Writing into file..."
    print "Len of dict is"+ str(len(termDict))

    for term in termDict:
        features = ' '.join(termDict[term])
        class_input.write(term+'\t'+features+'\n')

    class_input.close()

    # /home/j/corpuswork/fuse/code/patent-classifier/tools/mallet/mallet-2.0.7/bin/csv2classify --input classification.input --output NB.results --classifier NB.classifier
