from otree.api import Currency as c, currency_range, Submission
from .pages import *
from ._builtin import Bot
import json
import random
from .models import Constants


def random_answer(rows):
    keys = [r['value'] for r in rows]
    return dict(partner_answers={k: random.randint(0, 5) for k in keys})


class PlayerBot(Bot):
    def play_round(self):
        rows = GuessAnswerPage.get_rows(self.participant)
        answer = random_answer(rows)
        yield Submission(GuessAnswerPage, dict(survey_data=json.dumps(answer)), check_html=False)
        rows = NonMonGuessAnswerPage.get_rows(self.participant)
        answer = random_answer(rows)
        yield Submission(NonMonGuessAnswerPage, dict(survey_data=json.dumps(answer)), check_html=False)
        if self.player.results_order:
            yield GuessResults1,
        q1_data = {'interest_in_us_politics': 'Moderately interested',
                   'opinion_impact': random.randint(1, 5),
                   'partner_effort':  random.randint(1, 5),
                   'political_discussion_at_work': 'Appropriate',
                   'political_orientation':  random.randint(1, 5),
                   'self_effort':  random.randint(1, 5),
                   'team_communication_effectiveness':  random.randint(1, 5),
                   'team_satisfaction': 'Dissatisfied'}

        yield Submission(Q1, dict(survey_data=json.dumps(q1_data)), check_html=False)
        if not self.player.results_order:
            yield GuessResults2,

        yield Feedback, dict(feedback='Great study!', instructions_clarity=5,
                             purpose='To learn about political opinions')
