from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, encode_word_with_alphabet
import emojis
import logging

logger = logging.getLogger(__name__)


class Intro(Page):
    def is_displayed(self):
        return self.round_number == 1


class WorkingPage(Page):
    live_method = 'process_input'

    def js_vars(self):
        word = Constants.words[self.round_number - 1]
        res = encode_word_with_alphabet(word)

        return res

    def post(self):
        print(f'Got data: {self.request.POST}')
        start_time = self.request.POST.get('startTime')
        end_time = self.request.POST.get('endTime')
        time_elapsed = float(self.request.POST.get('timeElapsed'))
        if start_time and end_time and time_elapsed:
            try:
                self.player.start_time = start_time
                self.player.end_time = end_time
                self.player.time_elapsed = time_elapsed


            except Exception as e:
                print(e)
                logger.error("Failed to set duration of decision page")
        return super().post()


page_sequence = [Intro,
                 WorkingPage,
                 ]
