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
from datetime import timedelta, datetime, timezone
from otree.models import Participant
from django.db import models as djmodels
from django.db.models import Count
from random import choices, sample
import random
from start.models import Constants as start_constants
import json
import logging
from collections import OrderedDict
# let's import cycle
from pprint import pprint
from os import environ

logger = logging.getLogger(__name__)


# TODO
# separete example with dictionary and with input
# 1. ABOUT SUBMITTION (THEY WILL PROCEED AUTOMATICALLY AS SOON AS THEY ENTER)

# TODO:

# 4. popup confirming success when the word is submitted correctly

def split_alphabet_for_decoding(decoded_word, alphabet_to_emoji, n=10):
    # Remove duplicates and convert the decoded word to a set for efficient lookups
    unique_letters = set(decoded_word)

    # Ensure the word has an even number of letters
    if len(unique_letters) % 2 != 0:
        raise ValueError("Decoded word must have an even number of unique letters.")

    # Select half of the unique letters randomly
    half_size = len(unique_letters) // 2
    first_half_letters = set(sample(unique_letters, k=half_size))

    # The other half is the set difference between the unique letters and the first half
    second_half_letters = unique_letters - first_half_letters

    # Create dictionaries for the two participants
    # Each participant's dictionary includes all letters not in the decoded word
    # plus their assigned half of letters from the decoded word
    alphabet = set(alphabet_to_emoji.keys())

    letters_not_in_word = alphabet - unique_letters
    # we need to decrease alphabet, choosing randomly N letters from full one
    letters_not_in_word = set(sample(letters_not_in_word, k=n))
    first_participant_dict = OrderedDict(sorted({letter: alphabet_to_emoji[letter] for letter in
                                                 letters_not_in_word.union(first_half_letters)}.items()))

    second_participant_dict = OrderedDict(sorted({letter: alphabet_to_emoji[letter] for letter in
                                                  letters_not_in_word.union(second_half_letters)}.items()))
    print(f'Length of first participant dict: {len(first_participant_dict)}')
    print(f'Length of second participant dict: {len(second_participant_dict)}')
    return json.dumps(first_participant_dict), json.dumps(second_participant_dict)


def encode_word_with_alphabet(word):
    # List of example emojis categorized under 'People & Body' for demonstration
    # all_emojis = emojis.db.utils.db.EMOJI_DB
    # let's read emojis from 'data/emojis.txt
    with open('data/emojis.txt', 'r') as f:
        allowed_emojis = f.readlines()
        allowed_emojis = list(set([i.strip() for i in allowed_emojis]))

    # Create a mapping between alphabets and a random set of emojis
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    random.seed(environ.get('SEED', 1))
    selected_emojis = random.sample(allowed_emojis, len(alphabet))
    alphabet_to_emoji = dict(zip(alphabet, selected_emojis))

    # Encode the word
    encoded_word = [alphabet_to_emoji.get(letter) for letter in word]
    return {'encoded_word': encoded_word, 'alphabet_to_emoji': alphabet_to_emoji}


author = 'Philipp Chapkovski, UBonn, chapkovski@gmail.com'

doc = """
Your app description
"""
# let's read data/polquestions.csv
import csv


class Constants(BaseConstants):
    name_in_url = 'wedr'
    players_per_group = 2
    # we need to read words from data/words.txt
    with open('data/words.csv', 'r') as f:
        words = [i.strip() for i in f.readlines()]

    num_rounds = int(environ.get('NUM_WORDS', 5))
    seconds_on_page = 20  # how much time they should stay at the page with info about the partner
    assert len(words) >= num_rounds, 'Not enough words in the file for this number of rounds'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment = models.StringField()

    def set_treatment(self):
        treatments = list(set([p.participant.vars.get('treatment', '') for p in self.get_players()]))
        # check if both players have the same treatment and each treatmnt in start_constants.treatment
        if len(treatments) == 1 and treatments[0] in start_constants.treatments:
            self.treatment = treatments[0]

    def get_messages(self):
        return (Message.objects.
                filter(owner_group=self.id_in_subsession,
                       owner__session=self.session).
                order_by('utc_time'))

    def set_up_game(self):
        g = self
        # we need to encode the word and split the alphabet between the two players
        g.decoded_word = Constants.words[self.round_number - 1]  # choices(Constants.words)[0]
        res = encode_word_with_alphabet(g.decoded_word)
        g.alphabet_to_emoji = json.dumps(res['alphabet_to_emoji'])
        g.encoded_word = json.dumps(res['encoded_word'])
        p1 = g.get_player_by_id(1)
        p2 = g.get_player_by_id(2)
        p1.partial_dict, p2.partial_dict = split_alphabet_for_decoding(g.decoded_word, res['alphabet_to_emoji'])

    decoded_word = models.StringField()
    encoded_word = models.StringField()
    alphabet_to_emoji = models.StringField()
    start_time = djmodels.DateTimeField(null=True)
    end_time = djmodels.DateTimeField(null=True)
    time_elapsed = models.FloatField()
    completed = models.BooleanField(default=False)


class Player(BasePlayer):
    def get_partner(self):
        return self.get_others_in_group()[0]

    def start(self):

        # TODO FOR TESTING ONLY, NB::   REMOVE THIS LATER
        v = self.participant.vars
        if 'start' not in self.session.config.get('app_sequence'):
            index = (self.id_in_subsession - 1) // 2
            treatment = start_constants.treatments[index % 2]
            self.participant.vars['treatment'] = treatment
            qs = [q['name'] for q in start_constants.polq_data if q['treatment'] == treatment]
            print(f'qs: {qs}')
            _qs = qs.copy()
            random.shuffle(_qs)
            self.participant.vars['qs'] = _qs
        self.qs_order = json.dumps(v.get('qs', []))

    qs_order = models.StringField()
    partial_dict = models.StringField()
    time_elapsed = models.FloatField()
    start_time = djmodels.DateTimeField(null=True)
    completion_time = djmodels.DateTimeField(null=True)
    completed = models.BooleanField(default=False)

    def handle_message(self, data):
        logger.info('Got message', data)
        Message.objects.create(
            utc_time=data['utcTime'],
            owner=self.participant,
            owner_group=self.group.id_in_subsession,
            message=data['message'],
        )
        return {'type': 'message', 'who': self.participant.code, 'message': data['message']}



    def handle_answer(self, data):
        logger.info('Got answer')
        self.completion_time = data['completedAt']
        self.start_time = data['startTime']
        self.time_elapsed = data['timeElapsed']
        self.completed = True
        other = self.get_others_in_group()[0]
        if other.completed:
            self.group.completed = True
            self.group.start_time = self.start_time
            self.group.end_time = self.completion_time
            self.group.time_elapsed = self.time_elapsed

        return {'type': 'completed',
                'who': self.participant.code,
                'group_completed': self.group.completed,
                }  # this is needed to trigger the completion of the page

    def process_data(player, data):
        logger.info(f"Got data: {data}")
        type = data.get('type')
        data = data.get('data')
        if type == 'message':
            resp = player.handle_message(data)
            return {0: resp}


        elif type == 'answer':
            data = player.handle_answer(data)
            return {i.id_in_group: {**data, 'player_completed': i.completed} for i in player.group.get_players()}
    @property
    def remaining_time(self):
        time_to_go = self.participant.vars.get('time_to_go')
        return time_to_go - datetime.now(timezone.utc).timestamp()





class Message(djmodels.Model):
    meta = {'ordering': ['utc_time']}  # this is needed to get the messages in the right order
    utc_time = djmodels.DateTimeField()
    owner = djmodels.ForeignKey(to=Participant, on_delete=djmodels.CASCADE, related_name='messages')
    owner_group = models.IntegerField()
    message = models.StringField()


