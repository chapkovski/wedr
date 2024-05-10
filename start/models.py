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
from copy import deepcopy
from pprint import pprint
import yaml
import json
from jinja2 import Template

import pandas as pd

author = 'Philip Chapkovski, Uni Duisburg-Essen'

doc = """
Your app description
"""


def create_survey_page(row, choices):
    """
    Convert a row from CSV with 'name' and 'text' columns to a SurveyJS page with a single element.

    :param row: A dictionary with keys 'name' and 'text', e.g., {'name': 'question1', 'text': 'Question text here'}
    :return: A dictionary formatted as a SurveyJS page containing one question element.
    """
    choices = [{"value": key, "text": text} for key, text in choices.items()]

    return {
        "name": row["name"] + "_page",  # Unique page name using question name
        "elements": [
            {
                "type": "radiogroup",
                "name": row["name"],
                "title": row["text"],
                "isRequired": True,
                "choices": choices
            }
        ]
    }


def load_csv_to_survey_pages(polq_data, choices):
    """
    Load a CSV file and convert each row to a SurveyJS page with a single question element.

    :param csv_filename: The path to the CSV file
    :return: A list of dictionaries, each representing a separate page in SurveyJS
    """
    pages = []

    for row in polq_data:
        page = create_survey_page(row, choices)
        pages.append(page)
    return pages


class Constants(BaseConstants):
    name_in_url = 'start'
    players_per_group = 2
    num_rounds = 1
    # let's use pandas to read csv in data/polqustions.csv and create two lists: polarizing and neutral based on treatment key
    df = pd.read_csv('data/polquestions.csv')
    # let's convert the dataframe to a dictionary
    polq_data = df.to_dict('records')

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
    file_path = 'data/presurvey.yaml'
    with open(file_path, 'r', encoding="utf-8") as yaml_file:
        yaml_template = yaml_file.read()
        rendered_yaml = Template(yaml_template).render({})
        survey_prototype = yaml.safe_load(rendered_yaml)
    POLARIZING_TREATMENT = 'polarizing'
    NEUTRAL_TREATMENT = 'neutral'
    treatments = [POLARIZING_TREATMENT, NEUTRAL_TREATMENT]


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    treatment = models.StringField()

    def set_treatment(self):
        self.treatment = Constants.treatments[self.id_in_subsession % 2]
        qs = [q['name'] for q in Constants.polq_data if q['treatment'] == self.treatment]
        print(f'qs: {qs}')
        for p in self.get_players():
            _qs = qs.copy()
            random.shuffle(_qs)
            p.qs_order = json.dumps(_qs)
            p.participant.vars['treatment'] = self.treatment
            p.participant.vars['qs'] = _qs


class Player(BasePlayer):
    def start(self):
        pass

    @property
    def full_q(self):
        qs_order = json.loads(self.qs_order)
        qs = [next(q for q in Constants.polq_data if q['name'] == name) for name in qs_order]

        rendered_questionnaire = load_csv_to_survey_pages(qs, choices=Constants.response_mapping)
        # let's make a deepcopy of the survey_prototype
        res = deepcopy(Constants.survey_prototype)
        res['pages'].extend(rendered_questionnaire)
        return res

    consent_accept = models.BooleanField(
        label="""
         I agree to participate in the current  study. I understand that I can withdraw my consent to participate at any time and by giving
                    consent I am not giving up any of my legal rights.""",
        widget=widgets.CheckboxInput
    )

    qs_order = models.StringField()
    # user agent block
    full_user_data = models.LongStringField()
    useragent_is_mobile = models.BooleanField()
    useragent_is_bot = models.BooleanField()
    useragent_browser_family = models.StringField()
    useragent_os_family = models.StringField()
    useragent_device_family = models.StringField()
    ip_address = models.StringField()
    # political demographic quetionsnnaire fields: ['age', 'gender', 'maritalStatus', 'employmentStatus', 'householdIncome', 'women', 'partisanship', 'immigration', 'books', 'cities', 'cars']
    age = models.StringField()
    gender = models.StringField()
    maritalStatus = models.StringField()
    employmentStatus = models.StringField()
    householdIncome = models.StringField()
    # polarizing
    women = models.StringField()
    partisanship = models.StringField()
    immigration = models.StringField()
    climate_change = models.StringField()
    # neutral
    books = models.StringField()
    cities = models.StringField()
    cars = models.StringField()
    healthy_eating = models.StringField()
