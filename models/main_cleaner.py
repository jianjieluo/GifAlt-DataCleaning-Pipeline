# stage == 1 --> candidates with a high rate of token repetition are discarded
# stage == 2 --> candidates with no determiner, no noun, or no preposition are discarded   
#                candidates with a high noun ratio are also discarded
#                candidates that score too high or too low on the polarity annotations are discarded
# stage == 3 --> remove question

import os
import re
import nltk
from nltk.corpus import stopwords, words
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from config import cfg
from models.ques_filter import QuestionDetector


class MainCleaner(object):
    def __init__(self):
        super(MainCleaner, self).__init__()
        self.max_noun_ratio = cfg.MAX_NOUN_RATIO
        self.sent_pos = cfg.SENT_POS
        self.pos_dict = {
            'CC': 'CC', 'CD': 'CD', 'EX': 'EX', 'FW': 'FW', 'IN': 'IN', 'LS': 'LS', 'MD': 'MD',
            'DT': 'DT', 'PDT': 'DT',
            'RP': 'RP', 'TO': 'TO', 'UH': 'UH',
            'WDT': 'WDT', 'WP': 'WP', 'WP$': 'WP', 'WRB': 'WRB',
            'POS': 'POS', 'PRP': 'PRP', 'PRP$': 'PRP',
            'JJ': 'JJ', 'JJR': 'JJ', 'JJS': 'JJ', 
            'NN': 'NN', 'NNS': 'NN', 'NNP': 'NN', 'NNPS': 'NN',
            'RB': 'RB', 'RBR': 'RB', 'RBS': 'RB',     
            'VB': 'VB', 'VBG': 'VB', 'VBD': 'VB', 'VBN': 'VB', 'VBP': 'VB', 'VBZ': 'VB',
        }

        self.max_freq = cfg.MAX_FREQ
        self.max_polarity = cfg.MAX_POLARITY
        self.min_polarity = cfg.MIN_POLARITY
        self.polarity_scorer = SIA()

        self.qdet = QuestionDetector()
        self.stop_words = set(stopwords.words('english'))
        
    def clean_sent(self, sent, tag_words, stage):
        if stage == 1:
            return self.clean_sent_by_freq(sent)
        elif stage == 2:
            return self.clean_sent_by_tag(sent, tag_words)
        elif stage == 3:
            return self.clean_sent_by_question(sent)
        else:
            raise NotImplementedError

    def load_model(self, stage):
        if stage == 3:
            self.qdet.load_model()

    def clean_sent_by_freq(self, sent):
        tokens = sent.split(' ')
        core_words = [w for w in tokens if w not in self.stop_words]

        if len(core_words) == 0:
            return 'none'

        # candidates with a high rate of token repetition are discarded
        words_freq = {}
        for w in core_words:
            words_freq[w] = words_freq.get(w, 0) + 1
        freq = [words_freq[word] for word in words_freq]
        max_freq = max(freq)
        if max_freq >= self.max_freq:
            return 'none'
        return sent

    def clean_sent_by_question(self, sent):
        if self.qdet.IsQuestion(sent) == True:
            return 'none'
        else:
            return sent

    def clean_sent_by_tag(self, sent, tag_words):
        words = sent.split(' ')

        # 1. candidates with no determiner, no noun, or no preposition are discarded   
        tag_freq = {}
        for tag_word in tag_words:
            if tag_word in self.pos_dict:
                tag = self.pos_dict[tag_word]
                tag_freq[tag] = tag_freq.get(tag, 0) + 1
                
        for pos in self.sent_pos:
            if pos not in tag_freq:
                return 'none'
        
        # 2. candidates with a high noun ratio are also discarded
        if tag_freq['NN'] / len(words) > self.max_noun_ratio:
            return 'none'
        
        # 3. candidates that score too high or too low on
        # the polarity annotations are discarded
        polarity_score = self.polarity_scorer.polarity_scores(sent)
        polarity_score = polarity_score['compound']
        if polarity_score >= self.max_polarity or polarity_score <= self.min_polarity:
            return 'none'

        return sent
