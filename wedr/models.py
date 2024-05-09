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

def has_disagreement(dict1, dict2):
    """
    Check if there is any disagreement between two dictionaries.
    Disagreement exists if for any key, the values in both dictionaries are different.

    :param dict1: First dictionary of responses.
    :param dict2: Second dictionary of responses.
    :return: True if there is any disagreement, False otherwise.
    """
    return any(dict1.get(k) != dict2.get(k) for k in dict1 if k in dict2)


def has_agreement(dict1, dict2):
    """
    Check if there is any agreement between two dictionaries.
    Agreement exists if for any key, the values in both dictionaries are the same.

    :param dict1: First dictionary of responses.
    :param dict2: Second dictionary of responses.
    :return: True if there is any agreement, False otherwise.
    """
    return any(dict1.get(k) == dict2.get(k) for k in dict1 if k in dict2)


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

    num_rounds = int(environ.get('NUM_WORDS', 5))
    seconds_on_page = 20  # how much time they should stay at the page with info about the partner
    assert len(words) >= num_rounds, 'Not enough words in the file for this number of rounds'
    POLARIZING_TREATMENT = 'polarizing'
    NEUTRAL_TREATMENT = 'neutral'
    treatments = [POLARIZING_TREATMENT, NEUTRAL_TREATMENT]
    treatment_keys = ['polar_disagree_info', 'polar_disagree_noinfo']
    treatment_options = {
        'polar_disagree_info': {'treatment': POLARIZING_TREATMENT, 'agree': False, 'info': True},
        'polar_disagree_noinfo': {'treatment': POLARIZING_TREATMENT, 'agree': False, 'info': False},
        # 'polar_disagree_details': {'treatment': POLARIZING_TREATMENT, 'agree': False, 'info': True},
        # 'polar_agree_info': {'treatment': POLARIZING_TREATMENT, 'agree': True, 'info': True},
        # 'neutral_disagree_info': {'treatment': NEUTRAL_TREATMENT, 'agree': False, 'info': True},
        # 'neutral_agree_info': {'treatment': NEUTRAL_TREATMENT, 'agree': True, 'info': True}
    }
    with open('data/polquestions.csv', 'r') as f:
        statements = list(csv.DictReader(f))


class Subsession(BaseSubsession):

    def creating_session(self):
        default_treatment = self.session.config.get('default_treatment')
        if default_treatment != '':
            assert self.session.config.get(
                'default_treatment') in Constants.treatment_options.keys(), 'Invalid default treatment'


class Group(BaseGroup):
    treatment_key = models.StringField()
    treatment = models.StringField()
    agreement = models.BooleanField()
    show_disagreement = models.BooleanField()
    show_details = models.BooleanField()

    def check_agreement_availability(self, p1, p2):
        """
        Check the availability of agreement and disagreement for polarizing and neutral sets.

        Args:
        p1, p2: Participant objects, each containing 'polarizing_set' and 'neutral_set'.

        Returns:
        Dictionary with the availability of agreement and disagreement for polarizing and neutral question sets.
        """
        # Polarizing set agreement and disagreement
        polar_agree = has_agreement(p1.vars['polarizing_set'], p2.vars['polarizing_set'])
        polar_disagree = has_disagreement(p1.vars['polarizing_set'], p2.vars['polarizing_set'])

        # Neutral set agreement and disagreement
        neutral_agree = has_agreement(p1.vars['neutral_set'], p2.vars['neutral_set'])
        neutral_disagree = has_disagreement(p1.vars['neutral_set'], p2.vars['neutral_set'])

        # Compile the availability into a dictionary
        availability_dict = {
            'polarizing': {'agree': polar_agree, 'disagree': polar_disagree},
            'neutral': {'agree': neutral_agree, 'disagree': neutral_disagree}
        }

        return availability_dict

    def filter_feasible_treatments(self):
        # Get participant objects
        p1 = self.get_player_by_id(1).participant
        p2 = self.get_player_by_id(2).participant

        # Check agreement availability
        availability = self.check_agreement_availability(p1, p2)
        print(f'{availability=}')

        # Define possible treatments and their feasibility requirements
        treatment_requirements = Constants.treatment_options

        treatment_counts_dict = {key: 0 for key in treatment_requirements.keys()}
        treatment_counts_query = (self.subsession.group_set
                                  .values('treatment_key')
                                  .annotate(count=Count('id')))
        treatment_counts_dict.update({item['treatment_key']: item['count'] for item in treatment_counts_query})

        # Prepare a dictionary to store feasible treatments
        feasible_treatment_counts = {}

        # Evaluate each treatment option for feasibility
        for treatment_key, requirements in treatment_requirements.items():
            treatment_type = requirements['treatment']
            required_agreement = requirements['agree']

            # Adjust feasibility check based on whether agreement or disagreement is required
            is_feasible = (
                availability[treatment_type]['agree'] if required_agreement else availability[treatment_type][
                    'disagree'])

            if is_feasible:
                feasible_treatment_counts[treatment_key] = treatment_counts_dict[treatment_key]

        return feasible_treatment_counts

    def choose_treatment(self):
        return Constants.treatment_keys[self.id_in_subsession % 2]
        feasible_treatment_counts = self.filter_feasible_treatments()
        # if it is not available let's replace it by {'polar_disagree_info': 0, 'polar_disagree_noinfo': 0}
        if not feasible_treatment_counts:
            feasible_treatment_counts = {'polar_disagree_info': 0, 'polar_disagree_noinfo': 0}

        # Find the minimum count among the feasible treatments
        min_count = min(feasible_treatment_counts.values())

        # Collect all treatment keys that have the minimum count
        least_popular_treatments = [key for key, count in feasible_treatment_counts.items() if count == min_count]

        # Randomly choose one from the least popular treatments
        if least_popular_treatments:
            chosen_treatment_key = random.choice(least_popular_treatments)
            print(f"Chosen treatment: {chosen_treatment_key}")
            return chosen_treatment_key
        else:
            print("No feasible treatment found")
            return None

    def set_treatment(self):
        if self.session.config.get('default_treatment') == '':
            treatment_key = self.choose_treatment()
            if treatment_key:
                self.treatment_key = treatment_key
            else:
                raise Exception("No feasible treatment found")
        else:
            treatment_key = self.session.config.get('default_treatment')
            self.treatment_key = treatment_key
        self.treatment = Constants.treatment_options[treatment_key]['treatment']
        self.agreement = Constants.treatment_options[treatment_key]['agree']
        self.show_disagreement = Constants.treatment_options[treatment_key]['info']
        self.show_details = self.treatment_key == 'polar_disagree_details'

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
        self.survey_data = json.dumps(v.get('survey_data', []))
        if 'start' not in self.session.config.get('app_sequence'):
            data = start_constants.polq_data.copy()
            response_mapping = start_constants.response_mapping.copy()
            full_polarizing_set = {}
            full_neutral_set = {}
            threshold = 3
            for item in data:
                response_value = random.randint(0, 5)
                item['response_text'] = response_mapping[response_value]
                item['user_response'] = response_value
                if item['treatment'] == 'polarizing':
                    full_polarizing_set[item['name']] = response_value
                else:
                    full_neutral_set[item['name']] = response_value

            self.survey_data = json.dumps(data)
            v['survey_data'] = data
            v['full_polarizing_set'] = full_polarizing_set
            v['full_neutral_set'] = full_neutral_set
            v['polarizing_set'] = {k: v >= threshold for k, v in full_polarizing_set.items()}
            v['neutral_set'] = {k: v >= threshold for k, v in full_neutral_set.items()}
        self.full_polarizing_set = json.dumps(v['full_polarizing_set'])
        self.full_neutral_set = json.dumps(v['full_neutral_set'])
        self.polarizing_set = json.dumps(v['polarizing_set'])
        self.neutral_set = json.dumps(v['neutral_set'])

    survey_data = models.LongStringField()
    partial_dict = models.StringField()
    time_elapsed = models.FloatField()
    start_time = djmodels.DateTimeField(null=True)
    completion_time = djmodels.DateTimeField(null=True)
    completed = models.BooleanField(default=False)

    neutral_set = models.StringField()
    polarizing_set = models.StringField()
    full_neutral_set = models.StringField()
    full_polarizing_set = models.StringField()

    def handle_message(self, data):
        logger.info('Got message', data)
        Message.objects.create(
            utc_time=data['utcTime'],
            owner=self,
            owner_group=self.group,
            message=data['message'],
        )
        return {'type': 'message', 'who': self.participant.code, 'message': data['message']}

    def handle_input(self, data):
        logger.info('Got input')
        Input.objects.create(
            utc_time=data['utcTime'],
            owner=self,
            input=data['input'],
            input_index=data['inputIndex'],
            since_last_input=data['sinceLastInput']
        )

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

        elif type == 'input':
            player.handle_input(data)
        elif type == 'answer':
            data = player.handle_answer(data)
            return {i.id_in_group: {**data, 'player_completed': i.completed} for i in player.group.get_players()}


class Input(djmodels.Model):
    utc_time = djmodels.DateTimeField()
    owner = djmodels.ForeignKey(to=Player, on_delete=djmodels.CASCADE, related_name='inputs')
    input = models.StringField()
    input_index = models.IntegerField()
    since_last_input = models.FloatField()


class Message(djmodels.Model):
    meta = {'ordering': ['utc_time']}  # this is needed to get the messages in the right order
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
