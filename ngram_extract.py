"""
ngram_extract.py
Input: d3_feats file
Output:
3   nucleic acid immunization       nucleic acid immunizations      US20040234539A1 JJ NN NNS

"""

# gunzip -c US5579518A.xml.gz | python2.7 ngram_extract.py

import sys
import canon
import os
import gzopen
import dir2filelist
import re
import codecs

can = canon.Canon()


def file_base_name(file_name):
    """ Given a file name, return base filename without the extension(s).  """
    if '.' in file_name:
        separator_index = file_name.index('.')
        base_name = file_name[:separator_index]
        return base_name
    else:
        return file_name


def path_base_name(path):
    """ Given a full path, strip off path and extensions and return base file name. """
    file_name = os.path.basename(path)
    return file_base_name(file_name)

#def ngram_extract_from_file(infile, can, out_stream)

def file2ngram_info(infile, min_len, max_len):
    """ Given a d3_feats file, return a list of tab separated strings of the form:
    <ngram_length> <canonicalized term> <surface term> <doc_id> <pos_signature>
    e.g., 3       epitaxial silicon process       epitaxial silicon processes     000171485800006 JNN
    NOTE: All elements are returned as strings, including the <ngram_length>
    min_len and max_len constrain the length of ngrams to be included in output.
    """

    #print("[file2ngram_info] %s" % infile) ///
    s_infile = gzopen.gzopen(infile)
    # list of lists of info to be returned for each line of input file
    l_term_info = []
    for line in s_infile:
        line = line.strip("\n")
        l_fields = line.split("\t")
        filename = l_fields[0]
        doc_id = path_base_name(filename)
        term = l_fields[2]
        ngram_len = len(term.split(" "))

        # continue if conditions for the term are met (ngram length and filter check)
        if (ngram_len >= min_len) and (ngram_len <= max_len) and not(canon.illegal_phrase_p(term)) :

            canon_np = can.get_canon_np(term)
            # We assume that the last feature on the line is tag_sig!
            pos_sig = l_fields[-1]
            if pos_sig[:7] != "tag_sig":
                print ("[ngram_extract.py]Error: last feature on input line is not labeled tag_sig")
                print ("line: %s" % line)
                sys.exit()
            else:
                # replace pos_sig with a string made of the first char of each pos in the phrase
                # e.g. JJ_NN_NNS => JNN
                pos_sig = "".join(item[0] for item in pos_sig[8:].split("_"))

                prev_Npr = ""
                prev_N = ""
                # grab the prev_Npr feature, if there is one
                try:
                    # extract the value of the prev_Npr feature, if there is one.
                    match = re.search(r'prev_Npr=(\S+)	', line)
                    prev_Npr = match.group(1)
                    # canonicalize the noun
                    prev_N = can.get_canon_np(prev_Npr.split("_")[0])
                except:
                    pass

                l_term_info.append([str(ngram_len), canon_np, term, doc_id, pos_sig, prev_Npr, prev_N])

    s_infile.close()
    return(l_term_info)

def flist2_ngram_info(flist_file, outfile):
    """ flist_file is a file containing a list of pathnames of d3_feats files.
    outfile is pathname of file to which term_info lines are to be written
    """
    s_flist_file = open(flist_file, "r")
    for filename in s_flist_file:
        filename = filename.strip("\n")
        l_term_info = file2ngram_info
        print("\t".join(term_info))

    s_fl_file.close()

# python2.7 ngram_extract.py

"""
if __name__ == "__main__":
    dir = "/home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files/2002/000171/"
    filen = "000171485800006.xml.gz"
    infile = dir + filen
    l_term_info = file2ngram_info(infile)
    for term_info in l_term_info:
        print("\t".join(term_info))
        #print "%i\t%s\t%s\t%s\t%s" % (ngram_len, canon_np, term, doc_id, pos_sig)
"""

if __name__ == "__main__":
    #dir = "/home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files/2002/000171/"
    #filen = "000171485800006.xml.gz"
    #infile = dir + filen
    #inDir = "/home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files/2002/"
    #min_len = 2
    #max_len = 6

    args = sys.argv
    inDir = args[1]
    outfile = args[2]
    min_len = int(args[3])
    max_len = int(args[4])

    s_outfile = codecs.open(outfile, "w", encoding='utf-8')

    fl = dir2filelist.dir2filelist(inDir)
    for infile in fl:
        # stdout will be piped into ngrams.log file in output dir
        print("file: %s" % infile)
        l_term_info = file2ngram_info(infile, min_len, max_len)
        for term_info in l_term_info:
            outline = "\t".join(term_info)
            s_outfile.write("%s\n" % outline)

    s_outfile.close()
