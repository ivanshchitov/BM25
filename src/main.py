__author__ = 'Nick Hirakawa'

import sys, getopt
import io
import os, errno
import re
from parse import *
from query import QueryProcessor
import operator


def get_arguments():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:q:t:f:h", ["corpus=", "queries=", "thesaurus=","format=", "help"])
    except getopt.GetoptError as err:
        print str(err)
        print(help_text)
        sys.exit(2)
    corpus = None
    topics = None
    thesaurus = None
    output_format = "topic-to-text"
    for o, a in opts:
        if o in ("-c", "--corpus"):
            corpus = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-q", "--queries"):
            topics = a
        elif o in ("-t", "--thesaurus"):
            thesaurus = a
        elif o in ("-f", "--format"):
            output_format = a
        else:
            assert False, "unhandled option"

    return corpus, topics, thesaurus, output_format

help_text = """Usage: python main.py -c CORPUS_PATH -t TOPICS_PATH
-c CORPUS_PATH, --corpus=CORPUS_PATH:
\tPath to the document with the corpus of texts
-1 QUERIES_PATH, --queries=QUERIES_PATH:
\tPath to the document with list of queries(topics)
-f FORMAT, --format=FORMAT:
\tThe output format of algorythm result. Allowable values: "bm25" and "topic-to-texts"
-h, --help:
\tprints this help
"""

def usage():
    print help_text


def load_thesaurus_dictionary(thesaurus_path, synonym, hyponym, hypernym):
    if thesaurus_path is None:
        return None
    thesaurus_file = io.open(thesaurus_path, 'r')
    thesaurus_dictionary = []
    thesaurus_item = {}
    for line in thesaurus_file:
        if '*NEWRECORD' in line:
            thesaurus_item = {'SYNON': [], 'MN': [], 'HYPON': [], 'HYPERN': []}
        elif line == '\n':
            thesaurus_dictionary.append(thesaurus_item)
        elif line[:7] == 'NAME = ':
            thesaurus_item['MH'] = line[7:].replace(',', '').replace('\n', '')
        elif synonym and line[:17] == 'SYNONYMS_NAMES = ':
            entry = line[17:]
            for entry_item in entry.replace('[', '').replace(']', '').replace('\n', '').split(', '):
                if entry_item != '':
                    thesaurus_item['SYNON'] = list(set(thesaurus_item['SYNON']) | set([entry_item[2:len(entry_item) - 1]]))
        elif hyponym and line[:17] == 'HYPONYMS_NAMES = ':
            entry = line[17:]
            for entry_item in entry.replace('[', '').replace(']', '').replace('\n', '').split(', '):
                if entry_item != '':
                    thesaurus_item['HYPON'] = list(set(thesaurus_item['HYPON']) | set([entry_item[2:len(entry_item) - 1]]))
        elif hypernym and line[:18] == 'HYPERNYMS_NAMES = ':
            entry = line[18:]
            for entry_item in entry.replace('[', '').replace(']', '').replace('\n', '').split(', '):
                if entry_item != '':
                    thesaurus_item['HYPERN'] = list(set(thesaurus_item['HYPERN']) | set([entry_item[2:len(entry_item) - 1]]))
        elif line[:5] == 'ID = ':
            thesaurus_item['MN'] = list(set(thesaurus_item['MN']) | set([line[5:].replace('\n', '')]))
    thesaurus_file.close()
    return thesaurus_dictionary


def main():
	corpus_path, queries_path, thesaurus, output_format = get_arguments()
	cp = CorpusParser(filename=corpus_path)
	qp = QueryParser(filename=queries_path)
	qp.parse()
	queries = qp.get_queries()
	cp.parse()
	corpus = cp.get_corpus()
	thesaurus_dictionary = load_thesaurus_dictionary(thesaurus, 0, 1, 1)
	proc = QueryProcessor(queries, corpus)
	results = proc.run(thesaurus_dictionary)
	qid = 0
	for topic, result in results:
		sorted_x = sorted(result.iteritems(), key=operator.itemgetter(1 if output_format == "bm25" else 0))
		if output_format == "bm25": sorted_x.reverse()
		index = 0
		docs = []
		for item in sorted_x:
			tmp = (qid + 1, item[0], index, item[1])
			if output_format == "bm25": 
				print '{:>1}\tQ0\t{:>4}\t{:>2}\t{:>12}\tNH-BM25'.format(*tmp)
			index += 1
			docs.append(item[0])
		qid += 1
		if output_format != "bm25":
			print ' '.join(topic) if thesaurus_dictionary is None else topic + ' ' +', '.join(docs)


if __name__ == '__main__':
	main()

