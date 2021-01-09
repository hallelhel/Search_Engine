import string

from nltk import PorterStemmer, re

from parser_module import Parse

class Parse(Parse) :
    def __init__(self):
        self.stemmer = PorterStemmer()
        super().__init__()

    def text_operation(self, text):
        """
        This function takes a list of tokenizes and manipulate every token to his case
        param: text: list of tokens.
        :return: the text after parser.
        """
        len_text = len(text)
        tokenAfterParse = []
        counter = -1
        for term in text:
            counter = counter + 1
            if self.per == True:
                self.per = False
                continue
            if self.per2 == True:
                self.per = True
                self.per2 = False
                continue
            if term == " " or term == '' or "http" in term:
                continue

            if term[-1] in string.punctuation or ord(term[-1]) < 48 or ord(
                    term[-1]) > 127:  # to remove anything that is not a word or number in the end of the word
                if term[-1] != '%':
                    while term[-1] in string.punctuation or ord(term[-1]) < 48 or ord(term[-1]) > 127:
                        term = term[:-1]
                        if term == "":
                            break
                if term == "":
                    continue
                # text[counter] = term FIXME happen in line 160

            # hashtag & tags cases:
            if term[0] in string.punctuation or ord(term[0]) > 127:
                if term[0] == '#' and len(term) > 2:
                    # if len(term) == 2:
                    #     continue
                    words = self.hashtag_tokenize(
                        term[1:])  # this func split the words and add the original hashtag with lower case to words
                    tokenAfterParse.extend(words)
                    continue
                elif term[0] != '@':
                    while term[0] in string.punctuation:
                        term = term[1:]
                        if len(term) < 2:
                            break
                    if term == "":
                        continue
                    text[counter] = term

            # number cases - dates/percentage:
            if term.startswith('covid') or term.startswith('Covid') or term.startswith('COVID'):
                tokenAfterParse.append('covid19')
                continue

            if term.startswith('corona') or term.startswith('Corona') or term.startswith('CORONA'):
                tokenAfterParse.append('corona')
                continue

            term = self.clean_word(term)
            if isinstance(term, list):
                continue

            # try to minimize the covid terms
            if (term.isdigit() or term[0].isdigit()) and not (re.search('[a-zA-Z]', term)):
                if counter + 1 < len_text and term.isdigit():
                    if text[counter + 1] in self.month_dict:  # Date
                        tokenAfterParse.append(self.Date_Toknize(term, text, counter, len_text))
                        continue
                    if text[counter + 1] == "percent" or text[counter + 1] == "percentage" or text[
                        counter + 1] == "Percent" or text[counter + 1] == "Percentage":  # %
                        new_word = term + text[counter + 1]
                        tokenAfterParse.append(new_word)
                        self.per = True
                        continue
                new_number = self.numbeOpertion(term, text, counter, len_text)
                tokenAfterParse.append(new_number)
                continue

            # check entity
            if counter + 1 < len_text:
                if term[0].isupper() and text[counter + 1][0].isupper():  # words with big letter
                    name = self.entity(text, counter, len_text)
                    tokenAfterParse.append(name)
                    tokenAfterParse.append(term)
                    continue
                if term in self.month_dict and text[counter + 1].isdigit():
                    tokenAfterParse.append(self.Date_Toknize(term, text, counter, len_text))
                    continue
            # replace every number from one to ten to digits:
            elif term in self.dict_numbers.keys():
                term = self.dict_numbers[term]

            term = self.stemmer.stem(term)
            tokenAfterParse.append(term)
        return tokenAfterParse


    def hashtag_tokenize(self, hashtag):
        words = []
        # if ord(hashtag[0]) > 127: TODO no need
        #    return words

        # case under score
        if "_" in hashtag:
            words = hashtag.split("_")
            words = list(filter(None, words))
            words = self.ignore_fake_words(words)
            words.append('#' + hashtag.replace("_", "").lower())
            return words
        word = ""
        len_word = len(hashtag)
        i = 0
        upper_before = False
        if hashtag[0].isupper():
            if hashtag[1].islower():
                word = hashtag[:2]
                i = 2
            else:
                word = hashtag[0]
                i = 1
                upper_before = True
        while i < len_word:

            if hashtag[i].isupper() and upper_before == True:  # seq of upper
                if i + 1 <= len_word - 1:
                    if hashtag[i + 1].islower():
                        words.append(word)
                        word = hashtag[i]
                    else:
                        word = word + hashtag[i]
                else:
                    word = word + hashtag[i]
                    break
            elif hashtag[i].isupper():  # before was lower or
                if len(word) > 0:
                    words.append(word)
                word = hashtag[i]  # initialize new word
                if i + 1 > len_word - 1:
                    break
                upper_before = True

            elif hashtag[i].islower() and upper_before == False:  # seq of lower
                word = word + hashtag[i]
                upper_before = False
                if i + 1 > len_word - 1:
                    break

            elif hashtag[i].islower() and upper_before == True:  # before was upper

                if len(word) == 1:  # capital letter (only one letter in word)
                    word = word + hashtag[i]

                elif len(word) > 1:  # save the word seperate
                    words.append(word)
                    word = hashtag[i]  # initialize new word
                upper_before = False

                if i + 1 > len_word - 1:
                    break

            elif hashtag[i].isdigit():
                if len(word) > 0 and not word.isdigit():
                    words.append(word)
                    word = ""
                word = word + hashtag[i]

            i += 1
        words.append(word)
        words = self.ignore_fake_words(words)
        new_list = []
        for word in words:
            word = self.stemmer.stem(word)
            new_list.append(word)
        new_list.append('#' + hashtag.lower())
        #words.append('#' + hashtag.lower())  # add the real hashtag with lower case
        return new_list


