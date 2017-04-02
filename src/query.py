__author__ = 'Nick Hirakawa'

from invdx import build_data_structures
from rank import score_BM25
import operator


class QueryProcessor:
	def __init__(self, queries, corpus):
		self.queries = queries
		self.index, self.dlt = build_data_structures(corpus)


	def queries_with_thes(self, queries, thesaurus_dictionary):
		results = []
		for query in queries:
			for sub_query in query:
				for item in thesaurus_dictionary:
					if sub_query in item['MH']:
						results.append((' '.join(query), item))
					elif ' '.join(query) not in dict(results):
						results.append((' '.join(query), {}))
		return results


	def run(self, thesaurus_dictionary=None):
		results = []
		if thesaurus_dictionary is not None:
			self.queries = self.queries_with_thes(self.queries, thesaurus_dictionary)
		for query in self.queries:
			if thesaurus_dictionary is None:
				results.append((query, self.run_query(query)))
			elif query[0] in dict(results):
				results[[x[0] for x in results].index(query[0])][1].update(self.runz(query))
			else:
				results.append((query[0], self.runz(query)))
		return results


	def runz(self, query):
		query_result = dict()
		thes_term = query[1];
		term = thes_term['MH'] if thes_term else query[0]
		terms = term.split(' ')
		synonims = thes_term['SYNON'] if thes_term else []
		hyponims = thes_term['HYPON'] if thes_term else []
		hyperonims = thes_term['HYPERN'] if thes_term else []
		terms_in_index = any(x in self.index for x in terms)
		synonims_in_index = any(x in self.index for x in synonims)
		hyponims_in_index = any(x in self.index for x in hyponims)
		hyperonims_in_index = any(x in self.index for x in hyperonims)
		if terms_in_index or synonims_in_index or hyponims_in_index or hyperonims_in_index:
			for item in synonims + hyponims + hyperonims + terms:
				if item not in self.index: break
				doc_dict = self.index[item] # retrieve index entry
				for docid, freq in doc_dict.iteritems(): #for each document and its word frequency
					score = score_BM25(n=len(doc_dict), f=freq, qf=1, r=0, N=len(self.dlt),
									   dl=self.dlt.get_length(docid), avdl=self.dlt.get_average_length()) # calculate score
					if docid in query_result: #this document has already been scored once
						query_result[docid] += score
					else:
						query_result[docid] = score
		return query_result


	def run_query(self, query):
		query_result = dict()
		for term in query:
			if term in self.index:
				doc_dict = self.index[term] # retrieve index entry
				for docid, freq in doc_dict.iteritems(): #for each document and its word frequency
					score = score_BM25(n=len(doc_dict), f=freq, qf=1, r=0, N=len(self.dlt),
									   dl=self.dlt.get_length(docid), avdl=self.dlt.get_average_length()) # calculate score
					if docid in query_result: #this document has already been scored once
						query_result[docid] += score
					else:
						query_result[docid] = score
		return query_result

