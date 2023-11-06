from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

class FirstWP(WaitPage):
    group_by_arrival_time = True
    body_text = "If you wait for more than 5 minutes, please submit NOPARTNER code in prolific and we will compensate you for your time! Thank you!"
    def is_displayed(self):
        return self.round_number == 1

class Intro(Page):
    def is_displayed(self):
        return self.round_number == 1
class CQPage(Page):
    pass


page_sequence = [
    FirstWP,
    Intro,
    CQPage,
]
