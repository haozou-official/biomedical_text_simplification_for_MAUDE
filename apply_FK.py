import textstat
import argparse


def apply_FK_score(documents_file, outfile):
    """
    Applies Flesch-Kincaid calculation to individual file

    Parameters
    ----------
    documents_file : File
        Txt file containing documents separated by newline.
    outfile : File
        Outfile destination.

    Returns
    -------
    None.

    """
    with open(outfile, 'w') as outfile:
        for line in open(documents_file, 'r').readlines():
            outfile.write(line.strip('\n') + '\t' 
                          + str(textstat.flesch_reading_ease(line.lower())) 
                          + '\n')
            

def apply_FK_diff(doc_file_pre, doc_file_post, outfile):
    """
    Applies Flesch-Kincaid calculation to original and translated file, 
    providing the difference (positive difference = increased readability)

    Parameters
    ----------
    doc_file_pre : File
        Txt file containing original documents separated by newline.
    doc_file_post : File
        Txt file containing post-simplification documents separated by newline.
    outfile : File
        Outfile destination.

    Returns
    -------
    None.

    """
    with open(outfile, 'w') as outfile:
        original = open(doc_file_pre, 'r').readlines()
        trans = open(doc_file_post, 'r').readlines()
        for i in range(0, len(original)):
            outfile.write(original[i].strip('\n') + '\t'
                          + trans[i].strip('\n') + '\t'
                          + str(textstat.flesch_reading_ease(trans[i].lower()) 
                             - textstat.flesch_reading_ease(original[i].lower()))
                          + '\n')
                          

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("doc_file", type=str,
                        help="""The file containing the documents""")
    parser.add_argument("-t", "--trans", type=str,
                        help="Post translational file, if getting difference in FK scores")
    parser.add_argument("outfile", type=str,
                        help="Where to write the evaluation result.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.trans is not None:
        apply_FK_diff(args.doc_file, args.trans, args.outfile)
    else:
        apply_FK_score(args.doc_file, args.outfile)
