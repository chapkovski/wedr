from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, encode_word_with_alphabet
import emojis
import logging
logger=logging.getLogger(__name__)

class MyPage(Page):
    def vars_for_template(self):
        logger.critical(emojis.db.get_categories())
        res=encode_word_with_alphabet('hello')
        return {

            **res
        }


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
