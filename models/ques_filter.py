import random
import os
import nltk 
import nltk.corpus
from nltk.corpus import nps_chat
from nltk.tokenize import TweetTokenizer
import pickle
import re

SEED = 1
MODEL_NAME = 'qdet.pkl'

class TokenizedCleaner(object):
    PUNCTUATIONS = ["''", "'", "``", "`", "-LRB-", "-RRB-", "-LCB-", "-RCB-", \
        ".", "?", "!", ",", ":", "-", "--", "...", ";"] 

    def __init__(self):
        super(TokenizedCleaner, self).__init__()

    def clean_sent(self, sent):
        sent = sent.lower()
        tokens = nltk.word_tokenize(sent)
        tokenized_sent = ' '.join([w for w in tokens \
                    if w not in self.PUNCTUATIONS])
        return tokenized_sent

class QuestionDetector(object):
    #Class Initialier:
    #- Creates naive bayes classifier using nltk nps_chat corpus and custom ques dataset
    #- Initializes Tweet tokenizer
    #- Initializes question words set to be used
    def __init__(self, use_classifier=False):

        with open('txt/ques_word.txt', 'r', encoding='utf-8') as fid:
            Question_Words = [line.strip() for line in fid]
        special_ques_words = ['what', 'who', 'which', 'whose', 'whom', 'when', 'where', 'why', 'how']
        
        self.Question_Words_Set = set(Question_Words)
        self.special_ques_words_set = set(special_ques_words)
        self.general_ques_words_set = self.Question_Words_Set - self.special_ques_words_set

        self.classifier = None
        self.use_classifier = use_classifier

    #Private method, Gets the word vector from sentance
    def __dialogue_act_features(self,sentence):
        features = {}
        # gram N feature
        gram3 = set()
        gram4 = set()
        gram5 = set()
        gram6 = set()
        sent = '<bos> %s <eos>' % sentence
        words = sent.split(' ')

        for i in range(len(words) - 2):
            w = (words[i], words[i+1], words[i+2])
            gram3.add(w)
        for i in range(len(words) - 3):
            w = (words[i], words[i+1], words[i+2], words[i+3])
            gram4.add(w)
        for i in range(len(words) - 4):
            w = (words[i], words[i+1], words[i+2], words[i+3], words[i+4])
            gram5.add(w)
        for i in range(len(words) - 5):
            w = (words[i], words[i+1], words[i+2], words[i+3], words[i+4], words[i+5])
            gram6.add(w)
        
        for gram in gram3:
            if '<bos>' in gram and '<eos>' not in gram:
                features['contains({})'.format(' '.join(gram))] = True
        for gram in gram4:
            if '<bos>' in gram and '<eos>' not in gram:
                features['contains({})'.format(' '.join(gram))] = True
        for gram in gram5:
            if '<bos>' in gram and '<eos>' not in gram:
                features['contains({})'.format(' '.join(gram))] = True
        for gram in gram6:
            if '<bos>' in gram and '<eos>' not in gram:
                features['contains({})'.format(' '.join(gram))] = True

        return features

    def load_model(self):
        if self.use_classifier:
            self.classifier = pickle.load(open(MODEL_NAME, 'rb'), encoding='bytes')

    #Public Method, Returns 'True' if sentance is predicted to be a question, returns 'False' otherwise
    def IsQuestion(self, sentence):
        tokens = sentence.split(' ')

        # sentences without question words are impossible 
        if len(self.Question_Words_Set.intersection(tokens)) == 0:
            return False

        # sentences with (am|is|are|was|were) beginning can not be used
        if bool(re.match(r"\b(am|is|are|was|were|isnt|arent|wasnt|werent)\b", sentence)):
            return True

        # `what a/an...` exclamation must can be used
        if bool(re.match(r"\bwhat an?\b", sentence)):
            return False

        # ques noun words head can't be used
        if bool(re.match(r"\b(what|who|which|whose|whom|whats|whos)\b", sentence)):
            return True

        # ques adv words + (a|an|the|this|that|...) may can be used by remove the heading ques words
        if bool(re.match(r"\b(when|where|why|how) (a|an|the|this|that|these|those)\b", sentence)):
            return False

        if tokens[0] in self.special_ques_words_set \
        and tokens[1] in self.general_ques_words_set:
            return True
        
        if self.use_classifier:
            predicted = self.classifier.classify(self.__dialogue_act_features(sentence))
            return predicted == 'Ques'
        else:
            return False

    def train(self):
        cleaner = TokenizedCleaner()
        
        # collect tweet data
        posts = nltk.corpus.nps_chat.xml_posts()
        tweet_data = [(cleaner.clean_sent(post.text), post.get('class')) for post in posts]
        tweet_data = [item for item in tweet_data if len(item[0]) > 0]

        # collect custom data
        with open('txt/ques_train_corpus/positive.txt', 'r', encoding='utf-8') as f:
            custom_positive = set([l.strip() for l in f])
            custom_positive = [(cleaner.clean_sent(sent), 'whQuestion') for sent in custom_positive]
        with open('txt/ques_train_corpus/negative.txt', 'r', encoding='utf-8') as f:
            custom_negative = set([l.strip() for l in f])
            custom_negative = [(cleaner.clean_sent(sent), 'NotQues') for sent in custom_negative]

        data = custom_negative + custom_positive + tweet_data
        featuresets = [(self.__dialogue_act_features(item[0]), item[1]) for item in data]

        positive = [(x[0], 'Ques') for x in featuresets if x[1] in ['whQuestion', 'ynQuestion']]
        negative = [(x[0], 'NotQues') for x in featuresets if not x[1] in ['whQuestion', 'ynQuestion']]

        # keep the num of pos and neg balanced
        random.seed(SEED)
        if len(positive) > len(negative):
            print("Sample positive")
            random.shuffle(positive)
            positive = positive[:len(negative)]
        else:
            print("Sample negative")
            random.shuffle(negative)
            negative = negative[:len(positive)]

        featuresets = positive + negative

        random.seed(SEED)
        random.shuffle(featuresets)
        size = int(len(featuresets) * 0.1)
        train_set, test_set = featuresets[size:], featuresets[:size]
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        pickle.dump(classifier, open(MODEL_NAME, 'wb'))

        print('Eval on validation set:')
        print('Accuracy: ', nltk.classify.accuracy(classifier, test_set))
        classifier.show_most_informative_features(20)

if __name__ == '__main__':
    qdet = QuestionDetector()
    qdet.train()
