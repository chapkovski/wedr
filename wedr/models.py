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
from random import choices, sample
import random
import emojis
import json
import logging
from collections import OrderedDict
# let's import cycle
from pprint import pprint

logger = logging.getLogger(__name__)


# TODO
# separete example with dictionary and with input
# 1. ABOUT SUBMITTION (THEY WILL PROCEED AUTOMATICALLY AS SOON AS THEY ENTER)

# TODO:

# 4. popup confirming success when the word is submitted correctly

def has_disagreement(list1, list2):
    return any(x != y for x, y in zip(list1, list2))


def has_agreement(list1, list2):
    return any(x == y for x, y in zip(list1, list2))


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

    num_rounds = 3
    seconds_on_page= 15
    assert len(words) >= num_rounds, 'Not enough words in the file for this number of rounds'
    POLARIZING_TREATMENT = 'polarizing'
    NEUTRAL_TREATMENT = 'neutral'
    treatments = [POLARIZING_TREATMENT, NEUTRAL_TREATMENT]

    with open('data/polquestions.csv', 'r') as f:
        statements = list(csv.DictReader(f))


class Subsession(BaseSubsession):

    def creating_session(self):
        pass


class Group(BaseGroup):

    def set_time_over(self):
        default_time = datetime.now(timezone.utc) + timedelta(seconds=self.session.config.get("time_for_work", 1000))
        for p in self.get_players():
            p.participant.vars['time_to_go'] = default_time.timestamp()

    def set_treatment(self):
        self.set_time_over()
        _id = self.id_in_subsession - 2
        self.ideal_treatment = Constants.treatments[_id % 2]
        is_ideal_treatment_polar = self.ideal_treatment == Constants.POLARIZING_TREATMENT
        self.ideally_agree = (_id // 2) % 2
        # here we need to check feasilibity:

        p1 = self.get_player_by_id(1).participant
        p2 = self.get_player_by_id(2).participant
        if self.ideally_agree:
            print('we try to find if there is at least one agreement')
            agreement_status_pol = has_agreement(p1.vars['polarizing_set'], p2.vars['polarizing_set'])
            agreement_status_neutral = has_agreement(p1.vars['neutral_set'], p2.vars['neutral_set'])

        else:
            print('we try to find if there is at least one disagreement')
            agreement_status_pol = not has_disagreement(p1.vars['polarizing_set'], p2.vars['polarizing_set'])
            agreement_status_neutral = not has_disagreement(p1.vars['neutral_set'], p2.vars['neutral_set'])

        current_status = {Constants.POLARIZING_TREATMENT: agreement_status_pol, Constants.NEUTRAL_TREATMENT: agreement_status_neutral}
        print(f'Current status: {current_status=}')
        if current_status[self.ideal_treatment] == self.ideally_agree:
            self.treatment = self.ideal_treatment
            self.agreement = self.ideally_agree
        else:
            #     let's get all previous groups, calculate the number of times  of combinations of treatments and agreements and wll choose the least frequent one
            previous_groups = self.subsession.get_groups()
            n_polarized_groups = len([g for g in previous_groups if
                                      g.treatment == Constants.POLARIZING_TREATMENT and g.agreement == agreement_status_pol])
            n_neutral_groups = len([g for g in previous_groups if
                                    g.treatment == Constants.NEUTRAL_TREATMENT and g.agreement == agreement_status_neutral])
            if n_polarized_groups < n_neutral_groups:
                self.treatment = Constants.POLARIZING_TREATMENT
                self.agreement = agreement_status_pol
            else:
                self.treatment = Constants.NEUTRAL_TREATMENT
                self.agreement = agreement_status_neutral

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

    treatment = models.StringField()
    agreement = models.BooleanField()

    ideal_treatment = models.StringField()
    ideally_agree = models.BooleanField()
    decoded_word = models.StringField()
    encoded_word = models.StringField()
    alphabet_to_emoji = models.StringField()
    start_time = djmodels.DateTimeField(null=True)
    end_time = djmodels.DateTimeField(null=True)
    time_elapsed = models.FloatField()
    completed = models.BooleanField(default=False)


class Player(BasePlayer):
    def start(self):
        # TODO FOR TESTING ONLY, NB::   REMOVE THIS LATER
        v = self.participant.vars
        v['polarizing_set'] = choices([0, 1], k=3, )
        v['neutral_set'] = choices([0, 1], k=3, )
        v['polarizing_score'] = sum(v['polarizing_set']) / 3
        v['neutral_score'] = sum(v['neutral_set']) / 3
        self.polarizing_set = json.dumps(v['polarizing_set'])
        self.neutral_set = json.dumps(v['neutral_set'])
        self.polarizing_score = self.participant.vars['polarizing_score']
        self.neutral_score = self.participant.vars['neutral_score']



    @property
    def remaining_time(self):
        time_to_go = self.participant.vars.get('time_to_go')
        return time_to_go - datetime.now(timezone.utc).timestamp()

    partial_dict = models.StringField()
    time_elapsed = models.FloatField()
    start_time = djmodels.DateTimeField(null=True)
    completion_time = djmodels.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    neutral_score = models.FloatField()
    polarizing_score = models.FloatField()
    neutral_set = models.StringField()
    polarizing_set = models.StringField()



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
