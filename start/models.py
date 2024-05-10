import random

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

author = 'Philip Chapkovski, Uni Duisburg-Essen'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'start'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent_accept = models.BooleanField(
        label="""
         I agree to participate in the current  study. I understand that I can withdraw my consent to participate at any time and by giving
                    consent I am not giving up any of my legal rights.""",
        widget=widgets.CheckboxInput
    )

    # user agent block
    full_user_data = models.LongStringField()
    useragent_is_mobile = models.BooleanField()
    useragent_is_bot = models.BooleanField()
    useragent_browser_family = models.StringField()
    useragent_os_family = models.StringField()
    useragent_device_family = models.StringField()
    ip_address = models.StringField()
