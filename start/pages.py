from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, calculate_grouped_averages
import json
from json import JSONDecodeError
from pprint import pprint

class FirstWP(WaitPage):
    group_by_arrival_time = True
    body_text = "If your partner does not show up after 5 minutes, please submit NO_PARTNER code in Prolific and we will compensate you for your time."

    def is_displayed(self):
        return self.round_number == 1


class Intro(Page):
    def vars_for_template(self):
        return dict(minutes=int(self.session.config.get('time_for_work', 600) / 60))


class Instructions1(Page):
    def vars_for_template(self):
        return dict(show_images=True)


class Instructions2(Page):
    pass


class CQPage(Page):
    pass


class PolPage(Page):
    def is_displayed(self):
        return self.round_number == 1

    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:
            json_data = json.loads(raw_data)
            averages = calculate_grouped_averages(json_data)
            self.player.polarizing_score = averages.get('polarizing', 0)
            self.player.neutral_score = averages.get('neutral', 0)
            self.player.survey_data = json.dumps(json_data)
            self.participant.vars['survey_data'] = json_data
            self.participant.vars['polarizing_score'] = self.player.polarizing_score
            self.participant.vars['neutral_score'] = self.player.neutral_score


        except JSONDecodeError:
            print('No data')
        print('*' * 100)
        return super().post()


page_sequence = [
    FirstWP,

    # Intro,
    # Instructions1,
    # Instructions2,
    # CQPage,
    PolPage,
]
