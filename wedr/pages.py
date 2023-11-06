from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, encode_word_with_alphabet
import emojis
import logging

logger = logging.getLogger(__name__)



class GameSettingWP(WaitPage):
    template_name = 'wedr/FirstWP.html'
    group_by_arrival_time = True
    body_text = "If you wait for more than 5 minutes, please submit NOPARTNER code in prolific and we will compensate you for your time! Thank you!"

    after_all_players_arrive = 'set_up_game'


class WorkingPage(Page):
    live_method = 'process_data'

    def is_displayed(self):
        return not self.group.completed

    def js_vars(self):
        word = Constants.words[self.round_number - 1]
        res = encode_word_with_alphabet(word)
        messages = self.group.messages.all()
        formatted_messages = [
            {
                "type": "message",
                "who": i.owner.participant.code,
                "message": i.message,
                "own": i.owner == self.player,
            }
            for i in messages
        ]
        res.update({'messages': formatted_messages})
        return res

    def post(self):
        logger.info(f'Got data: {self.request.POST}')
        return super().post()


page_sequence = [


    GameSettingWP,
    WorkingPage,
]
