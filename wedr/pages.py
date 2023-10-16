from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, encode_word_with_alphabet
import emojis
import logging
logger=logging.getLogger(__name__)


class MyPage(Page):
    live_method = 'process_input'
    def js_vars(self):
        word = Constants.words[self.round_number - 1]
        res = encode_word_with_alphabet(word)

        return res
    def post(self):
        print(f'Got data: {self.request.POST}')
        try:
            self.player.start_time= self.request.POST.get('startTime')
            self.player.end_time= self.request.POST.get('endTime')
            self.player.time_elapsed= float(self.request.POST.get('timeElapsed'))
        except Exception as e:
            print(e)
            logger.error("Failed to set duration of decision page")
        return super().post()

class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage,
                 # ResultsWaitPage, Results
                 ]
