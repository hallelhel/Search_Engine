import itertools
from collections import OrderedDict

from ranker import Ranker
#import utils


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        quert_list = query.split(" ")
        query_as_list = self._parser.text_operation(quert_list)
        query_as_list = self._parser.parse_sentence(query_as_list)

        #query_as_list = self._parser.parse_sentence(query)

        relevant_docs = self._relevant_docs_from_posting(query_as_list) # return all the rel doc for the quiry

        #ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)

        relevant_docs = OrderedDict(sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True))
        relevant_docs = dict(itertools.islice(relevant_docs.items(), 2000))   #max is 2000 docs
        #relevant_docs_sort = self._ranker.rank_relevant_docs(relevant_docs, self._indexer, len(query_as_list))

        relevant_docs_sort = self._ranker.dot_prodact_and_cos(relevant_docs, self._indexer, len(query_as_list))
        n_relevant = len(relevant_docs_sort)
        if k is not None:
            relevant_docs_sort = self.ranker.retrieve_top_k(relevant_docs_sort, k)

        return n_relevant, relevant_docs_sort



    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        for word in query_as_list:
            posting_list = self._indexer.get_term_posting_list(word) #get all the twite with this word
            for doc in posting_list:
                id = doc[0]
                if id not in relevant_docs.keys():
                    relevant_docs[id] = [1, []]
                    #self._indexer.get_term_inverted_idx[word]
                    tfidf = doc[4] * self._indexer.get_term_inverted_idx(word)[2]
                    relevant_docs[id][1].append(tfidf)
                else:
                    tfidf = doc[4] * self._indexer.get_term_inverted_idx(word)[2]
                    relevant_docs[id][1].append(tfidf)
                    relevant_docs[id][0] += 1
        return relevant_docs
