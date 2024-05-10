import random

from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, encode_word_with_alphabet
from matcher.models import Constants as matcher_constants
import logging
import json
from datetime import timedelta, datetime, timezone
from pprint import pprint

logger = logging.getLogger(__name__)


class GameSettingWP(WaitPage):
    template_name = 'wedr/FirstWP.html'
    after_all_players_arrive = 'set_treatment'
    @property
    def body_text(self):
        body_text = f"If you wait for more than {self.min_to_wait} minutes, please submit NO_PARTNER code in Prolific and we will compensate you for your time! Thank you!"
        return body_text

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


class WorkingPage(Page):
    live_method = 'process_data'

    def is_displayed(self):
        if self.player.remaining_time <= 0:
            return False
        return not self.group.completed

    def vars_for_template(self):
        return dict(show_warning=True, num_puzzles=Constants.num_rounds)

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


class IntroGuess(Page):
    def is_displayed(self):
        return self.round_number == 1
    def vars_for_template(self):
        qs_order = self.participant.vars.get('qs', [])
        qs = [next(q for q in matcher_constants.polq_data if q['name'] == name) for name in qs_order]
        return dict(statements=qs)

page_sequence = [
    GameSettingWP,
    # IntroGuess,
    PartnerWP,
    WorkingPage,
]
