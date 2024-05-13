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
from wedr.models import Constants as wedr_constants
import random
import json

author = 'Philipp Chapkovski'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'q'
    players_per_group = None
    num_rounds = 1
    polq_items = [i.get('name') for i in wedr_constants.polq_data]
    print(polq_items)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    def start(self):
        if 'wedr' not in self.session.config.get('app_sequence'):
            self.participant.vars['treatment'] = random.choice(wedr_constants.treatments)
            treatment = self.participant.vars['treatment']
            self.participant.vars['own_polq'] = {i.get('name'): random.randint(0, 5) for i in wedr_constants.polq_data
                                                 if i.get('treatment') == treatment}
            print(self.participant.vars['own_polq'])
            self.participant.vars['partner_polq'] = {i.get('name'): random.randint(0, 5) for i in
                                                     wedr_constants.polq_data if i.get('treatment') == treatment}
            print(self.participant.vars['partner_polq'])
        self.treatment = self.participant.vars.get('treatment')
        self.own_polq = json.dumps(self.participant.vars.get('own_polq'))
        self.partner_polq = json.dumps(self.participant.vars.get('partner_polq'))
        print(f'Current treatment: {self.treatment}')

    def set_payoffs(self):
        current_guess = json.loads(self.guess)
        partner_answers = json.loads(self.partner_polq)
        # let's match guess with actual answers
        match = all(current_guess.get(key) == partner_answers.get(key) for key in current_guess)
        remuneration = self.session.config.get('payment_for_guess', 1.00)
        self.payoff = c(remuneration) if match else 0

    treatment = models.StringField()
    own_polq = models.StringField()
    partner_polq = models.StringField()
    guess = models.StringField()
    # block of questions to keep partner's answers they all start with partner_

    partner_women = models.IntegerField()
    partner_immigration = models.IntegerField()
    partner_climate_change = models.IntegerField()

    partner_books = models.IntegerField()
    partner_cars = models.IntegerField()
    partner_healthy_eating = models.IntegerField()

    purpose = models.LongStringField(label='What do you think was the purpose of the study?')
    instructions_clarity = models.IntegerField(label="""
       How clear and understandable were the instructions to you? (Please write your answer between 1 = not understandable at all and 5 = completely understandable)
       """, choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    feedback = models.LongStringField(
        label="Please provide any feedback you have about the study. What did you like? What did you dislike? What could be improved?"
    )

    interest_in_us_politics = models.StringField()
    opinion_impact = models.StringField()
    partner_effort = models.StringField()
    political_discussion_at_work = models.StringField()
    political_orientation = models.StringField()
    self_effort = models.StringField()
    team_communication_effectiveness = models.StringField()
    team_satisfaction = models.StringField()
