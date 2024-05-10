from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import json
from json import JSONDecodeError
from pprint import pprint
from wedr.models import Constants as wedr_constants
import logging
from datetime import timedelta, datetime, timezone
from pprint import pprint

logger = logging.getLogger(__name__)
from django_user_agents.utils import get_user_agent


class Consent(Page):
    def get(self, *args, **kwargs):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        if ip:
            self.player.ip_address = ip
        user_agent = get_user_agent(self.request)
        logger.info(f'User agent: {user_agent}')
        self.player.full_user_data = json.dumps(user_agent.__dict__)
        self.player.useragent_is_mobile = user_agent.is_mobile
        self.player.useragent_is_bot = user_agent.is_bot
        self.player.useragent_browser_family = user_agent.browser.family
        self.player.useragent_os_family = user_agent.os.family
        self.player.useragent_device_family = user_agent.device.family
        return super().get()

    def vars_for_template(self):
        return dict(num_words=wedr_constants.num_rounds)

    form_model = 'player'
    form_fields = ['consent_accept']


class Intro(Page):
    def vars_for_template(self):
        return dict(num_puzzles=wedr_constants.num_rounds)


class Instructions1(Page):
    def vars_for_template(self):
        return dict(show_images=True, num_puzzles=wedr_constants.num_rounds)


class Instructions2(Page):
    def vars_for_template(self):
        return dict(show_images=True, num_puzzles=wedr_constants.num_rounds)


class CQPage(Page):
    pass


page_sequence = [
    Consent,
    Intro,
    Instructions1,
    Instructions2,
    CQPage,
]
