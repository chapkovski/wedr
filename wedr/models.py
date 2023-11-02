from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
from django.db import models as djmodels
from random import choices, sample
import emojis
import json
import logging

logger = logging.getLogger(__name__)


# TODO:
# 1. progrfess bar
# 2. insert page with instructions
# 3. popup button at the working page
# 4. popup confirming success when the word is submitted correctly


def encode_word_with_alphabet(word):
    # List of example emojis categorized under 'People & Body' for demonstration
    all_emojis = emojis.db.utils.db.EMOJI_DB
    allowed_categories = ['People & Body', 'Animals & Nature', 'Food & Drink', 'Travel & Places', 'Activities', ]
    allowed_emojis = [i.emoji for i in all_emojis if i.category in allowed_categories]

    emojis.db.get_emojis_by_category('People & Body')
    # Create a mapping between alphabets and a random set of emojis
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    selected_emojis = sample(allowed_emojis, k=len(alphabet))  # Randomly choose 22 emojis from the list
    alphabet_to_emoji = dict(zip(alphabet, selected_emojis))

    # Encode the word
    encoded_word = [alphabet_to_emoji.get(letter, letter) for letter in word]
    return {'encoded_word': encoded_word, 'alphabet_to_emoji': alphabet_to_emoji}


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'wedr'
    players_per_group = 2
    num_rounds = 10
    words = ['elefant', 'banana', 'cherry', 'grapes', 'pencil', 'eraser', 'mirror', 'window', 'bottle', 'laptop']


class Subsession(BaseSubsession):
    def creating_session(self):
        for g in self.get_groups():
            g.decoded_word = choices(Constants.words)[0]
            res=encode_word_with_alphabet(g.decoded_word)
            g.alphabet_to_emoji = json.dumps(res['alphabet_to_emoji'])
            g.encoded_word = json.dumps(res['encoded_word'])



class Group(BaseGroup):
    decoded_word = models.StringField()
    encoded_word = models.StringField()
    alphabet_to_emoji = models.StringField()



class Player(BasePlayer):
    time_elapsed = models.FloatField()
    start_time = djmodels.DateTimeField(null=True)
    end_time = djmodels.DateTimeField(null=True)

    def handle_message(self, data):
        print('Got message', data)
        Message.objects.create(
            utc_time=data['utcTime'],
            owner=self,
            owner_group=self.group,
            message=data['message'],
        )
        return {0: {'type': 'message', 'who': self.participant.code, 'message': data['message']}}

    def handle_input(self, data):
        print('Got input')
        Input.objects.create(
            utc_time=data['utcTime'],
            owner=self,
            input=data['input'],
            input_index=data['inputIndex'],
            since_last_input=data['sinceLastInput']
        )


    def process_data(player, data):
        print(f"Got data: {data}")
        type=data.get('type')
        data=data.get('data')
        if type == 'message':
            resp = player.handle_message(data)
            return {0: resp}

        elif  type == 'input':
            player.handle_input(data)



class Input(djmodels.Model):
    utc_time = djmodels.DateTimeField()
    owner = djmodels.ForeignKey(to=Player, on_delete=djmodels.CASCADE, related_name='inputs')
    input = models.StringField()
    input_index = models.IntegerField()
    since_last_input = models.FloatField()


class Message(djmodels.Model):
    meta = {'ordering': ['utc_time']}   # this is needed to get the messages in the right order
    utc_time = djmodels.DateTimeField()
    owner = djmodels.ForeignKey(to=Player, on_delete=djmodels.CASCADE, related_name='messages')
    owner_group = djmodels.ForeignKey(to=Group, on_delete=djmodels.CASCADE, related_name='messages')
    message = models.StringField()


def custom_export(players):
    # we'll need to get for each player all its inputs
    inputs = Input.objects.all()
    yield ['session_code', 'participant_code', 'input_index', 'input', 'utc_time', 'since_last_input']
    for p in players:
        for i in p.inputs.all():
            yield [p.session.code, p.participant.code, i.input_index, i.input, i.utc_time, i.since_last_input]
