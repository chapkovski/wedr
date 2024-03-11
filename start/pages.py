from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import json
from json import JSONDecodeError

class FirstWP(WaitPage):
    group_by_arrival_time = True
    body_text = "If you wait for more than 5 minutes, please submit NO_PARTNER code in Prolific and we will compensate you for your time! Thank you!"

    def is_displayed(self):
        return self.round_number == 1


class Intro(Page):
    def is_displayed(self):
        return self.round_number == 1


class CQPage(Page):
    pass


class PolPage(Page):
    def is_displayed(self):
        return self.round_number == 1

    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:
            json_data= json.loads(raw_data)
            print(json_data)
            self.player.survey_data = json.dumps(json_data)
        except JSONDecodeError:
            print('No data')
        print('*' * 100)
        return super().post()


page_sequence = [
    FirstWP,
    PolPage,
    Intro,
    CQPage,
]
