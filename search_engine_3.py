import os
import time

import pandas as pd
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher_3 import Searcher
#import utils


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        #r = ReadFile(self.config.get__corpusPath())
        #reader = ReadFile(fn)
        #walk_dir = self.config.get__corpusPath()
        # for root, subdirs, files in os.walk(walk_dir, topdown=True):
        #   for file in files:  # files=folder
        #        if file.endswith('.parquet'):


        start = time.time()
        number_of_documents = 0
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()

        # Iterate over every document in the file
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
            # print("finish file")
        end = time.time()
        print(end-start)
        self._indexer.sum_terms_per_docs(number_of_documents)
        #self._indexer.load_to_disk()
        print('Finished parsing and indexing.')
        #utils.save_obj(self._indexer.inverted_idx, "inverted_idx")
        # utils.save_obj(indexer.postingDict, "posting")
        #utils.save_obj(self._indexer.weight_doc_dict, "weight_doc_dict")
    # save


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """

        pass

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(query)
