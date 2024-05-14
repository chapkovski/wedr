import random

from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, encode_word_with_alphabet
import logging
import json
from datetime import timedelta, datetime, timezone
from pprint import pprint
from json import JSONDecodeError

logger = logging.getLogger(__name__)


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
    def is_displayed(self):
        return self.round_number == 1


class PolPage(Page):
    def is_displayed(self):
        return self.round_number == 1

    def js_vars(self):
        return dict(json=self.player.full_q)

    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:
            available_keys = [i['name'] for i in Constants.polq_data]
            json_data = json.loads(raw_data)
            data = Constants.polq_data.copy()
            response_mapping = Constants.response_mapping.copy()
            user_responses = json_data
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
            self.participant.vars['own_polq'] = {k:v for k,v in user_responses.items() if k in available_keys}


        except JSONDecodeError as e:
            print('*' * 100)
            print(str(e))
            print('No data')
        print('*' * 100)
        return super().post()


class WorkingPage(Page):
    live_method = 'process_data'

    def is_displayed(self):
        if self.player.remaining_time <= 0:
            return False
        return not self.group.completed

    def vars_for_template(self):
        qs = [q for q in Constants.polq_data if q.get('treatment') == self.group.treatment]
        return dict(show_warning=True, num_puzzles=Constants.num_rounds, statements=qs)

    def js_vars(self):
        main_dict = dict(
            groupDict=json.loads(self.group.alphabet_to_emoji),
            encodedWord=json.loads(self.group.encoded_word),
            decodedWord=self.group.decoded_word,
            partialDict=json.loads(self.player.partial_dict),
            ownCode=self.participant.code,
            remaining_time=self.player.remaining_time,
            player_completed=self.player.completed,
            group_completed=self.group.completed,
            num_decoded_words=self.round_number - 1,
            total_words=Constants.num_rounds,
        )

        word = Constants.words[self.round_number - 1]
        res = encode_word_with_alphabet(word)
        messages = self.group.get_messages()
        formatted_messages = [
            {
                "type": "message",
                "who": i.owner.code,
                "message": i.message,
                "own": i.owner == self.participant,
            }
            for i in messages
        ]
        res.update({'messages': formatted_messages})
        res.update(main_dict)
        return res

    def post(self):
        logger.info(f'Got data: {self.request.POST}')
        return super().post()


class PartnerWP(WaitPage):
    after_all_players_arrive = 'set_up_game'

    def is_displayed(self):
        if self.round_number == 1:
            return True

        if self.player.remaining_time <= 0:
            return False
        return True


class IntroGuess(Page):
    form_model = 'player'
    form_fields = ['guess_check']
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):

        qs = [q for q in Constants.polq_data if q.get('treatment') == self.group.treatment]
        return dict(statements=qs)


page_sequence = [
    GameSettingWP,
    IntroToPol,
    PolPage,
    IntroGuess,
    PartnerWP,
    WorkingPage,

]
