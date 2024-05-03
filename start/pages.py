from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import json
from json import JSONDecodeError
from pprint import pprint
from wedr.models import Constants as wedr_constants


class FirstWP(WaitPage):
    group_by_arrival_time = True
    body_text = "If your partner does not show up after 5 minutes, please submit NO_PARTNER code in Prolific and we will compensate you for your time."

    def is_displayed(self):
        return self.round_number == 1


class Intro(Page):
    def vars_for_template(self):
        return dict(num_puzzles=wedr_constants.num_rounds)


class Instructions1(Page):
    def vars_for_template(self):
        return dict(show_images=True, num_puzzles=wedr_constants.num_rounds)


class Instructions2(Page):
    def vars_for_template(self):
        return dict(show_images=True, num_puzzles=wedr_constants.num_rounds)


class CQPage(Page):
    pass


class IntroToPol(Page):
    pass


class PolPage(Page):
    def is_displayed(self):
        return self.round_number == 1

    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:

            json_data = json.loads(raw_data)

            data = Constants.polq_data.copy()
            response_mapping = Constants.response_mapping.copy()
            user_responses = json_data
            for item in data:
                response_value = user_responses.get(item['name'])
                response_text = response_mapping.get(response_value)
                item['user_response'] = response_value
                item['response_text'] = response_text


            threshold = 3
            polarizing_set = [v for k, v in json_data.items() if k in Constants.polarizing]
            neutral_set = [v for k, v in json_data.items() if k in Constants.neutral]
            self.player.full_polarizing_set = json.dumps(polarizing_set)
            self.player.full_neutral_set = json.dumps(neutral_set)
            self.player.polarizing_set = json.dumps([v >= threshold for v in polarizing_set])
            self.player.neutral_set = json.dumps([v >= threshold for v in neutral_set])

            self.player.survey_data = json.dumps(data)
            pprint(data)
            self.participant.vars['survey_data'] = data
            self.participant.vars['full_polarizing_set'] = polarizing_set
            self.participant.vars['full_neutral_set'] = neutral_set
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
    # Intro,
    # Instructions1,
    # Instructions2,
    # CQPage,
    # IntroToPol,
    PolPage,
]
