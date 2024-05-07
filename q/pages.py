from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from django.shortcuts import redirect


class Feedback(Page):
    form_model = "player"
    form_fields = ["instructions_clarity", "purpose", "feedback"]


class FinalForProlific(Page):

    def get(self):
        full_return_url = self.session.config.get("prolific_return_url", "https://cnn.com")
        return redirect(full_return_url)


class Q1(Page):
    pass


page_sequence = [Q1, Feedback, FinalForProlific]
