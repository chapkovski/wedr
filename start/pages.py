from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import json
from json import JSONDecodeError
from pprint import pprint
from wedr.models import Constants as wedr_constants
import logging
from datetime import timedelta, datetime, timezone
from pprint import pprint

logger = logging.getLogger(__name__)
from django_user_agents.utils import get_user_agent


class GameSettingWP(WaitPage):
    template_name = 'wedr/FirstWP.html'
    group_by_arrival_time = True

    @property
    def body_text(self):
        body_text = f"If you wait for more than {self.min_to_wait} minutes, please submit NO_PARTNER code in Prolific and we will compensate you for your time! Thank you!"
        return body_text

    after_all_players_arrive = 'set_treatment'

    @property
    def min_to_wait(self):
        return self.session.config.get('min_to_wait', 5)

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return dict(no_partner_url=self.session.config.get('no_partner_url'))

    def js_vars(self):
        # Get the current UTC time
        current_utc_time = datetime.utcnow()

        # Convert to a format that JavaScript can parse
        utc_time_string = current_utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        current_time = self.participant.vars.setdefault('start_waiting_time', utc_time_string)
        return {'currentTime': current_time, 'minToWait': self.min_to_wait}


class Consent(Page):
    def get(self, *args, **kwargs):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        if ip:
            self.player.ip_address = ip
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
        return dict(json=self.player.full_q)

    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:

            json_data = json.loads(raw_data)
            data = Constants.polq_data.copy()
            response_mapping = Constants.response_mapping.copy()
            user_responses = json_data
            pprint(user_responses)
            res = {}
            for k, v in user_responses.items():
                try:
                    setattr(self.player, k, str(v))
                except AttributeError as e:
                    logger.error(
                        f'No such field at player level: {k} for value {v}. Player {self.player.participant.code}. Error: {e}')
            for item in data:
                name = item['name']
                if name in user_responses:
                    res[name] = dict(
                        response_value=user_responses[name],
                        response_text=response_mapping[user_responses[name]],
                        text=item['text'],
                    )

            self.participant.vars['polq_data'] = res
            self.participant.vars['own_polq'] = user_responses


        except JSONDecodeError as e:
            print('*' * 100)
            print(str(e))
            print('No data')
        print('*' * 100)
        return super().post()


page_sequence = [
    GameSettingWP,
    Consent,
    Intro,
    Instructions1,
    Instructions2,
    CQPage,
    IntroToPol,
    PolPage,
]
