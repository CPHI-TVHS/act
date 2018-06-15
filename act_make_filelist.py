
import os
import dir2filelist
import sys

"""
import canon
import gzopen
import re
import codecs

can = canon.Canon()
"""

# python2.7 act_make_filelist.py /home/j/corpuswork/techwatch/corpora/uspto/2018/ipa180104/data/d3_feats/01/files/0001 /home/j/anick/tw/roles/data/corpora sp 9999 
if __name__ == "__main__":
    #dir = "/home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files/2002/000171/"
    #filen = "000171485800006.xml.gz"
    #infile = dir + filen
    #inDir = "/home/j/corpuswork/techwatch/corpora/SignalProcessing/data/d3_feats/01/files/2002/"
    #min_len = 2
    #max_len = 6

    args = sys.argv
    in_path = args[1]
    corpus_root = args[2]
    corpus_name = args[3]
    year = args[4]
    # out_file mode default to "w"
    if len(args) > 5:
        mode = args[5]
    else:
        mode = "w"

    out_path = "/".join([corpus_root, corpus_name, "filelists"])
    year_filename = year + ".files"
    out_file = "/".join([out_path, year_filename])

    print("[act_make_filelist.py]creating path: %s,\nwriting to %s" % (out_path, out_file))
 
    try:
        # create directory path for corpus, if it does not aleady exist
        os.makedirs(out_path)
    except:
        print("[act_make_filelist.py]Path already exists (or cannot be created).")


        
    # create a file (<year>.files) containing a list of fully specified source (.xml.gz) files 
    # In most cases, open the out_file as a new file.  But the "a" mode allows for appending more
    # filenames into an existing file.

    s_out_file = open(out_file, mode)

    fl = dir2filelist.dir2filelist(in_path)
    file_count = 0
    for infile in fl:
        # write out file path
        s_out_file.write("%s\n" % infile)
        file_count += 1
    s_out_file.close()

    print("[act_make_filelist.py]Wrote %i files into %s." % (file_count, out_file))
