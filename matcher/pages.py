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
        current_time = self.participant.vars.setdefault('start_waiting_time1', utc_time_string)
        return {'currentTime': current_time, 'minToWait': self.min_to_wait}


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
    IntroToPol,
    PolPage,
]
