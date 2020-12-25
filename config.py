import os
import os.path as osp
import numpy as np

from easydict import EasyDict as edict

# https://www.guru99.com/pos-tagging-chunking-nltk.html
# Abbreviation	      Meaning
# CC	              coordinating conjunction
# CD	              cardinal digit
# DT	              determiner
# EX	              existential there
# FW	              foreign word
# IN	              preposition/subordinating conjunction
# JJ	              adjective (large)
# JJR	              adjective, comparative (larger)
# JJS	              adjective, superlative (largest)
# LS	              list market
# MD	              modal (could, will)
# NN	              noun, singular (cat, tree)
# NNS	              noun plural (desks)
# NNP	              proper noun, singular (sarah)
# NNPS	              proper noun, plural (indians or americans)
# PDT	              predeterminer (all, both, half)
# POS	              possessive ending (parent\ 's)
# PRP	              personal pronoun (hers, herself, him,himself)
# PRP$	              possessive pronoun (her, his, mine, my, our )
# RB	              adverb (occasionally, swiftly)
# RBR	              adverb, comparative (greater)
# RBS	              adverb, superlative (biggest)
# RP	              particle (about)
# TO	              infinite marker (to)
# UH	              interjection (goodbye)
# VB	              verb (ask)
# VBG	              verb gerund (judging)
# VBD	              verb past tense (pleaded)
# VBN	              verb past participle (reunified)
# VBP	              verb, present tense not 3rd person singular(wrap)
# VBZ	              verb, present tense with 3rd person singular (bases)
# WDT	              wh-determiner (that, what)
# WP	              wh- pronoun (who)
# WRB	              wh- adverb (how)

__C = edict()
# Consumers can get config by:
#   from fast_rcnn_config import cfg
cfg = __C

__C.MIN_LEN = 5

__C.MAX_LEN = 80

__C.MAX_POLARITY = 0.9

__C.MIN_POLARITY = -0.9

__C.MAX_NOUN_RATIO = 0.5

__C.SENT_POS = ['DT', 'NN', 'IN']

__C.MAX_FREQ = 3

__C.CACHE_DIR = 'cache'

__C.PIPELINE_TYPE = 'SOFT' # HARD, SOFT

__C.BASE_GID = 0