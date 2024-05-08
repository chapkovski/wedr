from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, make_guess_survey
import json
from json import JSONDecodeError
from pprint import pprint
from wedr.models import Constants as wedr_constants
import logging

logger = logging.getLogger(__name__)
from django_user_agents.utils import get_user_agent


class FirstWP(WaitPage):
    group_by_arrival_time = True
    body_text = "If your partner does not show up after 5 minutes, please submit NO_PARTNER code in Prolific and we will compensate you for your time."

    def is_displayed(self):
        return self.round_number == 1


class Consent(Page):
    def get(self, *args, **kwargs):
        user_agent = get_user_agent(self.request)
        logger.info(f'User agent: {user_agent}')
        self.player.full_user_data = json.dumps(user_agent.__dict__)
        self.player.useragent_is_mobile = user_agent.is_mobile
        self.player.useragent_is_bot = user_agent.is_bot
        self.player.useragent_browser_family = user_agent.browser.family
        self.player.useragent_os_family = user_agent.os.family
        self.player.useragent_device_family = user_agent.device.family
        return super().get()

    def vars_for_template(self):
        return dict(num_words=wedr_constants.num_rounds)

    form_model = 'player'
    form_fields = ['consent_accept']


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

    def js_vars(self):
        return dict(json=self.participant.vars['full_q'])

    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:

            json_data = json.loads(raw_data)
            data = Constants.polq_data.copy()
            response_mapping = Constants.response_mapping.copy()
            user_responses = json_data
            for k, v in user_responses.items():
                try:
                    setattr(self.player, k, str(v))
                except AttributeError as e:
                    logger.error(
                        f'No such field at player level: {k} for value {v}. Player {self.player.participant.code}. Error: {e}')
            for item in data:
                response_value = user_responses.get(item['name'])
                response_text = response_mapping.get(response_value)
                item['user_response'] = response_value
                item['response_text'] = response_text

            threshold = 3
            polarizing_set = {k: v for k, v in json_data.items() if k in Constants.polarizing}
            neutral_set = {k: v for k, v in json_data.items() if k in Constants.neutral}
            self.player.full_polarizing_set = json.dumps(polarizing_set)
            self.player.full_neutral_set = json.dumps(neutral_set)
            self.participant.vars['survey_data'] = data
            self.participant.vars['full_polarizing_set'] = polarizing_set
            self.participant.vars['full_neutral_set'] = neutral_set
            self.participant.vars['polarizing_set'] = {k: v >= threshold for k, v in polarizing_set.items()}
            self.player.polarizing_set = json.dumps(self.player.participant.vars['polarizing_set'])
            self.participant.vars['neutral_set'] = {k: v >= threshold for k, v in neutral_set.items()}
            self.player.neutral_set = json.dumps(self.player.participant.vars['neutral_set'])
            self.player.survey_data = json.dumps(data)
        except JSONDecodeError as e:
            print('*' * 100)
            print(str(e))
            print('No data')
        print('*' * 100)
        return super().post()


class IntroGuess(Page):
    pass


class GuessPage(Page):
    def js_vars(self):
        return dict(json=make_guess_survey())

    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:
            user_responses = json.loads(raw_data)
            pprint(user_responses)
            for k, v in user_responses.items():
                try:
                    setattr(self.player, k, v)
                except AttributeError as e:
                    logger.error(
                        f'No such field at player level: {k} for value {v}. Player {self.player.participant.code}. Error: {e}')
        except JSONDecodeError as e:
            print('*' * 100)
            print(str(e))
            print('No data')
        print('*' * 100)
        return super().post()


page_sequence = [
    Consent,
    Intro,
    Instructions1,
    Instructions2,
    CQPage,
    IntroToPol,
    PolPage,
    IntroGuess,
    GuessPage,

]
