import os, fnmatch
import pdb 

def dir2filelist(inDir):
    """ Given a directory, return a list of all files below it in directory tree. """

    # limit the filenames returned to those stored as <name>.xml.gz
    file_pattern = '*.xml.gz'
    # limit the directory path to the d3_feats subdirectories
    dir_pattern = '*d3_feats*'
    fileList = []
 
    # Walk through directory
    for dName, sdName, fList in os.walk(inDir):

        for fileName in fList:
            # Limit matches to those in d3_feats subdir and matching .xml.gz
            if fnmatch.fnmatch(dName, dir_pattern) and fnmatch.fnmatch(fileName, file_pattern): 
                #pdb.set_trace()                
                fileList.append(os.path.join(dName, fileName))
    return(fileList)

