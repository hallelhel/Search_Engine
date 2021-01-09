import itertools
from collections import OrderedDict

from ranker_new_test import Ranker
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

        relevant_docs, relevant_words = self._relevant_docs_from_posting(query_as_list) # return all the rel doc for the quiry

        #ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        relevant_docs = self._order_doc_by_words(relevant_docs, relevant_words)
        relevant_docs = OrderedDict(sorted(relevant_docs.items(), key=lambda item: item[1][3], reverse=True))
        relevant_docs = dict(itertools.islice(relevant_docs.items(), 2000))   #max is 2000 docs
        #relevant_docs_sort = self._ranker.rank_relevant_docs(relevant_docs, self._indexer, len(query_as_list))

        #relevant_docs_sort = self._ranker.dot_prodact_and_cos(relevant_docs, self._indexer, len(query_as_list))
        n_relevant = len(relevant_docs)
        if k is not None:
            relevant_docs = self.ranker.retrieve_top_k(relevant_docs, k)

        return n_relevant, relevant_docs



    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        relevant_words = {} #TODO new line
        for word in query_as_list:
            if word not in relevant_words.keys(): # TODO new line
                relevant_words[word] = 0
            posting_list = self._indexer.get_term_posting_list(word) #get all the twite with this word
            if len(posting_list) == 0: # no docs for this word
                del relevant_words[word]
                continue
            for doc in posting_list:
                relevant_words[word] += 1 # TODO new line - counting how many doc per word
                id = doc[0]
                if id not in relevant_docs.keys():
                    relevant_docs[id] = [1, [], []]# TODO adding list of words [2]
                    #self._indexer.get_term_inverted_idx[word]
                    tfidf = doc[4] * self._indexer.get_term_inverted_idx(word)[2]
                    relevant_docs[id][1].append(tfidf)

                    relevant_docs[id][2].append(word)# TODO new line

                else:
                    tfidf = doc[4] * self._indexer.get_term_inverted_idx(word)[2]
                    relevant_docs[id][1].append(tfidf)
                    relevant_docs[id][0] += 1
                    relevant_docs[id][2].append(word)# TODO new line
            # for list_doc_id in posting_list:
            #     df = relevant_docs.get(list_doc_id, 0)
            #     relevant_docs[doc_id] = df + 1
        return relevant_docs, relevant_words

    def _order_doc_by_words(self,relevant_docs, relevant_words):
        max_docs = max(relevant_words.values())
        num_of_words = len(relevant_words)
        min_weight = 1/num_of_words #0.25
        min_docs  = min(relevant_words.values()) #most uniq need to change
        max_weight = 1 #for firsttime need to change
        weight_words = {}
        relevant_words = OrderedDict(sorted(relevant_words.items(), key=lambda item: item[1]))
        for word in relevant_words:
            if relevant_words[word] == min_docs:
                weight_words[word] = max_weight
            else:
                weight_words[word] = max_weight - min_weight
                max_weight = max_weight - min_weight
                min_docs = relevant_words[word]
        for doc in relevant_docs:
            relevant_docs[doc].append(0)
            sum =0
            for word in relevant_docs[doc][2]:
                sum += weight_words[word]
            relevant_docs[doc][3] = sum


        return relevant_docs
