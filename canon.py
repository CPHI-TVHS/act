# -*- coding: utf-8 -*-
# canon.py
# routines for canonicalizing English phrases
# using dictionary lemmatization (based on 55k lexicon.tcl)
# for unknown nouns: inflect.py package (debugged by PGA)
# original version was from https://pypi.python.org/pypi/inflect
# PGA made some corrections

# for unknown verbs: nltk porter stemmer
import sys
import pdb
from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()

import re
import inflect
ie = inflect.engine()

lexicon_file = "lexicon.tcl"

class Canon():

    def __init__(self):
        self.d_lex = {}
        # keep a dict mapping head nouns to their canonical form
        # this is needed to regenerate surface forms for canonicalized noun phrases 
        self.d_n2canon = {}

        self.process_lexicon(lexicon_file)

    def process_lexicon(self, lexicon_file):
        # lexicon should be loaded before creating chart instances
        s_lex = open(lexicon_file, "r")
        for line in s_lex:
            line = line.strip("\n")
            line = line.strip(" ")
            (surface, lemma, pos, pos_detailed, paradigm_info) = line.split(" ")
            # key is pos <underscore> surface form
            # pos: verb, noun, conjunction, preposition, adjective, adverb
            key = pos + "_" + surface
            self.d_lex[key] = lemma
        s_lex.close()

    # return lemma for nouns and verbs; lowercased surface for all other pos.
    def get_lemma(self, surface, stanford_pos):
        # create the dict key from surface and stanford_pos
        first_char = stanford_pos[0]
        pos = ""
        surface = surface.lower()
        if first_char == "V":
            pos = "verb"
        elif first_char == "N":
            pos = "noun"
        key = pos + "_" + surface
        if self.d_lex.has_key(key):
            lemma = self.d_lex.get(key)
        else:
            lemma = None
        return(lemma)

    # reduce a noun to its singular by stemming only
    def stem_noun(self, word):
        #print "word: %s" % word
        cword = ie.singular_noun(word)
        if cword:
            return(cword)
        else:
            return(word)

    # canonicalize the head word of an NP
    # assume NP is aleady split into a list of words
    # get_canon_l_npr(["my", "running", "men"])
    def get_canon_l_np(self, l_np):
        head = l_np[-1] 
        lemma = self.get_lemma(head, "N")
        canon_head = ""
        if lemma != None:
            canon_head = lemma

        else:
            canon_head = head

        """
        Removed the defaulting to stemming.
        If the head word is unknown, do not canonicalize at all, since
        it could be a proper noun or part of a name.

        else:
            # use the inflect.py stemmer
            canon_head = self.stem_noun(head)
        """

    

        if canon_head != head:
            l_np[-1] = canon_head
        #pdb.set_trace()

        # add the canonical entry to the dictionary mapping surface to canonical nouns
        if head not in self.d_n2canon:
            self.d_n2canon[head] = canon_head

        return(l_np)

    def get_canon_v(self, head):
        lemma = self.get_lemma(head, "V")
        canon_head = head
        if lemma != None:
            canon_head = lemma
        else:
            # do stemming for unknown verbs using NLTK porter stemmer
            canon_head = porter_stemmer.stem(head)

        return(canon_head)

    # defaults to stemming if noun is not in lexicon
    def get_canon_n(self, head):
        lemma = self.get_lemma(head, "N")
        canon_head = ""
        if lemma != None:
            canon_head = lemma
        else:
            # use the inflect.py stemmer
            canon_head = self.stem_noun(head)
        return(canon_head)

    # noun as object of prep
    # get_canon_l_npr(["men",  "at"])
    # get_canon_l_npr(["dialysis",  "in"])
    def get_canon_l_npr(self, l_npr):
        head = l_npr[0] 
        canon_head = self.get_canon_n(head)

        if canon_head != head:
            l_npr[0] = canon_head

        return(l_npr)

    # verb followed by prep
    # get_canon_l_npr(["running",  "at"])
    def get_canon_l_vp(self, l_vp):
        head = l_vp[0] 

        canon_head = self.get_canon_v(head)
        
        #replace the head in the phrase if canonical form is different
        if canon_head != head:
            l_vp[0] = canon_head

        return(l_vp)

    # noun or noun phrase
    def get_canon_np(self, np):
        l_np = np.split(" ")
        return(" ".join(self.get_canon_l_np(l_np)))

    # verb or verb followed by preposition
    def get_canon_vp(self, vp):
        l_vp = vp.split(" ")
        return(" ".join(self.get_canon_l_vp(l_vp)))

    # noun as object of preposition
    def get_canon_npr(self, npr):
        l_npr = npr.split(" ")
        return(" ".join(self.get_canon_l_npr(l_npr)))

    """
    canonicalize the head term of features of the form 
    prev_VNP=disclosed_in|application|by
    prev_V=uniting_without
    prev_Npr=controllers_for
    last_word=programs
    last_word
    prev_J
    prev_Jpr
    prev_Npr
    prev_V
    prev_VNP
    """
    # features contain type=value.
    def get_canon_feature(self, feat):
        (feat_type, value) = feat.split("=")
        #pdb.set_trace()
        
        # sometimes the porter stemmer generates an error:
        # UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 9: ordinal not in range(128)
        try:
            if feat_type[0:6] == "prev_V":
                # handle the optional separator "_"
                l_value = value.split("_")
                verb = self.get_canon_v(l_value[0])
                l_value[0] = verb
                return(feat_type + "=" + "_".join(l_value))
            elif feat_type in ( "prev_N", "prev_Npr", "last_word"):
                # handle the optional separator "_"
                l_value = value.split("_")
                noun = self.get_canon_n(l_value[0])
                l_value[0] = noun
                return(feat_type + "=" + "_".join(l_value))
            else:
                return(feat)
        except:
            # return feat unchanged
            return(feat)

# noise detection
# note the need for ur and flags in order for the regex to match unicode characters!
re_noise_phrase = re.compile(ur'[\,\+\=\.\:\\\\′\®\±\%\═\≅\>\>\<\≡\≡\″\≡\→\°]', flags=re.UNICODE)

# bibliography names, e.g. "nestle f o"
re_bib_name = re.compile('[a-z]+ [a-z] [a-z]')

# journal name
re_journal_name = re.compile('j[ .][a-z.]+')

# if these words appear in a phrase, we reject the phrase as
# incomplete or inappropriate for bracketing analysis
# u'\u2212' is a type of dash found in doc US20040248097A1  (year 2000 biomed patents)

illegal_words = set([u'\u2212', u'\u2032', u'\u2550', "−", "-", "'s", "'", "′", "%", "co", "et", "much", "millimeter", "milliliter", "mm", "ml", "mg", "kg", "kl", "km", "hr", "μl", "μg", "ng", "μm", "ul", "tm", "am", "pm", "example", "centimeter", "mcg\/liter", "milligram", "liter", "m2\/g", "kcal", "ml\/g", "p\/p", "m2\/g", "mcg\/liter", "lu\/ml", "moles\/l", "g\/l", "w\/cm2", "units\/ml", "w\/v", "w\/w", "g\/ml", "u\/ml", "mol\/kg", "regions\/cm2", "cm2\/cm2", "mmoles\/l", "g\/liter", "\*", "mol\/l", "micromole\/gram", "mg\/g", "mg\/l", "mg\/2", "g\/kg", "kg\/h", "pmole\/cm2", "weight\/weight", "iu\/g", "iu\/ml", "grams\/day", "μmole" ])

max_legal_word_len = 30
def illegal_word_len_p(phr, max_len=max_legal_word_len):

    for word in phr.split(" "):
        if len(word) > max_len:
            return(True)
    return(False)

# return True if phr contains illegal punc or a word
# matching an illegal word
def illegal_phrase_p(phr):
    # use debugging here to catch illegal words/characters
    #if phr.find("nestle") >= 0:
    #    pdb.set_trace()
    # first character of phrase should be alpha
    if not phr[0].isalpha():
        return(True)
    if illegal_word_len_p(phr):
        return(True)

    illegal_punc_p = bool(re_noise_phrase.search(phr)) or bool(re_bib_name.search(phr)) or bool(re_journal_name.search(phr))
    if illegal_punc_p:
        return(True)
    l_words = phr.split(" ")

    if list(illegal_words & set(l_words)) == []:
        return(False)
    else:
        return(True)
            
    
# A feature should be in the form name=value
# Check that 1 and only one equal sign occurs in the string       
# ie. "=" should split a feature into exactly two parts
def illegal_feature_p(feature):
    if len(feature.split("=")) != 2:
        return(True)
    else:
        return(False)


if __name__ == "__main__":
    try:
        # which field is to be filtered?
        filtered_field_idx = sys.argv[1] - 1
    except:
        # if not specified as an argument, select 0 (first tab separated field)
        filtered_field_idx = 0
 
    for line in sys.stdin:
        line = line.strip()
        l_line = line.split("\t")
        term = l_line[filtered_field_idx]
        if not illegal_phrase_p(term):
            print line


