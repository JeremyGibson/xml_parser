#!/usr/bin/env python3

"""
This module converts Stanford CoreNLP JSON output to XML per the ./tagged_content.xsd schema.
"""

# import modules.
import codecs
import json
from lxml import etree

class JsonToXML():
    """ """

    def __init__(self):
        self.custom_ner = ["PII.email_address"]


    def xml(self, jdoc, is_raw=False, charset="utf-8"):

        # if @is_raw == False, read JSON file.
        if not is_raw:
            with codecs.open(jdoc, "r", encoding=charset) as tmp:
                jdoc = tmp.read()

        # load JSON.
        jsml = json.loads(jdoc)
        
        # create XML namespace.
        ns_url = "http://archives.ncdcr.gov/mail-account/tagged-content/"
        ns_prefix = "{" + ns_url + "}"
        ns_map = {None : ns_url}

        # create root element.
        x_tokens = etree.Element(ns_prefix + "tokens", nsmap=ns_map)
        
        # parse JSON; write XML.
        j_sentences = jsml["sentences"]
        for j_sentence in j_sentences:
        
            j_tokens = j_sentence["tokens"]
            for j_token in j_tokens:

                x_token = etree.SubElement(x_tokens, ns_prefix + "token", nsmap=ns_map)
                
                j_originalText = j_token["originalText"]
                j_ner = j_token["ner"]
                j_after = j_token["after"]

                x_text = etree.SubElement(x_token, ns_prefix + "text", nsmap=ns_map)
                x_text.text = j_originalText

                if j_ner != "O":

                    x_entity = etree.SubElement(x_token, ns_prefix + "entity", nsmap=ns_map)
                    
                    if j_ner in self.custom_ner:
                        x_authority = "ncdcr.gov"
                    else:
                        x_authority = "stanford.edu"

                    x_entity.text = j_ner
                    x_entity.set("authority", x_authority)

                x_separator = etree.SubElement(x_token, ns_prefix + "separator",
                                                                    nsmap=ns_map)
                x_separator.text = j_after

        x_string = etree.tostring(x_tokens)
        return x_string

#####
def main():
    j2h = JsonToXML()
    x = j2h.xml("sample.json")
    return x

if __name__ == "__main__":
    main()
