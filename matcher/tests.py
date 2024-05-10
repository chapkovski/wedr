from otree.api import Currency as c, currency_range, Submission
from . import pages
from ._builtin import Bot
from .models import Constants
import random
import json


def generate_random_response():
    # Define the choices for each question
    choices = {
        'age': ["Under 18", "18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 - 64", "65 - 74", "75 - 84", "85 or older"],

        'employmentStatus': ["Employed full time (35 or more hours per week)",
                             "Employed part time (up to 34 hours per week)",
                             "Unemployed and currently looking for work", "Unemployed not currently looking for work",
                             "Student", "Retired", "Homemaker", "Self-employed", "Unable to work"],
        'gender': ["Male", "Female", "Other", "Prefer not to say"],
        'householdIncome': ["$1,000 - $2,000", "$2,000 - $5,000", "$5,000 - $10,000", "$10,000 - $25,000",
                            "$25,000 - $50,000", "$50,000 - $75,000", "$75,000 - $100,000", "$100,000 - $150,000",
                            "More than $150,000", "Prefer not to answer"],
        'immigration': list(range(0, 6)),  # Assuming scale 0-5
        'maritalStatus': ["Single (never married)", "Married, or in a domestic partnership", "Widowed", "Divorced",
                          "Separated"],
        'partisanship': list(range(0, 6)),  # Assuming scale 0-5
        'women': list(range(0, 6)),  # Assuming scale 0-5,
        'books': list(range(0, 6)),
        'cars': list(range(0, 6)),
        'cities': list(range(0, 6)),
        'climate_change': list(range(0, 6)),
        'healthy_eating': list(range(0, 6)),
    }

    # Generate a random response for each question
    response = {key: random.choice(value) for key, value in choices.items()}
    return response


class PlayerBot(Bot):
    def play_round(self):
        yield pages.IntroToPol
        raw_data = json.dumps(generate_random_response())
        yield Submission(pages.PolPage, dict(survey_data=raw_data,
                                             ), check_html=False)

