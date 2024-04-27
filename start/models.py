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


class Subsession(BaseSubsession):
    def group_by_arrival_time_method(self, waiting_players):
        if len(waiting_players) >0:
            return waiting_players[:1]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    neutral_score = models.FloatField()
    polarizing_score = models.FloatField()
    survey_data = models.LongStringField()




def calculate_grouped_averages(form_data):
    # Load the CSV data
    data = pd.read_csv('data/polquestions.csv')

    # Convert the form data dictionary into a DataFrame
    responses = pd.DataFrame(list(form_data.items()), columns=['name', 'response'])

    # Merge the responses with the CSV data based on the 'name' column
    merged_data = pd.merge(data, responses, on='name')

    # Group the merged data by the 'treatment' column and calculate the mean response for each group
    grouped_averages = merged_data.groupby('treatment')['response'].mean()

    # Return the grouped averages as a dictionary
    return grouped_averages.to_dict()

