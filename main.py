#!/usr/bin/env python3

"""
TODO:
    - Move into class structure; instantiate other classes in __init__.
        - Example: HTMLToText() only needs to be instantiated once.
        - BTW: Is that composition?
    - Add timeout length to NLP if text is long.
        - For now, setting timeout when starting the server (http://stackoverflow.com/a/36437157).
    - Likely better to write output XML incrementally rather than all at once.
        - This will be easier in a class structure.
	- You should still create a standalone text-to-NLP module to abstract the process.
		- Do the same for tagging EAXS - i.e. a module that returns tagged EAXS.
		- This script should just be a "playlist".

    - Currently (May 12, 2017): The tagged demo from main() has XML-entity escaped stuff in the Content element.
        - Also, the CotentType and TransferEncoding are missing.
        - Also, I'm seeing line breaks in other elements that were not there before.
    - Once a decision is made re: Comments, this would need to udpate ContentTypeComments,
    TransferEncodingComments, Description and/or DescriptionComments to say that this version
    of the EAXS has modifications VS the original.
    - Base64 decode.decode needs to take an encoding parameter.
"""

# import modules.
import base64
import json
from lxml.etree import CDATA
from pycorenlp import StanfordCoreNLP
from lib.eaxs_to_etree import *
from lib.html_to_text import *
from lib.nlp_to_xml import *

CHARSET = "utf-8"

def getText(html):
    """ Returns text version of @html (string). """

    # alter DOM.
    html = ModifyHTML(html, "html5lib")
    html.shift_links()
    html.remove_images()
    html = html.raw()
    
    # convert HTML to text.
    h2t = HTMLToText()
    text = h2t.text(html, is_raw=True)

    return text


def getNLP(text):
    """ Returns CoreNLP JSON string for @text (string). """

    nlp = StanfordCoreNLP("http://localhost:9000")
    options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
               "outputFormat": "json",
               "regexner.mapping": "regexner_TOMES/mappings.txt"}
    try:
        nlp = nlp.annotate(text, properties=options)
    except Exception as e:
        exit(e)
    
    return nlp
    

def getTagged(jdict):
    """ Returns tagged version of CoreNLP JSON string: @jdict (dictionary). """

    # convert JSON To tagged XML.
    n2x = NLPToXML()
    tagged = n2x.xml(jdict, return_string=True)
    print(tagged) # test.

    return tagged


def tagEAXS(eaxs_file):
    """ Returns tagged version EAXS file: @eaxs_file (string). """

    #
    eaxs = EAXSToEtree(eaxs_file)
    messages = eaxs.messages()

    #
    for message in messages:

        #
        charset = message["charset"]
        content = message["content"]
        content_type = message["content_type"]
        transfer_encoding = message["transfer_encoding"]

        #
        text = content.text
        if text == None:
            continue

        #
        if transfer_encoding == "base64":
            text = base64.decode(content.text)
            text = text.decode()
	
        #
        if content_type.text == "text/html":
            text = getText(text)
	
        #
        nlp = getNLP(text)
        tagged = getTagged(nlp)

        #
        charset.text = CHARSET
        content.text = CDATA(tagged)
        content_type.text  = "text/xml"
        transfer_encoding = None
        break # test line.
    
    return eaxs


# TEST.
def main():

    import codecs
    import sys
    
    try:
        f = sys.argv[1]
    except:
        exit("Please pass an EAXS file via the command line.")
    
    tagged = tagEAXS(f)
    print(tagged)
    tagged = etree.tostring(tagged.root, pretty_print=True)
    tagged = tagged.decode("utf-8")
    
    f_tagged = f.replace(".xml", ".tagged.xml")
    with codecs.open(f_tagged, "w", encoding="utf-8") as x:
        x.write(tagged)
 
if __name__ == "__main__":
	main()

