from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from django.shortcuts import redirect
import json
import logging
from json import JSONDecodeError
from pprint import pprint
logger = logging.getLogger(__name__)
class Feedback(Page):
    form_model = "player"
    form_fields = ["instructions_clarity", "purpose", "feedback"]


class FinalForProlific(Page):

    def get(self):
        full_return_url = self.session.config.get("prolific_return_url", "https://cnn.com")
        return redirect(full_return_url)


class Q1(Page):
    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:

            json_data = json.loads(raw_data)
            pprint(json_data)
            for k, v in json_data.items():
                try:
                    setattr(self.player, k, str(v))
                except AttributeError as e:
                    logger.error(
                        f'No such field at player level: {k} for value {v}. Player {self.player.participant.code}. Error: {e}')

        except JSONDecodeError as e:
            logger.error(str(e))
        print('*' * 100)
        return super().post()


page_sequence = [Feedback,Q1,  FinalForProlific]
