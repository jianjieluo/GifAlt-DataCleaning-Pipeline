import nltk
import re
import numpy as np
import functools
import json

import spacy
import en_core_web_lg

import sys
sys.path.append('models/text_hyper_transformation')
from rules import *


class Hypernymizer(object):
    PUNCTUATIONS = ["''", "'", "``", "`", "-LRB-", "-RRB-", "-LCB-", "-RCB-", \
        ".", "?", "!", ",", ":", "-", "--", "...", ";"] 

    def __init__(self):
        print("Load language model...")
        self.nlp = en_core_web_lg.load()
        print("Done!")

        self.useless_pattern = self._build_useless_pattern()

        self.pos_dict = {
            'JJ': 'JJ', 'JJR': 'JJ', 'JJS': 'JJ', 
            'NN': 'NN', 'NNS': 'NN', 'NNP': 'NN', 'NNPS': 'NN',
        }

        with open('txt/people_name.txt', 'r', encoding='utf-8') as fid:
            data = set([l.strip() for l in fid])
        self.person_pattern = r"\b(%s)\b" % '|'.join(data)

        # predefined vocab name refine dict:
        with open('txt/name_refine.json', 'r', encoding='utf-8') as f:
            self.refined_name = json.load(f)
        self.refined_name_set = set(self.refined_name.keys())

        grammar1 = r"""
                    CHUNK: {<IN>+<PDT>?<DT|PRP\$>?<JJ>*<NN>+}
                """
        self.chunk_parser1 = nltk.RegexpParser(grammar1)
        grammar2 = r"""
                    NP: {<NN><NN>+}
                    DTS: {<DT><DT>+}
                """
        self.chunk_parser2 = nltk.RegexpParser(grammar2)
        grammar3 = r"""
                    DTCC: {<DT>+<CC>+}
                    UH: {<UH>}
                """
        self.chunk_parser3 = nltk.RegexpParser(grammar3)
        
    def _build_useless_pattern(self):
        # Month
        month = [x.lower() for x in MONTH]
        in_month = ['in ' + x for x in month]
        month += in_month
        month.remove('may')
        # Maybe Others...

        # Combined
        useless = month
        r = r'\b(%s)\b' % '|'.join(useless)
        return r
        
    def noun_chunker_simplify(self, text):
        # Use name entity, noun chunkers, pos tags
        doc = self.nlp(text)
        person_li = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        dt_li = set([token.text for token in doc if token.tag_ in ['DT', 'PDT']])

        def contain_person(chunk):
            for p in person_li:
                if p in chunk:
                    return True
            return False

        li = []
        for chunk in doc.noun_chunks:
            src = chunk.text

            if contain_person(src):
                continue
            
            splits = src.split()
            dst = ' '.join([splits[0], chunk.root.text]) \
                  if splits[0] in dt_li \
                  else chunk.root.text
            li.append((src, dst))
        
        for item in li:
            text = text.replace(item[0], item[1])
        
        return ' '.join(text.split())

    def name_entity_hyper(self, text):
        # only use name entity
        with self.nlp.disable_pipes("tagger", "parser"):
            doc = self.nlp(text)
        hyper_classes = REPLACE_CLASSES + DROP_CLASSES
        newString = text
        # reversed to not modify the offsets of other entities when substituting
        for e in reversed(doc.ents):
            if e.label_ in hyper_classes:
                start = e.start_char
                end = start + len(e.text)
                newString = newString[:start] + e.label_ + newString[end:]
        return newString

    def remove_pos_tag_patterns(self, text):
        text = self.pos_tag_only(text)
        result = self.chunk_parser1.parse(text)
        terms = [[e[0]] if isinstance(e, tuple) else [w for w,t in e] for e in result]
        res = [x for x in terms if len(set(x).intersection(set(DROP_CLASSES))) == 0]
        if len(res) == 0:
            return 'none'
        text = ' '.join(functools.reduce(lambda x,y: x+y,res))

        # Remove duplicated <NN>+|<DT>+ pattern
        text = self.pos_tag_only(text)
        result = self.chunk_parser2.parse(text)
        terms = [e[0] if isinstance(e, tuple) else [w for w,t in e][-1] for e in result]
        text = ' '.join(terms)

        # Remove <DT>+<CC>+ or <UH> pattern
        text = self.pos_tag_only(text)
        result = self.chunk_parser3.parse(text)
        terms = [e[0] for e in result if isinstance(e, tuple)]
        text = ' '.join(terms)

        return text

    def pos_tag(self, text):
        # only use tagger
        with self.nlp.disable_pipes("parser", "ner"):
            doc = self.nlp(text)
        pos_tags = [
            (token.text, self.pos_dict[token.tag_] if token.tag_ in self.pos_dict else token.tag_) \
            for token in doc
        ]
        return pos_tags

    def pos_tag_only(self, text):
        tokens = text.split(' ')
        spaces = [True] * (len(tokens) - 1) + [False]

        # only use pos tagger, dont use spacy predefined tokenizer
        with self.nlp.disable_pipes("parser", "ner"):
            doc = spacy.tokens.doc.Doc(
                self.nlp.vocab, words=tokens, spaces=spaces)
            for name, proc in self.nlp.pipeline:
                doc = proc(doc)
        pos_tags = [
            (token.text, self.pos_dict[token.tag_] if token.tag_ in self.pos_dict else token.tag_) \
            for token in doc
        ]
        return pos_tags

    def multi2single_head(self, text):
        """
        hard code implement
        """
        text = re.sub(r"^mrs?.? ?[A-Za-z]*", "a PERSON", text)

        text = re.sub(r"^(im|i am)\b", "a PERSON is", text)
        text = re.sub(r"^i\b", "a PERSON", text)
        text = re.sub(r"^he\b", "a man", text)
        text = re.sub(r"^she\b", "a woman", text)
        text = re.sub(r"^they\b", "people", text)

        text = re.sub(r"(a |an )?PERSON (and )?(a |an )?PERSON", "people", text)
        return text

    def transform(self, text):
        text = re.sub(self.useless_pattern, "", text)
        text = ' '.join(text.split())

        text = re.sub(self.person_pattern, "a PERSON", text)
        tokens = text.split(' ')
        # refine the names in vocabulary
        if len(set(tokens) & self.refined_name_set) > 0:
            tokens = [self.refined_name[w] if w in self.refined_name else w for w in tokens]
            text = ' '.join(tokens)

        # Noun Chunker simplify
        text = self.noun_chunker_simplify(text)
        # Name entities hyper transform
        text = self.name_entity_hyper(text)
        # Multi head to single head
        text = self.multi2single_head(text)
        # Remove predefined pos-tag patterns
        text = self.remove_pos_tag_patterns(text)

        # remove whitespace and punctuation
        text = ' '.join(text.split()).lower()
        tokens = text.split(' ')
        text = ' '.join([w for w in tokens \
                    if w not in self.PUNCTUATIONS])

        text = re.sub(r"(a |an )?(person|people) (and )?(a |an )?(person|people)", "people", text)
        text = re.sub(r"(a |an )?(person|people) (and )?(a |an )?(person|people)", "people", text)
        return text

########################### Test Code ##################################

def precook(sent, vocab):
    # similar to basic_cleaner.py
    sent = sent.lower()
    tokens = nltk.word_tokenize(sent)
    tokens = [w for w in tokens if w in vocab]
    sent = ' '.join(tokens)
    sent = sent.strip()
    return sent

def read_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = [l.strip() for l in f]
    return data

if __name__ == '__main__':
    # Unit test
    alt_texts = [
        "Harrison Ford and Calista Flockhart attend the premiere of 'Hollywood Homicide' at the 29th American Film Festival September 5, 2003 in Deauville, France.",
        "Side view of a British Airways Airbus A319 aircraft on approach to land with landing gear down",
        "Two sculptures by artist Duncan McKellar adorn trees outside the derelict Norwich Union offices in Bristol, UK",
        "A Pakistani worker helps to clear the debris from the Taj Mahal Hotel November 7, 2005 in Balakot, Pakistan.",
        "Musician Justin Timberlake performs at the 2017 Pilgrimage Music & Cultural Festival on September 23, 2017 in Franklin, Tennessee."
    ]

    paper_res = [
        "actors attend the premiere at festival.",
        "side view of an aircraft on approach to land with landing gear down",
        "sculptures by person adorn trees outside the derelict offices",
        "a worker helps to clear the debris.",
        "pop artist performs at the festival in a city."
    ]

    wiki_vocab = read_txt('cache/vocab_clean.txt')

    hyper = Hypernymizer()
    results = []
    for alt, gt in zip(alt_texts, paper_res):
        alt = precook(alt.lower(), wiki_vocab)
        res = hyper.transform(alt)
        results.append({
            'Alt-text': alt,
            'Paper': gt,
            'Ours': res
        })

    with open('models/text_hyper_transformation/results.txt', 'w') as fid:
        for item in results:
            for k, v in item.items():
                s = "%s:\t%s\n" % (k, v)
                print(s)
                fid.write(s)
            fid.write("\n")
