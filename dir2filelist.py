import os, fnmatch
 

def dir2filelist(inDir):
    """ Given a directory, return a list of all files below it in directory tree. """

    pattern = '*'
    fileList = []
 
    # Walk through directory
    for dName, sdName, fList in os.walk(inDir):
        for fileName in fList:
            if fnmatch.fnmatch(fileName, pattern): # Match search string
                fileList.append(os.path.join(dName, fileName))
    return(fileList)

