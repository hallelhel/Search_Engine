import string
from urllib.parse import urlparse

from nltk import RegexpTokenizer, re, regexp_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english') + ['http', 'https', 'rt', '', ' ', '_', '-', '.', '/', ',', 'www']
        self.tokenizer = RegexpTokenizer(r'\w-|\$[\d\.]+|\S+')
        self.month_dict = {'January': '01', 'JANUARY': '01', 'February': '02', 'FEBRUARY': '02', 'March': '03', 'MARCH': '03', 'April': '04', 'APRIL': '04', 'May': '05', 'MAY': '05', 'June': '06', 'JUNE': '06', 'July': '07', 'JULY': '07', 'August': '08', 'AUGUST': '08', 'September': '09',
                           'SEPTEMBER': '09', 'October': '10', 'OCTOBER': '10', 'November': '11', 'NOVEMBER': '11', 'December': '12', 'DECEMBER': '12'}
        self.number_list = ["Thousand", "Million", "Billion", "million", "thousand", "billion"]
        self.dict_numbers = {"one": '1', "two": '2', "three": '3', "four": '4', "five": '5', "six": '6', "seven": '7',
                             "eight": '8', "nine": '9', "ten": '10'}
        self.per = False
        self.per2 = False
        self.url = []
        self.words_with_garbage = []

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        text_tokens_without_stopwords = []
        for w in text:
            if w.lower() not in self.stop_words:
                text_tokens_without_stopwords.append(w)
        return text_tokens_without_stopwords

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        quote_text = doc_as_list[7]
        quote_url = doc_as_list[8]
        term_dict = {}
        if "http" in full_text:
            if url != "{}":
                split_url = url.split('"')
                self.url = self.url_Opretion(split_url[3])
                # self.text_operation(self.url)
                # if len(index)>2:
                #     index_strart = int(index[0][2:])
                #     index_end = int(index[1][:-1])
                # else:
                #     index_strart= int(index[0][2:])
                #     index_end= int(index[1][:-2])
                # if index_strart == 117 and index_end ==140: # problematic indexes
                #     pass
                # else:
                #     full_text = full_text[:index_strart] + split_url[3] + full_text[index_end:]


        full_text = full_text.replace(",", "")
        tokenized_text = self.tokenizer.tokenize(full_text)
        tokenized_text = self.text_operation(tokenized_text)
        tokenized_text = self.parse_sentence(tokenized_text)
        self.words_with_garbage = self.text_operation(self.words_with_garbage)
        tokenized_text.extend(self.url)
        self.url = []
        tokenized_text.extend(self.words_with_garbage)
        self.words_with_garbage = []
        doc_length = len(tokenized_text)  # after text operations.
        uniq_max_freq = self.calc_uniq_max_freq(tokenized_text,term_dict)
        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,quote_url, term_dict, doc_length, uniq_max_freq[0], uniq_max_freq[1])
        return document

    def calc_uniq_max_freq(self, tokenized_text, term_dict):
        """
        The function puts in a dictionary and calculates the most common words
        """
        max_tf = 1
        num_of_uniq = 0
        for term in tokenized_text:
            try:
                if len(term) <= 2:
                    if term[0].isalpha():  # remove terms with one letter
                        continue
                if term[0].isupper():
                    term = term.upper()  # change the all term to capital letter
                else:
                    term = term.lower()
                if term not in term_dict.keys():
                    if term[0].isupper():  # capital letter --> check if exist lower case
                        if term.lower() in term_dict.keys():  # term exist already
                            term_dict[term.lower()] += 1
                            if max_tf < term_dict[term.lower()]:
                                max_tf = term_dict[term.lower()]
                            continue
                        else:
                            num_of_uniq += 1
                            term_dict[term] = 1
                            continue
                    else:  # lower case
                        if term.upper() in term_dict.keys():  # term exist already
                            term_dict[term.lower()] = term_dict.pop(term.upper())  # change the key to lower case
                            term_dict[term] += 1
                            if max_tf < term_dict[term.lower()]:
                                max_tf = term_dict[term.lower()]
                        else:
                            num_of_uniq += 1
                            term_dict[term] = 1
                else:  # this term already exist
                    # if term.lower() in term_dict.keys():
                    term_dict[term] += 1
                    if max_tf < term_dict[term]:
                        max_tf = term_dict[term]

            except:
                # print('problem with the following key {}'.format(term))
                pass

        return num_of_uniq, max_tf

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

            if term[-1] in string.punctuation or ord(term[-1]) < 48 or ord(term[-1]) > 127:  # to remove anything that is not a word or number in the end of the word
                if term[-1] != '%':
                    while term[-1] in string.punctuation or ord(term[-1]) < 48 or ord(term[-1]) > 127:
                        term = term[:-1]
                        if term == "":
                            break
                if term == "":
                    continue
                #text[counter] = term FIXME happen in line 160

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

            tokenAfterParse.append(term)
        return tokenAfterParse

    def hashtag_tokenize(self, hashtag):
        """
        This function takes a hashtag term  and splits every term
        param: hashtag: the char # + term/terms
        :return: list of terms and the original hashtag woth lower case.
        """
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
        words.append('#' + hashtag.lower())  # add the real hashtag with lower case
        return words

    def ignore_fake_words(self, words):
        """
       The function takes a word and removes the garbage from the end

        """
        new_words = []
        if '' in words:
            return new_words
        for word in words:
            try:
                if not (word[0] in string.punctuation):
                    if word[-1].isalpha():
                        if len(word) > 2:
                            while len(set(word[-3:])) == 1:
                                word = word[:-1]
                                if len(word) < 3:
                                    break
                    new_words.append(word)
            except:
                # print('problem with ignore fake words {}'.format(words))
                pass
        return new_words

    def url_Opretion(self, url):
        pars_url = urlparse(url)
        host_name = pars_url.hostname
        if not host_name or url == 'https://www' or host_name == 't.co':
            return []
        #host_name_tokenize = host_name.split(".")
        if host_name.startswith("www"):
            host_name_split = host_name.split(".", 1)
            try:
                host_name = host_name_split[1]
            except:
                host_name = host_name_split[0]
        return_host = [host_name]
        return return_host
        # text_tokens = regexp_tokenize(url, "[\w']+")
        # for word in host_name_tokenize:
        #     if word in text_tokens:
        #         text_tokens.remove(word)
        # text_tokens.append(host_name)
        # text_tokens = self.ignore_fake_words(text_tokens)
        # #self.url.extend(text_tokens)
        #return text_tokens

    # check sequence of capital letters in text
    def entity(self, text, ind, len_text):
        # text[ind] = self.remove_repited_letters(text[ind])
        name = text[ind]
        i = 0
        for word in text[ind + 1:len_text]:
            if word[0].isupper():
                if word[-1] in string.punctuation:  # remove pon from the end
                    word = word[:-1]
                # word = self.remove_repited_letters(word)
                name = name + " " + word
                if i == 2:  # 3 is the max intity
                    break
            else:
                break  # just words close to each other
            i += 1
        if name[1].isspace():
            name = self.remove_spaces(name)
        return name

    def numbeOpertion(self, number, text, counter, len_text):
        try:
            if float(number) < 1000:  # small number
                if counter + 1 < len_text:
                    if text[counter + 1] in self.number_list or '/' in text[counter + 1]:  # number with word or dicemal number
                        self.per = True
                        return self.number_with_word(number, text, counter)
                if (number.isdigit()) or ((len(number) - number.index('.') - 1) == 1) or (
                        (len(number) - number.index('.') - 1) == 2):  # 1 or 2 digit after the dot
                    new_num = str(number)
                    return new_num
                else:
                    new_num = float(number) - float(number) % 0.001  # more then 2 digit after the dot
                    return str(new_num)

            if (float(number) >= 1000) and (float(number) < 1000000):  # between 1000-1000000
                if '.' in number:
                    ind = number.index('.')
                    number = number[:ind]
                if float(number) % 1000 == 0:
                    new_num = round(int(number) / 1000)
                elif float(number) % 100 == 0:
                    new_num = round(int(number) / 1000, 2)
                elif float(number) % 10 == 0:
                    new_num = round(int(number) / 1000, 3)
                else:
                    new_num = float(number) / 1000
                    new_num = self.save_remind(new_num)
                new_num = str(new_num) + 'K'
                return new_num

            elif (float(number) >= 1000000) and (float(number) < 1000000000):  # between 1m- 1b
                if '.' in number:
                    ind = number.index('.')
                    number = number[:ind]
                if float(number) % 1000000 == 0:
                    new_num = round(int(number) / 1000000)
                elif float(number) % 100000 == 0:
                    new_num = round(int(number) / 1000000, 2)
                elif float(number) % 10000 == 0:
                    new_num = round(int(number) / 1000000, 3)
                else:
                    new_num = float(number) / 1000000
                    new_num = self.save_remind(new_num)
                new_num = str(new_num) + 'M'
                return new_num

            elif float(number) >= 1000000000:  # more milliard
                if '.' in number:
                    ind = number.index('.')
                    number = number[:ind]
                if float(number) % 1000000000 == 0:
                    new_num = round(int(number) / 1000000000)
                elif float(number) % 100000000 == 0:
                    new_num = round(int(number) / 1000000000, 2)
                elif float(number) % 10000000 == 0:
                    new_num = round(int(number) / 1000000000, 3)
                else:
                    new_num = float(number) / 1000000000
                    new_num = self.save_remind(new_num)
                new_num = str(new_num) + 'B'
                return new_num
        except:
            return number

    def save_remind(self, new_num):
        """
        The function deletes repetitive letters at the end of a word
        """
        new_num_str = str(new_num)
        p_ind = new_num_str.index('.')
        try:
            new_num_str = new_num_str[:p_ind + 4]  # 3 digit after point
        except:
            try:
                new_num_str = new_num_str[:p_ind + 3]  # 2 digit after point
            except:
                try:
                    new_num_str = new_num_str[:p_ind + 2]  # 1 digit after point
                except:
                    pass
        end_ind = len(new_num_str) - 1
        while int(new_num_str[end_ind]) < 1:
            new_num_str = new_num_str[:end_ind]
            end_ind = -1
            if new_num_str[end_ind] == '.':
                new_num_str = new_num_str[:-1]
                break
        return new_num_str

    def number_with_word(self, number, text, index):
        if text[index + 1] == 'Thousand' or text[index + 1] == 'thousand':  # with word
            new_num = str(number) + 'K'
            return new_num
        if text[index + 1] == 'Million' or text[index + 1] == 'million':  # with word
            new_num = str(number) + 'M'
            return new_num
        if text[index + 1] == 'Billion' or text[index + 1] == 'billion':  # with word
            new_num = str(number) + 'B'
            return new_num
        if '/' in text[index + 1]:  # decimal number
            new_num = str(number) + ' ' + text[index + 1]
            return new_num

    def remove_spaces(self, term):
        new_term = term[0]
        i = 2
        while i < len(term) - 1:
            if term[i].isspace():
                i += 1
                continue
            elif term[i - 1].isspace() and term[i + 1].isspace():
                new_term = new_term + term[i]
                i += 1
            else:
                if len(new_term) > 1:
                    new_term = new_term + term[i - 1:]
                else:
                    new_term = term[i:]
                break
        if i == len(term) - 1:  # case: index point on last letter in term
            new_term = new_term + term[-1]

        return new_term

    def Date_Toknize(self, term, text, counter, len_text):
        if term.isdigit():
            if len(term) == 4:
                new_word = term + '-' + self.month_dict[text[counter + 1]]
            else:
                if (counter + 2 < len_text and text[counter + 2].isdigit() and len(text[counter + 2]) == 4):
                    new_word = self.month_dict[text[counter + 1]] + '-' + term + '-' + text[counter + 2]
                    self.per2 = True
                    return new_word
                else:
                    new_word = self.month_dict[text[counter + 1]] + '-' + term
        else:
            if len(text[counter + 1]) == 4:
                new_word = text[counter + 1] + '-' + self.month_dict[term]
            else:
                if counter + 2 < len_text and text[counter + 2].isdigit() and len(text[counter + 2]) == 4:
                    new_word = self.month_dict[term] + '-' + text[counter + 1] + '-' + text[counter + 2]
                    self.per2 = True
                    return new_word
                else:
                    new_word = self.month_dict[term] + '-' + text[counter + 1]
        self.per = True
        return new_word


    def clean_word(self,term):
        if term[0] == '@' or term[-1] == '%':
            return term
        new_words =[]
        counter =-1
        start_index = 0
        for l in term:
            counter +=1
            if (ord(l) <48) or (ord(l) > 57 and ord(l)< 65) or (ord(l) > 90 and ord(l) < 97) or ord(l) > 122:
                if counter == start_index:
                    start_index += 1
                    continue
                new_words.append(term[:counter])
                term = term[counter+1:]
                counter = -1
                start_index = 0
                continue
        new_words.append(term[start_index:])
        if len(new_words) == 1:
            return new_words[0]
        self.words_with_garbage.extend(new_words)
        return new_words


