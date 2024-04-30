from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
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
            print('*' * 100)
            print(raw_data)
            print('*' * 100)
            json_data = json.loads(raw_data)
            pprint(raw_data)
            threshold = 3
            polarizing_set = [v  for k, v in json_data.items() if k in Constants.polarizing]
            neutral_set = [v  for k, v in json_data.items() if k in Constants.neutral]
            self.player.polarizing_score = sum(polarizing_set)/len(polarizing_set)
            self.player.neutral_score = sum(neutral_set)/len(neutral_set)
            self.player.polarizing_set = json.dumps([v >= threshold for v in polarizing_set])
            self.player.neutral_set = json.dumps([v >= threshold for v in neutral_set])

            self.player.survey_data = json.dumps(json_data)
            self.participant.vars['survey_data'] = json_data
            self.participant.vars['polarizing_score'] = self.player.polarizing_score
            self.participant.vars['neutral_score'] = self.player.neutral_score
            self.participant.vars['polarizing_set'] = [v >= threshold for v in polarizing_set]
            self.participant.vars['neutral_set'] = [v >= threshold for v in neutral_set]

        except JSONDecodeError as e:
            print('*' * 100)
            print(str(e))
            print('No data')
        print('*' * 100)
        return super().post()


page_sequence = [
    FirstWP,
    Intro,
    Instructions1,
    Instructions2,
    CQPage,
    PolPage,
]
