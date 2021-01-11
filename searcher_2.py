import itertools
from collections import OrderedDict
import nltk
#nltk.download("wordnet")
from nltk.corpus import wordnet as wn
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
        query_list = query.split(" ")
        query_as_list = self._parser.text_operation(query_list)
        # extension  by word net
        queary_list_after_word_net = self.q_word_net(query_as_list)
        #remove stop words
        query_as_list = self._parser.parse_sentence(queary_list_after_word_net)
        # find the docs
        relevant_docs = self._relevant_docs_from_posting(query_as_list) # return all the rel doc for the quiry

        relevant_docs = OrderedDict(sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True))
        relevant_docs = dict(itertools.islice(relevant_docs.items(), 2000))   #max is 2000 docs
        #relevant_docs_sort = self._ranker.rank_relevant_docs(relevant_docs, self._indexer, len(query_as_list))
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
    this function expand the query by using word net 
    get query as list and add words by word net
    """
    def q_word_net(self, query):
        extend_query = []
        extend_query.extend(query)
        for word in query:
            add_new_word = False
            counter_same_word = 0
            syn_list = wn.synsets(word)
            for i in range(len(syn_list)):
                if syn_list[i].lemma_names() != []:
                    for lemma in syn_list[i].lemma_names():
                        if lemma == word:
                            continue
                        else:
                            new_word = lemma
                            if "_" not in new_word:
                                if self._indexer._is_term_exist_in_idx(new_word):
                                    extend_query.append(new_word)
                                    add_new_word = True
                                    break
                            else: # more then one word
                                new_word_list = new_word.split("_")
                                for w in new_word_list:
                                    if self._indexer._is_term_exist_in_idx(w):
                                        extend_query.extend(new_word_list)
                                        add_new_word = True
                                        break
                        if add_new_word == True:
                            break
                        counter_same_word += 1
                        if counter_same_word > 1:
                            break
                    if add_new_word == True:
                        break
                if add_new_word == True:
                    break
                elif i>1:
                    break

        return set(extend_query)




            

