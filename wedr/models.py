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

from random import choices, sample
import emojis

import logging

logger = logging.getLogger(__name__)


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
    players_per_group = None
    num_rounds = 10
    words = ['orange', 'banana', 'cherry', 'grapes', 'pencil', 'eraser', 'mirror', 'window', 'bottle', 'laptop']


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
