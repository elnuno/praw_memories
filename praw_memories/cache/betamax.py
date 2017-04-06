import json
import os.path
from base64 import b64encode
import string

import betamax
import betamax.cassette.cassette
import prawcore
import requests
from betamax_serializers import pretty_json
from prawcore import RequestException
from prawcore.const import TIMEOUT

betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

ACCEPTABLE = set(string.digits + string.ascii_letters + '_-')
CLEAN_TABLE = str.maketrans(r' /\,+@#$.', '_' * 9)


def b64_string(input_string):
    """Return a base64 encoded string (not bytes) from input_string."""
    return b64encode(input_string.encode('utf-8')).decode('utf-8')


class CassetteRequestor(prawcore.Requestor):
    def __init__(self, user_agent, oauth_url='https://oauth.reddit.com',
                 reddit_url='https://www.reddit.com', session=None,
                 cacheable_methods=None, wrapper=None, **betamaxkwargs):
        super().__init__(user_agent, oauth_url, reddit_url, session)
        self.cacheable_methods = cacheable_methods or {'GET'}
        self.betamax = wrapper or get_betamax_cache(self._http, **betamaxkwargs)

    @staticmethod
    def get_cassette_name_from_url(url):
        oauth = 'https://oauth.reddit.com/'
        cassette_name = url.replace(oauth, '').translate(CLEAN_TABLE)
        cassette_name = ''.join(c for c in cassette_name if c in ACCEPTABLE)
        return cassette_name

    def request(self, *args, **kwargs):
        try:
            if args[0] in self.cacheable_methods:
                cassette_name = self.get_cassette_name_from_url(args[1])
                with self.betamax.use_cassette(cassette_name):
                    response = self._http.request(*args, timeout=TIMEOUT,
                                                  **kwargs)
            else:
                response = self._http.request(*args, timeout=TIMEOUT, **kwargs)
        except Exception as exc:
            raise RequestException(exc, args, kwargs)

        return response


def get_betamax_cache(session=None, cassette_library_dir='.praw_cassettes',
                      default_cassette_options=None, record_mode='once'):
    with betamax.Betamax.configure() as config:
        placeholders = {}
        # placeholders['basic_auth'] = b64_string(
        # '{}:{}'.format(placeholders['client_id'],
        #                placeholders['client_secret']))
        config.before_record(callback=filter_access_token)
        for key, value in placeholders.items():
            config.define_cassette_placeholder('<{}>'.format(key.upper()),
                                               value)

    session = session or requests.Session()
    default = dict(serialize_with='prettyjson', record_mode=record_mode)
    default_cassette_options = default_cassette_options or default
    if not os.path.exists(cassette_library_dir):
        os.mkdir(cassette_library_dir)
    wrapped = betamax.Betamax(session, cassette_library_dir,
                              default_cassette_options)
    return wrapped


def filter_access_token(interaction, current_cassette):
    """Add Betamax placeholder to filter access token."""
    request_uri = interaction.data['request']['uri']
    response = interaction.data['response']
    if ('api/v1/access_token' not in request_uri or
            response['status']['code'] != 200):
        return
    body = response['body']['string']
    try:
        token = json.loads(body)['access_token']
    except (KeyError, TypeError, ValueError):
        return
    current_cassette.placeholders.append(
            betamax.cassette.cassette.Placeholder(placeholder='<ACCESS_TOKEN>',
                                                  replace=token))
