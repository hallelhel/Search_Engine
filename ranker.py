# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math


class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(relevant_doc, _indexer ,len_query, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        for doc in relevant_doc:
            mone = 0
            for wij in relevant_doc[doc][1]:
                mone +=wij
            machne = _indexer.get_weight_doc[doc]
            machne= machne * len(len_query)
            cosSim= mone/math.sqrt(machne)
            relevant_doc[doc][1] = cosSim
        list_sorted = sorted(relevant_doc.items(), key=lambda item: item[1][1], reverse=True)
        return list_sorted
        # ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
        # if k is not None:
        #     ranked_results = ranked_results[:k]
        #return [d[0] for d in ranked_results]

    def retrieve_top_k(sorted_relevant_doc, k):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]


