from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, encode_word_with_alphabet
import emojis
import logging
logger=logging.getLogger(__name__)

class MyPage(Page):
    def js_vars(self):
        word = Constants.words[self.round_number - 1]
        res = encode_word_with_alphabet(word)

        return res


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage,
                 # ResultsWaitPage, Results
                 ]
