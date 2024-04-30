from otree.api import Currency as c, currency_range, Submission
from . import pages
from ._builtin import Bot

from .models import Constants
import json
import random

class PlayerBot(Bot):
    def play_round(self):
        raw_data = json.dumps({'books': random.randint(0,5),
                               'cars': random.randint(0,5),
                               'cities': random.randint(0,5),
                               'immigration': random.randint(0,5),
                               'partisanship': random.randint(0,5),
                               'women': 1})
        yield Submission(pages.PolPage, dict(survey_data=raw_data,
                                             ), check_html=False)
