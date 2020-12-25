from models.profanities_filter import ProfanitiesFilter as BaseProfanitiesFilter

import warnings
warnings.filterwarnings("ignore")
import profanity_check # there are warnings abount sk-learn version when import this package
import profanity_filter
import profanityfilter 
from better_profanity import profanity

class StrongProfanitiesFilter(BaseProfanitiesFilter):
    def __init__(self, filterlist, ignore_case=True, replacements="$@%-?!",
                 complete=True, inside_words=False):
        super(StrongProfanitiesFilter, self).__init__(
            filterlist, ignore_case, replacements, complete, inside_words)

        # https://pypi.org/project/profanity-filter/
        self.profanity_filter = profanity_filter.ProfanityFilter()

        # https://pypi.org/project/better-profanity/
        profanity.load_censor_words()

        # https://github.com/areebbeigh/profanityfilter
        self.profanityfilter = profanityfilter.ProfanityFilter()

    def is_profanity(self, text):
        # Stack the profanity checker from fast to slow

        # 1. https://pypi.org/project/better-profanity/
        if profanity.contains_profanity(text):
            return True

        # 2. the base method in parent class
        if super(StrongProfanitiesFilter, self).is_profanity(text):
            return True

        # 3. https://pypi.org/project/profanity-check/
        if profanity_check.predict([text])[0] == 1:
            return True

        # # 4. https://pypi.org/project/profanity-filter/
        # if self.profanity_filter.is_profane(text):
        #     return True

        # # 5. https://github.com/areebbeigh/profanityfilter
        # if self.profanityfilter.is_profane(text):
        #     return True

        return False


class StrongerProfanitiesFilter(StrongProfanitiesFilter):
    def __init__(self, filterlist, ignore_case=True, replacements="$@%-?!",
                 complete=True, inside_words=False):
        super(StrongerProfanitiesFilter, self).__init__(
            filterlist, ignore_case, replacements, complete, inside_words)

    def is_profanity(self, text):
        # Stack the profanity checker from fast to slow

        # 4. https://pypi.org/project/profanity-filter/
        if self.profanity_filter.is_profane(text):
            return True

        # 5. https://github.com/areebbeigh/profanityfilter
        if self.profanityfilter.is_profane(text):
            return True

        return False


if __name__ == "__main__":
    tests = [
        'the nazis in the white house',
        'tardew valley im gay and you can be gay in this',
        'you are a bullshit',
        'you are the son-of-a-bitch',

        'fascist',
        'traitor of the people',
        'scum',
        'rabble',
        'parasites',
        'turk town',
        'muslim thieves',
        'north african repeat offenders',
        'niggers',
        'ass',
        'crap',
        'shit',
        'dumb',
        'drivel',
        'to vomit'
    ]

    # load basic blacklist
    blacklist = set()
    with open('txt/blacklist.txt') as fid:
        for line in fid:
            blacklist.add(line.strip().lower())

    checker = StrongProfanitiesFilter(blacklist)

    res = []
    for text in tests:
        res.append(str(checker.is_profanity(text)) + '\t' + text)

    print('Detected Result: ')
    for s in res:
        print(s)

    # # Test each package time
    # tests = [
    #     'the nazis in the white house',
    #     'tardew valley im gay and you can be gay in this',
    #     'you are a bullshit',
    #     'you are the son-of-a-bitch',
    # ]

    # from time import time
    
    # tests = tests * 5
    # sent_num = len(tests)

    # base_checker = BaseProfanitiesFilter(blacklist)
    # t1 = time()
    # for sent in tests:
    #     temp = base_checker.is_profanity(sent)
    # t2 = time()
    # print("Base profanities filter time: \t", (t2 - t1) / sent_num)
    # # 0.0001998424530029297

    # t1 = time()
    # for sent in tests:
    #     checker.profanityfilter.is_profane(sent)
    # t2 = time()
    # print("self.profanityfilter time: \t", (t2 - t1) / sent_num)
    # # 0.16519991159439087

    # t1 = time()
    # for sent in tests:
    #     temp = profanity_check.predict([sent])[0] == 1
    # t2 = time()
    # print("profanity_check time: \t", (t2 - t1) / sent_num)
    # # 0.0016998291015625

    # t1 = time()
    # for sent in tests:
    #     temp = checker.profanity_filter.is_profane(sent)
    # t2 = time()
    # print("self.profanity_filter time: \t", (t2 - t1) / sent_num)
    # # 0.033400225639343264

    # t1 = time()
    # for sent in tests:
    #     temp = profanity.contains_profanity(sent)
    # t2 = time()
    # print("better_profanity time: \t", (t2 - t1) / sent_num)
    # # 0.00010017156600952148