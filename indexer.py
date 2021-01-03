# DO NOT MODIFY CLASS NAME
import math
import pickle


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.config = config
        self.inverted_idx = {}
        self.postingDict = {}
        self.instanceDict = {}
        self.num_of_call_to_load_disk = 0
        self.num_of_doc = 0
        self.create_postingDict()
        self.weight_doc_dict = {}

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        self.num_of_doc += 1
        # Go over each term in the doc
        for term in document_dictionary.keys():
            # posting dict order by first letter of term
            if term[0].isdigit():
                first_key = "numbers"
            else:
                first_key = term[0].upper()  # return "A"
                if first_key not in self.postingDict.keys():
                    continue

            # frequency in the doc
            num_term = document_dictionary[term]
            # frequency / |term with the max freq|
            tf_ij = num_term / document.max_tf
            if term not in self.inverted_idx.keys():
                if " " in term:  # name and entity
                    if term not in self.instanceDict:  # first time
                        self.instanceDict[term] = [[1, ""], [document.tweet_id, num_term, document.num_of_uniq,
                                                             document.max_tf,
                                                             tf_ij]]  # value[0] -> inverted , value[1] --> posting
                        continue
                    else:  # second time for this term
                        update = self.instanceDict[term][0][0] + 1
                        self.inverted_idx[term] = [update, ""]   # update inverted
                        try:
                            self.postingDict[first_key][term] = []
                            # update posting on the first time + for this time posting dict add at the end of func
                            self.postingDict[first_key][term].append(self.instanceDict[term][1])
                        except:
                            del self.inverted_idx[term]
                            continue
                        # remove from instances dict
                        del self.instanceDict[term]
                # term not in inverted & no spaces in term
                elif term[0].isupper():
                    # capital letter --> check if exist lower case
                    if term.lower() in self.inverted_idx.keys():
                        # exist already
                        term = term.lower()
                        self.inverted_idx[term][0] += 1
                    else:
                        self.inverted_idx[term] = [1, ""]
                        try:
                            # initialize this key adding to posting in end of func
                            self.postingDict[first_key][term] = []
                        except:
                            del self.inverted_idx[term]
                            continue
                else:  # lower case not in inverted
                    # term in upper exist already
                    if term.upper() in self.inverted_idx.keys():
                        # change the key to lower case in inverted index dict:
                        update = []
                        update.extend(self.inverted_idx[term.upper()])
                        # +1 for this time
                        update[0] += 1
                        self.inverted_idx[term] =[update[0],update[1]]
                        del self.inverted_idx[term.upper()]  # remove the upper case
                        if term.upper() in self.postingDict[first_key]:
                            try:
                                # new key in posting dict
                                self.postingDict[first_key][term] = self.postingDict[first_key][term.upper()]
                                del self.postingDict[first_key][term.upper()]  # remove the upper case from posting
                            except:
                                del self.inverted_idx[term]
                                continue
                    # no term in upper case
                    else:
                        self.inverted_idx[term] = [1, ""]
                        try:
                            self.postingDict[first_key][term] = []
                        except:
                            del self.inverted_idx[term]
                            continue
            # term in inverted idx
            else:
                self.inverted_idx[term][0] += 1
            """
            ----all the terms in the inverted are in posting----
            if term not in self.postingDict[first_key]:  # case after clear to posting dict
                try:
                    self.postingDict[first_key][term] = []
                except:
                    del self.inverted_idx[term]
                    continue
                    
            """
            try:
                self.postingDict[first_key][term].append(
                    [document.tweet_id, num_term, document.num_of_uniq, document.max_tf, tf_ij])
            except:
                continue

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        raise NotImplementedError

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        raise NotImplementedError

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []

    def get_term_inverted_idx(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.inverted_idx[term] if self._is_term_exist(term) else []

    def create_postingDict(self):
        self.postingDict.update(
            {'A': {}, 'B': {}, 'C': {}, 'D': {}, 'E': {}, 'F': {}, 'G': {}, 'H': {}, 'I': {}, 'J': {}, 'K': {}, 'L': {},
             'M': {}, 'N': {}, 'O': {}, 'P': {}, 'Q': {}, 'R': {}, 'S': {}, 'T': {}, 'U': {}, 'V': {}, 'W': {}, 'X': {},
             'Y': {}, 'Z': {}, "@": {}, "#": {},
             "numbers": {}})

    def load_to_disk(self):
        path = self.config.get__outPath()
        self.num_of_call_to_load_disk += 1
        for first_key in self.postingDict.keys():  # A/B../numbers/#/@
            file_name = path + first_key
            try:
                with open(file_name, "rb+") as pickfile:
                    dict_from_disk = pickle.load(pickfile)  # {aa:[],[], ab: [],[]...}

                for term in self.postingDict[first_key].keys():
                    data_of_term = self.postingDict[first_key][term]
                    if not self.inverted_idx[term][1]:  # file not open yet
                        self.inverted_idx[term][1] = first_key

                    if term in dict_from_disk.keys():  # term exist in same case
                        # dict_from_disk[term] = self.sort_values(term, dict_from_disk[term])
                        dict_from_disk[term].extend(data_of_term)
                    else:
                        if term.upper() in dict_from_disk:  # check if exist in upper case
                            # dict_from_disk[term] = self.sort_values(term, dict_from_disk[term.upper()]) # update the dict
                            dict_from_disk[term] = dict_from_disk[term.upper()]
                            dict_from_disk[term].extend(data_of_term)
                            del dict_from_disk[term.upper()]  # remove the upper case

                        else:  # not exist in all version
                            dict_from_disk[term] = data_of_term
                try:
                    with open(file_name, "wb") as pickfile:
                        pickle.dump(dict_from_disk, pickfile)
                except:
                    # print('problem with the doc {}'.format(file_name))
                    pass

            except:
                with open(file_name, "wb") as pickfile:
                    pickle.dump(self.postingDict[first_key], pickfile)
                    for term in self.postingDict[first_key].keys():
                        self.inverted_idx[term][1] = first_key
            self.postingDict[first_key] = {}

    def calc_idf(self, num_of_docs_in_cor):

        for term in self.inverted_idx:
            a = num_of_docs_in_cor/self.inverted_idx[term][0]
            idft = math.log(a, 10)
            self.inverted_idx[term].append(idft)

    def sum_terms_per_docs(self, num_of_docs_in_cor):

        self.calc_idf(num_of_docs_in_cor)
        path = self.config.get__outPath()
        for first_key in self.postingDict.keys():
            file_name = path + first_key
            try:
                with open(file_name, "rb+") as pickfile:
                    dict_from_disk = pickle.load(pickfile)

                for term in dict_from_disk:
                    idf = self.inverted_idx[term][2]
                    data_of_term = dict_from_disk[term]
                    num_of_doc = len(dict_from_disk[term])  # self.inverted_idx[term][0]
                    for i in range(num_of_doc - 1):
                        id_doc = data_of_term[i][0]
                        tf_ij = data_of_term[i][4]
                        if id_doc in self.weight_doc_dict.keys():
                            self.weight_doc_dict[id_doc] += (tf_ij * idf) ** 2
                        else:
                            self.weight_doc_dict[id_doc] = (tf_ij * idf) ** 2

            except:
                # print('problem with the doc {}'.format(file_name))
                pass
