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

import pandas as pd

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'start'
    players_per_group = None
    num_rounds = 1
    # let's use pandas to read csv in data/polqustions.csv and create two lists: polarizing and neutral based on treatment key
    df = pd.read_csv('data/polquestions.csv')
    polarizing = df[df['treatment'] == 'polarizing']['name'].tolist()
    neutral = df[df['treatment'] == 'neutral']['name'].tolist()



class Subsession(BaseSubsession):
    def group_by_arrival_time_method(self, waiting_players):
        if len(waiting_players) >0:
            return waiting_players[:1]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    neutral_score = models.FloatField()
    polarizing_score = models.FloatField()
    neutral_set = models.StringField()
    polarizing_set = models.StringField()
    survey_data = models.LongStringField()




