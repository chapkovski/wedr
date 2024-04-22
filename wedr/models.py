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
import random
import emojis
import json
import logging
from collections import OrderedDict
# let's import cycle

logger = logging.getLogger(__name__)
# TODO
# ADD IN INSTRUCTIONS AND CQS INFORMATION
# 1. ABOUT SUBMITTION (THEY WILL PROCEED AUTOMATICALLY AS SOON AS THEY ENTER)
# 2. ONCE AGAIN SOME LETTERS ARE *MISSING* FROM THE USER'S SET OF LETTERS

# TODO:
# 1. progrfess bar
# 2. insert page with instructions
# 3. popup button at the working page
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

def is_single_scalar(emoji):
    # Normalize the emoji to its fully decomposed form
    decomposed = emoji.encode('unicode-escape').decode('ASCII')
    # If it contains '\u200d' (Zero Width Joiner), it's a composite emoji
    return '\\u200d' not in decomposed

def get_unicode_codepoints(emoji):
    # Return a tuple of Unicode code points for a given emoji
    return tuple(ord(char) for char in emoji)

def select_emojis(emojis, number_to_select, min_distance):
    selected_emojis = []
    # Sort emojis by their combined code points values
    sorted_emojis = sorted(emojis, key=get_unicode_codepoints)

    while len(selected_emojis) < number_to_select:
        # Randomly select an emoji from the sorted list
        emoji = random.choice(sorted_emojis)
        emoji_codepoints = get_unicode_codepoints(emoji)

        # Check if the emoji is at a minimum distance from all previously selected emojis
        if all(min(abs(a - b) for a in emoji_codepoints for b in get_unicode_codepoints(e)) >= min_distance for e in selected_emojis):
            selected_emojis.append(emoji)
            # Remove a range of emojis around the selected one to maintain the distance
            sorted_emojis = [e for e in sorted_emojis if min(abs(a - b) for a in get_unicode_codepoints(e) for b in emoji_codepoints) >= min_distance]

        # If we've removed too many and can't select enough, reduce the distance
        if len(sorted_emojis) < number_to_select - len(selected_emojis):
            logger.warning("Not enough emojis to maintain the minimum distance. Reducing distance.")
            return select_emojis(emojis, number_to_select, min_distance - 1)

    return selected_emojis
def encode_word_with_alphabet(word):
    # List of example emojis categorized under 'People & Body' for demonstration
    all_emojis = emojis.db.utils.db.EMOJI_DB
    allowed_categories = ['People & Body', 'Animals & Nature', 'Food & Drink', 'Travel & Places', 'Activities', ]
    allowed_emojis = [i.emoji for i in all_emojis if i.category in allowed_categories]

    allowed_emojis = [i for i in allowed_emojis if is_single_scalar(i)]

    # Create a mapping between alphabets and a random set of emojis
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    selected_emojis = select_emojis(allowed_emojis, len(alphabet), 10)
    alphabet_to_emoji = dict(zip(alphabet, selected_emojis))

    # Encode the word
    encoded_word = [alphabet_to_emoji.get(letter, letter) for letter in word]
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
    # words = ['mandarin']
    num_rounds = 1
    words = sample(words, k=num_rounds)
    treatments = ['neutral', 'polarizing']
    time_for_work = 60
    with open('data/polquestions.csv', 'r') as f:
        statements = list(csv.DictReader(f))



class Subsession(BaseSubsession):
    def creating_session(self):
        pass

class Group(BaseGroup):
    def set_up_game(self):
        g=self
        # we need to encode the word and split the alphabet between the two players
        g.decoded_word = choices(Constants.words)[0]
        res = encode_word_with_alphabet(g.decoded_word)
        g.alphabet_to_emoji = json.dumps(res['alphabet_to_emoji'])
        g.encoded_word = json.dumps(res['encoded_word'])
        p1 = g.get_player_by_id(1)
        p2 = g.get_player_by_id(2)
        p1.partial_dict, p2.partial_dict = split_alphabet_for_decoding(g.decoded_word, res['alphabet_to_emoji'])
        g.treatment = Constants.treatments[g.id_in_subsession % 2]
    treatment = models.StringField()
    decoded_word = models.StringField()
    encoded_word = models.StringField()
    alphabet_to_emoji = models.StringField()
    start_time = djmodels.DateTimeField(null=True)
    end_time = djmodels.DateTimeField(null=True)
    time_elapsed = models.FloatField()
    completed = models.BooleanField(default=False)


class Player(BasePlayer):
    partial_dict = models.StringField()
    time_elapsed = models.FloatField()
    start_time = djmodels.DateTimeField(null=True)
    completion_time = djmodels.DateTimeField(null=True)
    completed = models.BooleanField(default=False)

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

    def handle_completed(self, data):
        logger.info('Got completion')
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
                'group_completed': self.group.completed}  # this is needed to trigger the completion of the page

    def process_data(player, data):
        logger.info(f"Got data: {data}")
        type = data.get('type')
        data = data.get('data')
        if type == 'message':
            resp = player.handle_message(data)
            return {0: resp}

        elif type == 'input':
            player.handle_input(data)
        elif type == 'completed':
            return {0: player.handle_completed(data)}


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
