from otree.api import Currency as c, currency_range, Submission
from . import pages
from ._builtin import Bot

from .models import Constants
import json
import random



class PlayerBot(Bot):
    def play_round(self):
        yield pages.Consent, {"consent_accept": True}
        yield pages.Intro,
        yield pages.Instructions1,
        yield pages.Instructions2,
        yield pages.CQPage,

