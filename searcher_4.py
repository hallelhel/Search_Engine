import itertools
from collections import OrderedDict
import nltk
from spellchecker import SpellChecker
from nltk.corpus import wordnet as wn
from ranker import Ranker
#import utils
"""
search engine for spell checker
"""

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
        query_list = query.split(" ")
        query_as_list = self._parser.text_operation(query_list)
        # extension  by spell checker
        queary_list_after_word_net = self.q_spell_check(query_as_list)
        #remove stop words
        query_as_list = self._parser.parse_sentence(queary_list_after_word_net)
        # find the docs
        relevant_docs = self._relevant_docs_from_posting(query_as_list) # return all the rel doc for the quiry
        #ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)

        relevant_docs = OrderedDict(sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True))
        relevant_docs = dict(itertools.islice(relevant_docs.items(), 2000))   #max is 2000 docs
        relevant_docs_sort = self._ranker.rank_relevant_docs(relevant_docs, self._indexer, len(query_as_list))
        n_relevant = len(relevant_docs)
        if k is not None:
            relevant_docs_sort = self.ranker.retrieve_top_k(relevant_docs_sort, self.k)
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
            posting_list = self._indexer.get_term_posting_list(word)  # get all the twite with this word
            for doc in posting_list:
                tf = self._indexer.get_term_inverted_idx(word)[2]
                id = doc[0]
                if id not in relevant_docs.keys():
                    relevant_docs[id] = [1, []]
                    # self._indexer.get_term_inverted_idx[word]
                    tfidf = doc[4] * tf
                    relevant_docs[id][1].append(tfidf)
                else:
                    tfidf = doc[4] * tf
                    relevant_docs[id][1].append(tfidf)
                    relevant_docs[id][0] += 1

        return relevant_docs
    """
    this function expand the query by using spell checker 
    get query as list and add words by checker
    """
    def q_spell_check(self, query):
      spell = SpellChecker()
      corr_q = []
      corr_q.extend(query)
      i = 0
      for word in query:
          new_word = spell.correction(word)
          if new_word != word:
              if self._indexer._is_term_exist_in_idx(new_word):
                  corr_q[i] = new_word
          i += 1
      return corr_q









            

