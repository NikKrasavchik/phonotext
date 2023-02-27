import re
from scipy import sparse as sp
import pickle
import numpy as np
import pandas as pd

class Corpus:
    def __init__(self, texts, alphabet="rus"):
        if alphabet == "rus": self.alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        elif alphabet == "en": self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        elif alphabet == "en+": self.alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        elif alphabet == "rus+": self.alphabet = "0123456789абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        elif alphabet == "rus+en": self.alphabet = "0123456789abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        else: self.alphabet = alphabet
        self.__all_symbols = {j:i for i,j in enumerate("абвгдеёжзийклмнопрстуфхцчшщъыьэюя", 1)}
        
        self.texts = [self.__preprocess_text(text) for text in texts]
        
        self.trained=False
        
    def __preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r"\d+", " ", text) # delete didgits
        text = re.sub(r"\W+ ", " ", text) # delete special chars
        text = re.sub(r"_+", " ", text)
        text = re.sub(r"\s+", " ", text) # delete extra spaces
        return text
    
    def get_words(self, text, vector=False):
        if not self.trained:
            raise RuntimeError("Model is not trained")
        text = self.__preprocess_text(text)
        if not vector:
            return text.split()
        else:
            return [self.get_word_vector(word) for word in text.split()]
        
    def __dict_sum(self, a, b):
        for k, v in b.items():
            a[k] = a.get(k, 0) + v
    
    def __calc_seq_number(self, seq):
        s = 0
        letters = len(self.__all_symbols)
        for power, sym in enumerate(seq[::-1]):
            s += self.__all_symbols.get(sym,0)*letters**power
        return(s)
    
    def __seq_to_number(self, seq):
        if not self.__all_terms.get(seq, False):
            self.__all_terms[seq] = len(self.__all_terms)+1 #self.__calc_seq_number(seq)
        return self.__all_terms[seq]
    
    def __get_word_numbers(self, word, get_len):
        l = len(word)
        numbers = {}
        for i in range(self.__min_num, self.__max_num+1):
            for j in range(l-i+1):
                if self.trained:
                    num = self.__all_terms.get(word[j:j+i], 0)
                else:
                    num = self.__seq_to_number(word[j:j+i])
                numbers[num] = numbers.get(num, 0) + i if get_len else 1
        if self.__min_pre_num > 0:
            for i in range(self.__min_pre_num, min(len(word), self.__max_pre_num+1)):
                num = self.__seq_to_number("#" + word[:i])
                numbers[num] = numbers.get(num, 0) + i if get_len else 1
        if self.__min_suf_num > 0:
            for i in range(self.__min_suf_num, min(len(word), self.__max_suf_num+1)):
                num = self.__seq_to_number(word[-i:] + "#")
                numbers[num] = numbers.get(num, 0) + i if get_len else 1
        return numbers
    
    def get_word_vector(self, word, get_len = False):
        if not self.trained:
            raise RuntimeError("Model is not trained")
        terms = self.__get_word_numbers(word, get_len)
        
        a = list(terms.values())# + [len(word)]
        b = list(terms.keys())  # + [self.max_num-1]
        c = [0, len(b)]
        return sp.csr_matrix((a,b,c), (1, self.max_num))
    
    def __process_text(self, text, get_len):
        if not text:
            return [0],[0],1
        words = text.split()
        terms = {}
        for word in words:
            if (self.__stop_words is None) or (word not in self.__stop_words):
                self.__dict_sum(terms, self.__get_word_numbers(word, get_len))
        
        val = list(terms.values()) #+ [np.mean([len(i) for i in words])]
        a = val # Calculating term frequency
        b = list(terms.keys())   #+ [self.max_num-1]
        c = len(b)
        return a, b, c
    
    def fit(self, min_num=2, max_num=4, 
            min_pre_num=1, max_pre_num=3, 
            min_suf_num=1, max_suf_num=3, 
            stop_words=None, use_length=False, 
            terms=None, tfidf=False):
        import numpy as np
        
        self.trained=False
        
        self.__max_num = max_num
        self.__min_num = min_num
        
        self.__max_pre_num = max_pre_num
        self.__max_suf_num = max_suf_num
        
        self.__min_pre_num = min_pre_num
        self.__min_suf_num = min_suf_num
        
        self.__stop_words = stop_words
        if terms is None:
            self.__all_terms = {}

        else:
            self.__all_terms = terms
        
        self.__doc_freq = {}            
        
        self.data = []
        self.ind = []
        self.iptr = [0]
        s = 0
        for text in self.texts:
            a,b,c = self.__process_text(text, use_length)
            for term in b:
                self.__doc_freq[term] = self.__doc_freq.get(term, 0) + 1
            self.data += a
            self.ind += b
            s += c
            self.iptr.append(s)
        

        #Apply TF-IDF on terms
        if tfidf:
            docs = len(self.texts)
            self.data = [val*np.log(docs/self.__doc_freq[term]) for val, term in zip(self.data, self.ind)]
        
        self.max_num=len(self.__all_terms)+1 
        self.trained = True

    def get_terms(self):
        if not self.trained:
            raise RuntimeError("Model is not trained")
        return self.__all_terms.copy()

    def __call__(self):
        if not self.trained:
            raise RuntimeError("Model is not trained")
        return sp.csr_matrix((self.data, self.ind, self.iptr), (len(self.iptr)-1, self.max_num)) 