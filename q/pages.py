from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from django.shortcuts import redirect
import json
import logging
from json import JSONDecodeError
from pprint import pprint
from wedr.models import Constants as wedr_constants

logger = logging.getLogger(__name__)


class Feedback(Page):
    form_model = "player"
    form_fields = ["instructions_clarity", "purpose", "feedback"]


class FinalForProlific(Page):

    def get(self):
        full_return_url = self.session.config.get("prolific_return_url", "https://cnn.com")
        return redirect(full_return_url)


class Q1(Page):

    def post(self):
        raw_data = self.request.POST.get('survey_data')
        try:

            json_data = json.loads(raw_data)
            pprint(json_data)
            for k, v in json_data.items():
                try:
                    setattr(self.player, k, str(v))
                except AttributeError as e:
                    logger.error(
                        f'No such field at player level: {k} for value {v}. Player {self.player.participant.code}. Error: {e}')

        except JSONDecodeError as e:
            logger.error(str(e))
        print('*' * 100)
        return super().post()


class _GuessPage(Page):
    template_name = 'q/GuessPage.html'

    def get_rows(self):
        raise NotImplementedError

    def js_vars(self):
        rows = self.get_rows()

        # let's generate the list of value-text dicts from wedr_constants.polq_data based on partner_answers

        columns = [dict(value=k, text=v) for k, v in wedr_constants.response_mapping.items()]
        return dict(rows=rows, columns=columns)

    def post(self):
        raw_data = self.request.POST.get('survey_data', {})
        try:
            json_data = json.loads(raw_data)
            partner_answers = json_data.get('partner_answers', {})
            full_guess = self.participant.vars.get('current_guess',{})
            full_guess.update(partner_answers)
            self.participant.vars['current_guess'] = full_guess
            for k, v in partner_answers.items():
                try:
                    setattr(self.player, f'partner_{k}', (v))
                except AttributeError as e:
                    logger.error(
                        f'No such field at player level: {k} for value {v}. Player {self.player.participant.code}. Error: {e}')

        except JSONDecodeError as e:
            logger.error(str(e))
        return super().post()


class GuessAnswerPage(_GuessPage):
    alert = dict(text="Remember that you will receive a bonus if you get all your partner's answers correct below.",
                 color='warning')

    def get_rows(self):
        rows = [dict(value=i.get('name'), text=i.get('text')) for i in wedr_constants.polq_data if
                i.get('treatment') == self.participant.vars.get('treatment')]
        return rows
    def before_next_page(self):
        self.player.guess = json.dumps(self.participant.vars.get('current_guess',{}))
        self.player.results_order = self.player.id_in_group % 2 ==0
        self.player.set_payoffs()

class NonMonGuessAnswerPage(_GuessPage):
    alert = dict(text="Now we will ask you to guess your partner's answers to the rest of of the questions. <br>The correctness of the answers below <b>will not</b> affect your bonus.",
                 color='success')

    def get_rows(self):
        rows = [dict(value=i.get('name'), text=i.get('text')) for i in wedr_constants.polq_data if
                i.get('treatment') !=self.participant.vars.get('treatment')]
        return rows
    def before_next_page(self):
        self.player.guess = json.dumps(self.participant.vars.get('current_guess', {}))

class GuessResults(Page):
    template_name = 'q/GuessResults.html'
    def vars_for_template(self):
        current_guess = json.loads(self.player.guess)
        partner_answers = json.loads(self.player.partner_polq)

        # Merge the two dictionaries into a list of tuples or a new dictionary,
        # where each key is the statement and the values are tuples containing
        # the partner's answer and the current guess.
        combined_results = []
        polq_data = wedr_constants.polq_data
        for statement in polq_data:
            name = statement.get('name')
            if name in partner_answers and name in self.player.keys_needed:
                partner_answer_text = wedr_constants.response_mapping.get(partner_answers.get(name))
                combined_results.append({
                    'name': name,
                    'text': statement.get('text'),
                    'partner_answer_num': partner_answers.get(name),
                    'partner_answer_text': partner_answer_text,
                    'current_guess_num': current_guess.get(name, "No Guess"),
                    'current_guess_text': wedr_constants.response_mapping.get(current_guess.get(name, "No Guess")),
                    'color': 'bg-success' if partner_answers.get(name) == current_guess.get(name) else 'bg-warning'
                })

        # Return the combined list of dictionaries to the template
        return {'combined_results': combined_results}
class GuessResults1(GuessResults):
    def is_displayed(self):
        return self.player.results_order

class GuessResults2(GuessResults):
    def is_displayed(self):
        return not self.player.results_order
page_sequence = [
    GuessAnswerPage,
    NonMonGuessAnswerPage,
    GuessResults1,
    Q1,
    GuessResults2,
    # Feedback,
    # FinalForProlific
]
