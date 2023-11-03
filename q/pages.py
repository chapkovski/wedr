from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from django.shortcuts import redirect

class Feedback(Page):
    form_model = "player"
    form_fields = ["instructions_clarity","feedback"]



class FinalForProlific(Page):


    def get(self):
        full_return_url = self.session.config.get("prolific_return_url")
        if full_return_url:
            return redirect(full_return_url)
        FALLBACK_URL = "https://cnn.com"
        return redirect(FALLBACK_URL)




page_sequence = [Feedback, FinalForProlific]