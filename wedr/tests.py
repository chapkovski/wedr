from otree.api import Currency as c, currency_range, Submission
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):
    def play_round(self):
        pass
        # if self.round_number == 1:
        #     yield pages.MatchPage2
        #
        # yield Submission(pages.WorkingPage, {}, check_html=False)

