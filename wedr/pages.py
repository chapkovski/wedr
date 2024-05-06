import random

from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, encode_word_with_alphabet
# import emojis
import logging
import json
from datetime import timedelta, datetime, timezone
from pprint import pprint

logger = logging.getLogger(__name__)


class GameSettingWP(WaitPage):
    template_name = 'wedr/FirstWP.html'
    group_by_arrival_time = True
    min_to_wait = 5
    body_text = f"If you wait for more than {min_to_wait} minutes, please submit NO_PARTNER code in Prolific and we will compensate you for your time! Thank you!"
    after_all_players_arrive = 'set_treatment'

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

            player_completed=self.player.completed,
            group_completed=self.group.completed,
            num_decoded_words=self.round_number - 1,
            total_words=Constants.num_rounds,
        )

        word = Constants.words[self.round_number - 1]
        res = encode_word_with_alphabet(word)
        messages = self.group.messages.all()
        formatted_messages = [
            {
                "type": "message",
                "who": i.owner.participant.code,
                "message": i.message,
                "own": i.owner == self.player,
            }
            for i in messages
        ]
        res.update({'messages': formatted_messages})
        res.update(main_dict)
        return res

    def post(self):
        logger.info(f'Got data: {self.request.POST}')
        return super().post()


class MatchPage(Page):
    def is_displayed(self):
        return self.round_number == 1

    def js_vars(self):
        return dict(seconds_on_page=Constants.seconds_on_page)

    def vars_for_template(self):
        treatment = self.group.treatment
        my_answers = json.loads(self.player.survey_data)
        pprint(my_answers)
        print('$' * 100)
        partner_answers = json.loads(self.player.get_partner().survey_data)
        # let's update the data to include color: if the user_response value is <3 color 'lightred' and 'lightgreen' otherwise
        for i in my_answers:
            i['color'] = 'lightred' if i['user_response'] < 3 else 'lightgreen'
        for i in partner_answers:
            i['color'] = 'lightred' if i['user_response'] < 3 else 'lightgreen'

        my_relevant_answers = [i for i in my_answers if i['treatment'] == treatment]
        partner_relevant_answers = [i for i in partner_answers if i['treatment'] == treatment]
        if not self.group.show_disagreement:
            my_relevant_answers = my_answers
            partner_relevant_answers = partner_answers
        full_data = list(zip(my_relevant_answers, partner_relevant_answers))

        random.shuffle(full_data)
        agreement_status = 'agree' if self.group.agreement else 'disagree'
        return dict(statements=full_data, agreement_status=agreement_status)


class PartnerWP(WaitPage):
    after_all_players_arrive = 'set_up_game'


page_sequence = [
    GameSettingWP,
    MatchPage,
    PartnerWP,
    WorkingPage,
]
