"""
Module that provides a class that filters profanities
Modified by jianjie
"""

__author__ = "leoluk & jianjieluo"
__version__ = '0.0.2'

import random
import re

class ProfanitiesFilter(object):
    def __init__(self, filterlist, ignore_case=True, replacements="$@%-?!", 
                 complete=True, inside_words=False):
        """
        Inits the profanity filter.

        filterlist -- a list of regular expressions that
        matches words that are forbidden
        ignore_case -- ignore capitalization
        replacements -- string with characters to replace the forbidden word
        complete -- completely remove the word or keep the first and last char?
        inside_words -- search inside other words?

        """
        cw = []
        for sent in filterlist:
            words = sent.split(' ')
            cw.append((len(words), sent))
        cw = list(sorted(cw, reverse=True))
        filterlist = [c[1] for c in cw]

        self.badwords = filterlist
        self.ignore_case = ignore_case
        self.replacements = replacements
        self.complete = complete
        self.inside_words = inside_words

        # compile the regex
        self.r = self._compile_re()

    def _make_clean_word(self, length):
        """
        Generates a random replacement string of a given length
        using the chars in self.replacements.

        """
        return ''.join([random.choice(self.replacements) for i in
                  range(length)])

    def __replacer(self, match):
        value = match.group()
        if self.complete:
            return self._make_clean_word(len(value))
        else:
            return value[0]+self._make_clean_word(len(value)-2)+value[-1]

    def _compile_re(self):
        regexp_insidewords = {
            True: r'(%s)',
            False: r'\b(%s)\b',
            }

        regexp = (regexp_insidewords[self.inside_words] % 
                  '|'.join(self.badwords))

        r = re.compile(regexp, re.IGNORECASE if self.ignore_case else 0)
        return r

    def clean(self, text):
        """Cleans a string from profanity."""
        return self.r.sub(self.__replacer, text)

    def is_profanity(self, text):
        return bool(self.r.search(text))


if __name__ == '__main__':

    f = ProfanitiesFilter(['bad', 'un\w+'], replacements="-")      
    example = "I am doing bad ungood badlike things."

    print(f.clean(example))
    # Returns "I am doing --- ------ badlike things."

    f.inside_words = True
    f.r = f._compile_re()    
    print(f.clean(example))
    # Returns "I am doing --- ------ ---like things."

    f.complete = False
    f.r = f._compile_re()
    print(f.clean(example))
    # Returns "I am doing b-d u----d b-dlike things."