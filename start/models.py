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
    players_per_group = None
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


def create_statement_page(statement):
    return {
        "name": f"{statement['name']}_page",
        "elements": [
            {
                "type": "html",
                "name": statement["name"],
                "html": f"<div class='lead text-center display-3' style='font-size:1.2rem'><i>{statement['text']}</i></div>"
            },
            {
                "type": "radiogroup",
                "name": f"{statement['name']}_guess",
                "title": "Please consider the statement above and indicate your guess by choosing one of the following options:",
                "choices": [
                    {'value': 0, 'text': "My partner has a similar opinion (similar answers to mine)"},
                    {'value': 1, 'text': "My partner has an opposite opinion (opposite answers to mine)"},

                ]
            }
        ]
    }


def make_guess_survey():
    stub = dict(pages=[], showPrevButton=False, completeText="Next", showCompletedPage=False, showProgressBar='auto',
                progressBarType="questions")
    polq_data = deepcopy(Constants.polq_data.copy())
    random.shuffle(polq_data)
    stub['pages'] = [create_statement_page(statement) for statement in polq_data]
    return stub


class Subsession(BaseSubsession):
    def group_by_arrival_time_method(self, waiting_players):
        if len(waiting_players) > 0:
            return waiting_players[:1]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    def start(self):
        qs = Constants.polq_data.copy()
        random.shuffle(qs)
        self.qs_order = json.dumps([q['name'] for q in qs])
        rendered_questionnaire = load_csv_to_survey_pages(qs, choices=Constants.response_mapping)
        # let's make a deepcopy of the survey_prototype
        full_q = deepcopy(Constants.survey_prototype)
        full_q['pages'].extend(rendered_questionnaire)
        self.participant.vars['full_q'] = full_q

    consent_accept = models.BooleanField(
        label="""
         I agree to participate in the current  study. I understand that I can withdraw my consent to participate at any time and by giving
                    consent I am not giving up any of my legal rights.""",
        widget=widgets.CheckboxInput
    )
    #     guessing block
    books_guess = models.IntegerField()
    cars_guess = models.IntegerField()
    cities_guess = models.IntegerField()
    immigration_guess = models.IntegerField()
    partisanship_guess = models.IntegerField()
    women_guess = models.IntegerField()

    full_neutral_set = models.StringField()
    full_polarizing_set = models.StringField()
    neutral_set = models.StringField()
    polarizing_set = models.StringField()
    survey_data = models.LongStringField()
    qs_order = models.StringField()
    # user agent block
    full_user_data = models.LongStringField()
    useragent_is_mobile = models.BooleanField()
    useragent_is_bot = models.BooleanField()
    useragent_browser_family = models.StringField()
    useragent_os_family = models.StringField()
    useragent_device_family = models.StringField()
    # political demographic quetionsnnaire fields: ['age', 'gender', 'maritalStatus', 'employmentStatus', 'householdIncome', 'women', 'partisanship', 'immigration', 'books', 'cities', 'cars']
    age = models.StringField()
    gender = models.StringField()
    maritalStatus = models.StringField()
    employmentStatus = models.StringField()
    householdIncome = models.StringField()
    women = models.StringField()
    partisanship = models.StringField()
    immigration = models.StringField()
    books = models.StringField()
    cities = models.StringField()
    cars = models.StringField()
