#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import json
import logging
import unittest
import random
from lib.nlp_to_xml import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_NLPToXML(unittest.TestCase):

    def setUp(self):
		
        # set attributes.
        self.n2x = NLPToXML()
       
    
    def test__authorities(self):
        """ Does the authority splitter work for and NER tag with an authority? """
        
        # combine and then split authority and NER tag.
        auth_in, tag_in = "ncdcr.gov", "PII.email_address"
        auth_out, tag_out = self.n2x._split_authority("{}/{}".format(auth_in, tag_in))

        # check if result is as expected.
        self.assertTrue((auth_in, tag_in) == (auth_out, tag_out))


    def test__validation(self):
        """ Is the sample tagged XML snippet valid? """
        
        # validate XML.
        ner = [("Jane", "stanford.edu/PERSON", " "), ("Doe", "stanford.edu/PERSON", "")]
        xdoc = self.n2x.get_xml(ner)
        is_valid = self.n2x.validate_xml(xdoc)
        
        # check if result is as expected.
        self.assertTrue(is_valid)


# CLI TEST.
def main(CSV_NER="Jane,stanford.edu/PERSON,|Doe,stanford.edu/PERSON,"):
    
    "Prints tagged message version of CSV-style NER text (line ending = '|'). \
    \nexample: `py -3 test__nlp_to_xml.py 'Jane,PERSON, |Doe,PERSON,'`"

    # convert @CSV_NER to list of tuples.
    ner_data = [tuple(t.split(",")) for t in CSV_NER.split("|")]

    # convert @ner_data to XML.
    n2x = NLPToXML()
    xdoc = n2x.get_xml(ner_data)
    xdoc = etree.tostring(xdoc).decode()
    
    print(xdoc)


if __name__ == "__main__":
    
    import plac
    plac.call(main)

