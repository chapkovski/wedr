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
from pprint import pprint

import pandas as pd

author = 'Philip Chapkovski, Uni Duisburg-Essen'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'start'
    players_per_group = None
    num_rounds = 1
    # let's use pandas to read csv in data/polqustions.csv and create two lists: polarizing and neutral based on treatment key
    df = pd.read_csv('data/polquestions.csv')
    # let's convert the dataframe to a dictionary
    polq_data = df.to_dict( 'records')
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


class Subsession(BaseSubsession):
    def group_by_arrival_time_method(self, waiting_players):
        if len(waiting_players) >0:
            return waiting_players[:1]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent_accept= models.BooleanField(
        label="""
         I agree to participate in the current  study. I understand that I can withdraw my consent to participate at any time and by giving
                    consent I am not giving up any of my legal rights.""",
        widget=widgets.CheckboxInput
    )
    full_neutral_set = models.StringField()
    full_polarizing_set = models.StringField()
    neutral_set = models.StringField()
    polarizing_set = models.StringField()
    survey_data = models.LongStringField()
    # user agent block
    full_user_data = models.LongStringField()
    useragent_is_mobile = models.BooleanField()
    useragent_is_bot = models.BooleanField()
    useragent_browser_family = models.StringField()
    useragent_os_family = models.StringField()
    useragent_device_family = models.StringField()



