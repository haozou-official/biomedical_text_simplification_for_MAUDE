# -*- coding: utf-8 -*-
"""
Preprocessing for MAUDE data pull-
Tokenize Sentences and normalize abbreviations using the NLM Lexical Variant 
Generator (lvg); see https://www.nlm.nih.gov/research/umls/new_users/online_learning/LEX_004.html
for more information"""

import subprocess
import csv
from nltk import word_tokenize
import argparse

def main(file, workflow):
    corpus = []
    for record in load_data(file):
        document = record[12]
        document = document.replace('Description of Event or Problem : ', '')
        document = word_tokenize(document)
        corpus.append('\n'.join(document))
        
    output = []
    
    for doc in corpus:
        output.append(lvg_pipeline(doc, workflow))
    return(output)
    

def load_data(file):
    reports = []
    with open(file, 'r') as data_file:
        reader = csv.reader(data_file)
        # skip first four rows (meta-data and headers)
        for row in reader:
            reports.append(row)
    # Do not return first four rows of meta-data + headers
    return reports[4:]
    

def lvg_step(item, options=['-f:i']):
    """Executes a given step in the lvg workflow

    :param str item: A given document
    :param list options: Options for the lvg pipeline
    
    :return result in lvg field format
    """
    # Need to specify local java env
    # Need to specify lvg batch file (windows)
    # For mac os/linux will need appropriate program file
    java_env = {'PATH':'C:\\Program Files\\Java\\jre1.8.0_281\\bin'}
    lvg = ['C:\\Users\\Ariba\\lvg2020\\bin\\lvg.bat']
    lvg.extend(options)
    p1 = subprocess.run(lvg, env=java_env, text=True
                        , input=item, check=True, capture_output=True)
    return p1.stdout

def lvg_pipeline(start, workflow):
    """Given start document (sentence), function to set up workflow based on 
    defined workflow steps
    
    :param str start: A given raw document
    :param list workflow: A list of workflow flags consistent with lvg 
        documentation
    """
    assert len(workflow) > 0
    
    def get_output(output_str):
        output = output_str.split('\n')
        output = [x.split('|')[1] for x in output if x != '']
        return '\n'.join(output)
    
    workflow_steps = {'-f:0':'Strip NEC and NOS.', '-f:a':'Generate known acronym expansions.'
                      , '-f:A':'Generate known acronyms.', '-f:An':'Generate antiNorm.'
                      , '-f:b':'Uninflect the input term.', '-f:B':'Uninflect words.'
                      , '-f:Bn':'Normalized Uninflect words.', '-f:c': 'Tokenize.'
                      , '-f:ca': 'Tokenize keep all.', '-f:ch': 'Tokenize no hyphens.'
                      , '-f:C': 'Canonicalize.', '-f:Ct': 'Lexical name.'
                      , '-f:d': 'Generate derivational variants.', '-f:dc~LONG': 'Generate derivational variants, specifying output categories'
                      , '-f:e': 'Retrieve uninflected spelling variants.', '-f:E':'Retrieve Eui.'
                      , '-f:f': 'Filter output.', '-f:fa': 'Filter out acronyms and abbreviations.'
                      , '-f:fp': 'Filter out proper nouns.', '-f:g': 'Remove Genitive.'
                      , '-f:G': 'Generate fruitful variants.', '-f:Ge': 'Fruitful variants, enhanced.'
                      , '-f:Gn': 'Generate known fruitful variants.', '-f:i': 'Generate inflectional variants.'
                      , '-f:ici~LONG+LONG': 'Generate inflectional variants, specifying output categories and inflections'
                      , '-f:is': 'Generate inflectional variants (simple infl).', '-f:l':'Lowercase the input.'
                      , '-f:L':'Retrieve category and inflection.', '-f:Ln': 'Retrieve category and inflection from database.'
                      , '-f:Lp': 'Retrieve category and inflection for all terms begins with the given word.'
                      , '-f:m': 'Metaphone.', '-f:n': 'No operation.', '-f:nom': 'Retrieve nominalizations.'
                      , '-f:N': 'Normalize.', '-f:N3': 'LuiNormalize.', '-f:o': 'Replace punctuation with space.'
                      , '-f:p': 'Strip punctuation.', '-f:P':'Strip punctuation, enhanced.'
                      , '-f:q': 'Strip diacritics.', '-f:q0':'Map symbols to ASCII.', '-f:q1':'Map Unicode to ASCII.'
                      , '-f:q2': 'Split ligatures.', '-f:q3':'Get Unicode names.', '-f:q4':'Get Unicode synonyms.'
                      , '-f:q5': 'Norm Unicode to ASCII.', '-f:q6': 'Norm Unicode to ASCII with synonym option.'
                      , '-f:q7':'Unicode core norm.', 'f:q8':'Strip or map Unicode.', '-f:r': 'Recursive synonyms.'
                      , '-f:rs':'Remove (s), (es), (ies).', '-f:R':'Recursive derivations.'
                      , '-f:s':'Generate spelling variants.', '-f:S':'Syntactic uninvert.', '-f:Si':'Simple inflections.'
                      ,'-f:t':'Strip stop words.', '-f:T':'Strip ambiguity tags.', '-f:u':'Uninvert phrase around commas.'
                      , '-f:U':'Convert output.', '-f:v':'Generate fruitful variants from database.'
                      , '-f:w':'Sort by word order.', '-f:ws~INT':'Word size filter.', '-f:y':'Generate synonyms.'}
    
    i = 0
    for step in workflow:
        if i == 0:
            output = [(workflow_steps[workflow[0]], get_output(lvg_step(start.lower(), options=[workflow[0]])))]
            i += 1
        else:
            output.append((workflow_steps[step], get_output(lvg_step(output[i-1][1], options=[step]))))
            i += 1
    
    return output
        
def parse_args():
    parser = argparse.ArgumentParser(description="""Process raw documents with lvg""")
    parser.add_argument("infile", type=str,
                        help="""CSV file containing MAUDE data pull""")
    parser.add_argument("-o", "--option", action='append', 
                        help="LVG workflow flags", required=True)
    return parser.parse_args()

# default is gen variants - returns each var sep by \n

#output = lvg_stetp('sleep').split('\n')
#output = [info.split('|') for info in output]
#print(output)
# get synonyms
# print(lvg_step('sleep', options=['-f:y']))

# test_sent = 'The PG exhibited evidence of malfunction and oversensing was detected on the s-ECG'

# output = lvg_pipeline(test_sent, ['-f:ch', '-f:i'])
# print(output)

if __name__ == "__main__":
    args = parse_args()
    # add flags after parser
    args.option = ['-' + flag for flag in args.option]
    output = main(args.infile, args.option)
    for rec in output:
        print(rec)