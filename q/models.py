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


author = 'Philipp Chapkovski'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'q'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    purpose = models.LongStringField(label='What do you think was the purpose of the study?')
    instructions_clarity = models.IntegerField(label="""
       How clear and understandable were the instructions to you? (Please write your answer between 1 = not understandable at all and 5 = completely understandable)
       """, choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    feedback=models.LongStringField(
        label="Please provide any feedback you have about the study. What did you like? What did you dislike? What could be improved?"
    )
