from os import environ

EXTENSION_APPS = ["wedr"]
SESSION_CONFIGS = [
    dict(
        name='full',
        display_name="full",
        num_demo_participants=8,
        app_sequence=[
            'start',
            'wedr',
            'q'
        ]
    ),
    dict(
        name='wedr',
        display_name="wedr",
        num_demo_participants=8,
        app_sequence=['wedr']
    ),
    dict(
        name='start',
        display_name="start",
        num_demo_participants=18,
        app_sequence=['start']
    ),
    dict(
        name='q',
        display_name="post experimental q only",
        num_demo_participants=2,
        app_sequence=['q']
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    no_partner_url="https://app.prolific.co/submissions/complete?cc=NO_PARTNER",
    prolific_return_url="https://app.prolific.com/submissions/complete?cc=NO_CODE",
    for_prolific=True,
    real_world_currency_per_point=1.00, participation_fee=0.00, doc="",
    time_for_work=5 * 600
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'i@tj^rm09+(glgb3bu!*x0yugfe1p6n-r3b)2y-$)2d%rixtxs'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree', 'django_user_agents', ]

MIDDLEWARE_CLASSES = (
    'django_user_agents.middleware.UserAgentMiddleware',
)
USER_AGENTS_CACHE = 'default'
