import os
import pdb
import codecs
# mallet_config must set MALLET_DIR to the path to mallet bin
import mallet_config

MALLET = mallet_config.MALLET_DIR + "/./mallet"
VECTORS2INFO = mallet_config.MALLET_DIR + "/./vectors2info"

# Include the classification method as first in the file_name_prefix string!
# E.g. NB.rest.of.prefix or ME.rest.of.prefix
# features_to_include_file is taken into account only if num_infogain_features == 0

# Steps:
# 1. Create input for training and classification
# 2. Create vectors (Mallet's representation for the training set)
# 3. If num_infogain_features != 0 prune the vectors and update classification input
# 4. Train the classifier on the vectors
# 5. Classify the classification input and get .results file

def run_classify(tf_file, tcs_file, dir_path, file_name_prefix, feature_file_path=None, num_infogain_features=0, feat_info=False):
    # make sure dir_path has a slash at the end
    if dir_path[-1] != "/":
        dir_path = dir_path + "/"
    print("[run_mallet.py]starting run_mallet.run_classify\n dir_path: %s, file_name_prefix: %s\n" % (dir_path, file_name_prefix))
    #Vectors input and classification input
    #pdb.set_trace()
    create_input_for_mallet(tf_file, tcs_file, dir_path, file_name_prefix, feature_file_path, num_infogain_features, feat_info)
    #"""
    #Create vectors from vectors input
    create_vectors(dir_path, file_name_prefix, num_infogain_features)
    train_classifier(dir_path, file_name_prefix, num_infogain_features)
    if num_infogain_features != 0:
        filter_class_input_with_infogain_f(dir_path, file_name_prefix, feat_info)
    classify(dir_path, file_name_prefix)
    
    print "[run_mallet.py]Finished classifying " + file_name_prefix + " files in the directory " + dir_path + "\n\n"
    #"""

#-------------------------------------------------------------------------------------------------------------------------------------    
#Create two input files to Mallet's vectors creation call and classification call.
#Outputs ==>
#.train_input_svm file, each line is "label1 f1:v1 f2:v2 ..."
#.train_tcs_svm file, same as train_input_svm but including the term in col 1
#.class_input_svm file, each line is "term1 f1:v1 f2:v2 ..."
#Tab between label/term and f:v list, white space between elements of the f:v lists.
def create_input_for_mallet(tf_file, tcs_file, dir_path, file_name_prefix, features_to_include_file=None, num_infogain_features=0, feat_info=False):
    print("\n[run_mallet.py] starting run_mallet.create_input_for_mallet\ndir_path: %s, file_name_prefix: %s" % (dir_path, file_name_prefix))
    with open(tf_file,'r') as tf:
        tf_lines = tf.readlines()
    with open(tcs_file,'r') as tcs:
        tcs_lines = tcs.readlines()

    #Extract features only when not using the Mallet's infogain
    if num_infogain_features == 0:
        with open(features_to_include_file) as f_list:
            feature_set = list(f_list)
            feature_set = [f[:-1] for f in feature_set if f!="\n" and f[-1]=="\n"]
    else:
        feature_set = []

    #Initialize a dictionary for training terms in tcs (for training)
    tcsDict = {}
    for line in tcs_lines:
        fields = line.split('\t')
        # replace spaces with "_" in terms
        term = '_'.join(fields[0].split())
        #term:[label, []] where [] is for future features from tf
        tcsDict[term] = [fields[1], []]
        
    #Initialize a dictionary for all terms in tf (for classification)
    tfDict = {}
    
    #Accumulate features and counts from tf
    for line in tf_lines:
        fields = line.split('\t')
        # replace spaces with "_" in terms since mallet parser uses spaces as separators
        term = '_'.join(fields[0].split())
        feature = fields[1].strip()
        count = fields[2].strip()
        #pdb.set_trace()
        #print "line is: %s" % (line)
        #print "tf fields: %s %s %s" % (term, feature, count)
        #Skip bad features that cause bugs in Mallet
        if ':' in feature or '#' in feature or '<' in feature or '>' in feature:
            continue
        #Skip features that are not in feature_set
        if num_infogain_features == 0 and feature not in feature_set:
            if term in tfDict:
                tfDict[term][1].append(feature+":"+count)
            else:
                tfDict[term] = [[],[feature+":"+count]]
            continue
        #Add feature:count to the term's list in tcsDict
        if term in tcsDict:
            tcsDict[term][1].append(feature+":"+count)
        #Add feature:count to the term's list in tfDict
        if term in tfDict:
            tfDict[term][0].append(feature+":"+count)
        else:
            tfDict[term] = [[feature+":"+count],[]]
    
    train_input_file = open(dir_path + file_name_prefix + ".train_input_svm", 'w')
    train_tcs_file = open(dir_path + file_name_prefix + ".train_tcs_svm", 'w')
    class_input_file = open(dir_path + file_name_prefix + ".class_input_svm", 'w')
    if feat_info == True and num_infogain_features == 0:
        feat_info_file = open(dir_path + file_name_prefix + ".feat_info", 'w')
    
    for term in tcsDict:
        #Ignore terms without features (such exist only when feature_set!=[])
        if len(tcsDict[term][1]) == 0:
            continue

        train_input_file.write(tcsDict[term][0]+'\t')
        train_tcs_file.write(term + '\t' + tcsDict[term][0] + '\t')
        for f_v in tcsDict[term][1]:
            train_input_file.write(f_v)
            train_input_file.write(" ")
            train_tcs_file.write(f_v)
            train_tcs_file.write(" ")
        train_input_file.write("\n")
        train_tcs_file.write("\n")
        
    for term in tfDict:
        fv_lists = tfDict[term]
        polar_fv_list = ' '.join(fv_lists[0])
        
        
        #Compute (polar) feat-count and polar-ratio
        if feat_info == True and num_infogain_features == 0:
            polar_feat_count = sum([int(e.split(":")[1]) for e in fv_lists[0]])
            npolar_feat_count = sum([int(e.split(":")[1]) for e in fv_lists[1]])
            feat_count = polar_feat_count + npolar_feat_count
            polar_ratio = polar_feat_count/float(feat_count)
            npolar_fv_list = ' '.join(fv_lists[1])
            feat_info_file.write(term+'\t'+str(feat_count)+'\t'+str(polar_feat_count)+'\t'+str(polar_ratio)+'\t'+polar_fv_list+'\t'+npolar_fv_list+'\n')
	
	if len(fv_lists[0]) == 0:
		continue
	else:
		class_input_file.write(term+'\t'+polar_fv_list+'\n')
        
        
    
    train_input_file.close()
    train_tcs_file.close()
    class_input_file.close()
    if feat_info == True and num_infogain_features == 0:
        feat_info_file.close()
    


#Use .train_input_svm file to build Mallet's vectors.
#If num_infogain_features != 0, vectors are pruned by infogain with N = num_infogain_features
def create_vectors(dir_path, file_name_prefix, num_infogain_features):
    print("\n[run_mallet.py]starting run_mallet.create_vectors\ndir_path: %s, file_name_prefix: %s, num_infogain_features: %i" % (dir_path, file_name_prefix, num_infogain_features))
    import_svmlight_call = os.system(MALLET + " import-svmlight --input " + dir_path + file_name_prefix + ".train_input_svm --output " + dir_path + file_name_prefix + ".train.vectors")
    if import_svmlight_call != 0:
        print "[run_mallet.py]Could not create vectors file in directory."
        exit()
    #Create a pruned vectors file when using infogain
    if num_infogain_features != 0:
        prune_call = os.system(MALLET + " prune --input " + dir_path + file_name_prefix + ".train.vectors --prune-infogain " + str(num_infogain_features) + " --output " + dir_path + file_name_prefix + ".pruned.train.vectors")
        if prune_call != 0:
            print "[run_mallet.py]Could not create pruned vectors file in directory."
            exit()


#Use .train.vectors file to train the classifier
def train_classifier(dir_path, file_name_prefix, num_infogain_features):
    print "[run_mallet.py]Starting run_mallet.train_classifier"
    #First element of file_name_prefix is always the classification algorithm
    algorithm = file_name_prefix.split(".")[0]
    if algorithm=="NB":
        trainer = "NaiveBayes"
    elif algorithm=="ME":
        trainer = "MaxEnt"
    else:
        print "[run_mallet.py train_classifier]Unknown trainer name.  Prefix of file (%s) should be NB or ME." % file_name_prefix

    #Look for pruned vectors if num_infogain_features != 0
    if num_infogain_features != 0:
	 vectors_prefix = file_name_prefix + ".pruned"
    else:
	 vectors_prefix = file_name_prefix

    train_classifier_call = os.system(MALLET + " train-classifier --input "+dir_path+vectors_prefix+".train.vectors --trainer " + trainer + " --output-classifier "+dir_path+file_name_prefix+".classifier")
    if train_classifier_call !=0:
        print "[run_mallet.py]Could not train classifier."
        exit()

#Filter the .class_input_svm file according to the features pruned by Mallet.
#It is called only after the vectors creations and if num_infogain_features != 0
def filter_class_input_with_infogain_f(dir_path, file_name_prefix, feat_info=False):
    print "[run_mallet.py]Starting run_mallet.filter_class_input_with_infogain_f"
    vec2info_call = os.system(VECTORS2INFO + " --input " + dir_path + file_name_prefix + ".pruned.train.vectors --print-features > " + dir_path + file_name_prefix + ".infogain_features")
    if vec2info_call != 0:
        print "[run_mallet.py]Could not extract features from pruned vectors."
        exit()
    with open(dir_path + file_name_prefix + ".infogain_features",'r') as f_list:
        feature_set = list(f_list)
        feature_set = [f[:-1] for f in feature_set if f!="\n" and f[-1]=="\n"]
        featureDict = dict.fromkeys(feature_set)
    with open(dir_path+file_name_prefix+".class_input_svm",'r') as c_input:
        lines = c_input.readlines()

    #Overwrite the old class_input_svm file (closed automatically in the "with" block above)   
    class_input_file = open(dir_path + file_name_prefix +".class_input_svm",'w')
    if feat_info==True:
	feat_info_file = open(dir_path + file_name_prefix + ".feat_info", 'w')

    #Leave only the features after pruning, erase terms without features after filtering
    for line in lines:
        fields = line.split('\t')
        term = fields[0]
        # polar_feat is a misnomer.  It refers to features in the featureDict that are in
        # the top n of the infogain rank.
        polar_feat = []
        polar_feat_count = 0
        # non polar feat (features ignored due to low infogain rank)
        npolar_feat = []
        npolar_feat_count = 0
        for f_v in fields[1].split():
            feat = f_v.split(":")[0]
            if feat in featureDict:
                polar_feat.append(f_v)
                polar_feat_count += 1
            else:
                npolar_feat.append(f_v)
                polar_feat_count += 1

        #Compute (polar) feat-count and polar-ratio

        # create a blank separated string of usable features for a term
        polar_fv_list = ' '.join(polar_feat)
	
        if feat_info == True:
            """
            # buggy
            if polar_feat != []:
                polar_feat_count = sum([int(e.split(":")[1]) for e in polar_feat])
            else:
                polar_feat_count = 0
            if npolar_feat != []:
                npolar_feat_count = sum([int(e.split(":")[1]) for e in npolar_feat])
            else:
                npolar_feat_count = 0
            """

            feat_count = polar_feat_count + npolar_feat_count
            
            polar_ratio = polar_feat_count/float(feat_count)
            npolar_fv_list = ' '.join(npolar_feat)
	    #polar_fv_list = ' '.join(polar_feat)	
            feat_info_file.write(term+'\t'+str(feat_count)+'\t'+str(polar_feat_count)+'\t'+str(polar_ratio)+'\t'+polar_fv_list+'\t'+npolar_fv_list+'\n')

	if polar_feat == []:
            continue
        # if the term has usable features, output a line for the term
        class_input_file.write(term+'\t')
        class_input_file.write(polar_fv_list)
        class_input_file.write('\n')
        
    class_input_file.close()
    if feat_info == True:
        feat_info_file.close()


#Classify using the created classifier and .class_input_svm file

def classify(dir_path, file_name_prefix):
    print "[run_mallet.py]starting run_mallet.classify"
    classify_svmlight_call = os.system(MALLET + " classify-svmlight --input " + dir_path + file_name_prefix + ".class_input_svm --output " + dir_path + file_name_prefix + ".results --classifier " + dir_path + file_name_prefix + ".classifier")
    if classify_svmlight_call != 0:
        print "[run_mallet.py]Classification call failed."
        exit()
    # Also sort the result classes into the .classes file
    print "[run_mallet.py]starting run_mallet.sort_result_classes"
    sort_result_classes(dir_path, file_name_prefix)
    print "[run_mallet.py]Completed writing class assignments to .classes file"

# Python code to sort tuples using second element 
# of sublist In place way to sort using sort()
def sort_by2(sub_li, reverse=True):
 
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of 
    # sublist lambda has been used
    sub_li.sort(key = lambda x: x[1], reverse=reverse)
    return sub_li

# takes a list with even number of items 
#(class_str, float_str, class_str, float_str) 
# and returns a list of pairs [ [string, float], [string, float], ...] 
def list2paired_list(l_unpaired):
    l_paired = []
    it = iter(l_unpaired)
    # zip returns a tuple with nth elements of iterators paired.
    # In this case, we are pairing sequential output of the same iterator
    for mclass, score in zip(it, it):
        l_paired.append((mclass, float(score)))
    # now we want to sort the list by score from highest to lowest.
    return(sort_by2(l_paired, True) )
    

# run_mallet.sort_result_classes("/home/j/anick/tw/roles/data/corpora/SignalProcessing/data/tv/", "NB.IG50.SignalProcessing.woc.9999.5")
# 4/29/18 order the classes in .results by mallet scores
def sort_result_classes(dir_path, file_name_prefix):
    results_file = dir_path + file_name_prefix + ".results"
    results_classes_file = results_file + ".classes"
    s_results = codecs.open(results_file, encoding='utf-8')
    s_results_classes = codecs.open(results_classes_file, "w", encoding='utf-8')

    for line in s_results:
        # create a list of pairs of [class score]
        line = line.strip()
        fields = line.split("\t")
        term = fields[0]
        # get sorted list of (class, score) pairs
        plist = list2paired_list(fields[1:])
        top_class = plist[0][0]
        s_results_classes.write("%s\t%s\t%s\n" % (term, top_class, plist)) 

    s_results.close()
    s_results_classes.close()




"""
Instead of running from this file, open python2.7 and run routines defined in pa_runs.py.  This keeps a record of past runs, input
and output.

curr_tf_file = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/tv/2002.a.tf.f1.unigram.mtf.doc_all.no0"
curr_tcs_file = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/tv/doc_all/2002.a.tf.f1.unigram.mtf.ssi.1.0.2.tcs"
pr_feat_file_25 = "/home/j/anick/patent-classifier/ontology/roles/data/patents/ln-us-14-health/data/tv/doc_all/2002.bigram.f.diff.k5.pn.25"
run_classify(curr_tf_file, curr_tcs_file, "/home/j/llc/gititkeh/malletex/health_data/script_test/infogain_50/", "NB.IG50.ssi.uni.try", num_infogain_features=50, feat_info=True)

"""
