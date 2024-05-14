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

from random import choices, sample

import json
import logging
from collections import OrderedDict

import random
from copy import deepcopy
import yaml
import json
from jinja2 import Template
from pprint import pprint
import pandas as pd
from os import environ

logger = logging.getLogger(__name__)


def create_survey_page(row, choices):
    """
    Convert a row from CSV with 'name' and 'text' columns to a SurveyJS page with a single element.

    :param row: A dictionary with keys 'name' and 'text', e.g., {'name': 'question1', 'text': 'Question text here'}
    :return: A dictionary formatted as a SurveyJS page containing one question element.
    """
    choices = [{"value": key, "text": text} for key, text in choices.items()]

    return {
        "name": row["name"] + "_page",  # Unique page name using question name
        "elements": [
            {
                "type": "radiogroup",
                "name": row["name"],
                "title": row["text"],
                "isRequired": True,
                "choices": choices
            }
        ]
    }


def load_csv_to_survey_pages(polq_data, choices):
    """
    Load a CSV file and convert each row to a SurveyJS page with a single question element.

    :param csv_filename: The path to the CSV file
    :return: A list of dictionaries, each representing a separate page in SurveyJS
    """
    pages = []

    for row in polq_data:
        page = create_survey_page(row, choices)
        pages.append(page)
    return pages


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

    num_rounds = int(environ.get('NUM_ROUNDS', 20))
    seconds_on_page = 20  # how much time they should stay at the page with info about the partner
    assert len(words) >= num_rounds, 'Not enough words in the file for this number of rounds'
    print(f'Number of rounds: {num_rounds}; Number of words: {len(words)}')
    df = pd.read_csv('data/polquestions.csv')
    # let's convert the dataframe to a dictionary
    polq_data = df.to_dict('records')

    polarizing = df[df['treatment'] == 'polarizing']['name'].tolist()
    neutral = df[df['treatment'] == 'neutral']['name'].tolist()
    response_mapping = {
        0: "Strongly Disagree",
        1: "Moderately Disagree",
        2: "Slightly Disagree",
        3: "Slightly Agree",
        4: "Moderately Agree",
        5: "Strongly Agree"
    }
    file_path = 'data/presurvey.yaml'
    with open(file_path, 'r', encoding="utf-8") as yaml_file:
        yaml_template = yaml_file.read()
        rendered_yaml = Template(yaml_template).render({})
        survey_prototype = yaml.safe_load(rendered_yaml)
    POLARIZING_TREATMENT = 'polarizing'
    NEUTRAL_TREATMENT = 'neutral'
    treatments = [POLARIZING_TREATMENT, NEUTRAL_TREATMENT]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment = models.StringField()

    def set_treatment(self):
        self.treatment = Constants.treatments[self.id_in_subsession % 2]
        qs = [q['name'] for q in Constants.polq_data]
        print(f'qs: {qs}')
        for p in self.get_players():
            _qs = qs.copy()
            random.shuffle(_qs)
            p.qs_order = json.dumps(_qs)
            p.participant.vars['treatment'] = self.treatment
            p.participant.vars['qs'] = _qs

    def set_time_over(self):
        default_time = datetime.now(timezone.utc) + timedelta(seconds=self.session.config.get("time_for_work", 1000))
        for p in self.get_players():
            p.participant.vars['time_to_go'] = default_time.timestamp()

    def get_messages(self):
        return (Message.objects.
                filter(owner_group=self.id_in_subsession,
                       owner__session=self.session).
                order_by('utc_time'))

    def set_up_game(self):
        if self.round_number == 1:
            for p in self.get_players():
                p.participant.vars['partner_polq'] = p.get_partner().participant.vars.get('own_polq')
                p.own_polq = json.dumps(p.participant.vars.get('own_polq', {}))
                p.partner_polq = json.dumps(p.participant.vars.get('partner_polq', {}))
            self.set_time_over()
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

    @property
    def full_q(self):
        qs_order = json.loads(self.qs_order)
        qs = [next(q for q in Constants.polq_data if q['name'] == name) for name in qs_order]

        rendered_questionnaire = load_csv_to_survey_pages(qs, choices=Constants.response_mapping)
        # let's make a deepcopy of the survey_prototype
        res = deepcopy(Constants.survey_prototype)
        res['pages'].extend(rendered_questionnaire)
        return res

    def get_partner(self):
        return self.get_others_in_group()[0]

    def start(self):

        # TODO FOR TESTING ONLY, NB::   REMOVE THIS LATER
        v = self.participant.vars
        if 'start' not in self.session.config.get('app_sequence'):
            index = (self.id_in_subsession - 1) // 2
            treatment = Constants.treatments[index % 2]
            self.participant.vars['treatment'] = treatment
            qs = [q['name'] for q in Constants.polq_data if q['treatment'] == treatment]
            print(f'qs: {qs}')
            _qs = qs.copy()
            random.shuffle(_qs)
            self.participant.vars['qs'] = _qs
        self.qs_order = json.dumps(v.get('qs', []))

    """
    Choices:

Only A
Only B
Only C
A and B
A, B, and C"""
    guess_check = models.StringField(
        choices=['Only A', 'Only B', 'Only C', 'A and B', 'A, B, and C'],
        widget=widgets.RadioSelect
    )

    def guess_check_error_message(self, value):
        if value != 'A, B, and C':
            return 'Please check your answer'

    qs_order = models.StringField()
    own_polq = models.StringField()
    partner_polq = models.StringField()
    partial_dict = models.StringField()
    time_elapsed = models.FloatField()
    start_time = djmodels.DateTimeField(null=True)
    completion_time = djmodels.DateTimeField(null=True)
    completed = models.BooleanField(default=False)

    age = models.StringField()
    gender = models.StringField()
    education = models.StringField()
    employmentStatus = models.StringField()
    householdIncome = models.StringField()
    # polarizing
    women = models.StringField()
    immigration = models.StringField()
    climate_change = models.StringField()
    # neutral
    books = models.StringField()
    cars = models.StringField()
    healthy_eating = models.StringField()

    def handle_message(self, data):
        logger.info('Got message', data)
        Message.objects.create(
            utc_time=data['utcTime'],
            owner=self.participant,
            owner_group=self.group.id_in_subsession,
            round_number=self.round_number,
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
    round_number = models.IntegerField()
