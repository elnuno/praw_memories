import json
from os import path
import os
from types import SimpleNamespace
import unittest
from unittest import mock

import betamax
from prawcore import exceptions, Requestor, RequestException

import praw_memories
import praw_memories.cache
import praw_memories.cache.betamax


@unittest.skip('Cheat!')
class BogusTest(unittest.TestCase):
    def test_something(self):
        c = praw_memories.get_config()
        v = praw_memories.cache.CachingReddit(
                requestor_class=praw_memories.cache.betamax.CassetteRequestor,
                **c)
        v.redditor('elnuno')._fetch()
        v.redditor('ambersonata')._fetch()

        cache_session = \
            praw_memories.cache.requests_cache.get_requestscache_cache()
        kwargs = dict(session=cache_session)
        v = praw_memories.cache.ModernCachingReddit(requestor_kwargs=kwargs,
                                                    **c)
        v.redditor('elnuno')._fetch()
        v.redditor('ambersonata')._fetch()

        cache_session = \
            praw_memories.cache.cachecontrol.get_cachecontrol_cache()
        kwargs = dict(session=cache_session)
        v = praw_memories.cache.ModernCachingReddit(
                caching_session=cache_session, **c)
        v.redditor('elnuno')._fetch()
        v.redditor('ambersonata')._fetch()


placeholders = ('auth_code client_id client_secret password redirect_uri '
                'test_subreddit user_agent username').split()

placeholders = {key: key.upper() for key in placeholders}


class TestCache(unittest.TestCase):
    def test_legacy_caching_reddit(self):
        LCR = praw_memories.cache.LegacyCachingReddit
        bogus = LCR(caching_session=None, requestor_class=None,
                    requestor_kwargs=None, **placeholders)
        self.assertRaises(exceptions.ResponseException,
                          bogus.redditor('spez')._fetch)
        marker = object()
        use_session = LCR(caching_session=marker, **placeholders)
        self.assertIs(use_session._core._requestor._http, marker)

    def test_modern_caching_reddit(self):
        MCR = praw_memories.cache.ModernCachingReddit
        bogus = MCR(caching_session=None, requestor_class=None,
                    requestor_kwargs=None, **placeholders)
        self.assertRaises(exceptions.ResponseException,
                          bogus.redditor('spez')._fetch)
        marker = object()
        placeholders['caching_session'] = marker
        self.assertRaisesRegex(AttributeError, 'headers', MCR, **placeholders)

        class CustomRequestor(Requestor):
            pass

        placeholders['requestor_class'] = CustomRequestor
        placeholders.pop('caching_session')
        with_class = MCR(**placeholders)
        self.assertIsInstance(with_class._core._requestor, CustomRequestor)
        session = mock.Mock(headers={})
        with_caching_session = MCR(caching_session=session, **placeholders)
        self.assertIs(with_caching_session._core._requestor._http, session)
        placeholders['requestor_kwargs'] = {'session': session}
        placeholders['requestor_class'] = None
        with_session = MCR(**placeholders)
        self.assertIs(with_session._core._requestor._http, session)
        placeholders['caching_session'] = session
        self.assertRaisesRegex(ValueError, 'Cannot pass session both', MCR,
                               **placeholders)


class TestBetamax(unittest.TestCase):
    def setUp(self):
        self.config = betamax.Betamax.configure()
        self.config.cassette_library_dir = 'cassettes'
        self.config.default_cassette_options['record_mode'] = 'once'

    def test_cassette_requestor(self):
        CassetteRequestor = praw_memories.cache.betamax.CassetteRequestor
        UA = 'Dummy' * 3

        requestor = CassetteRequestor(UA)
        self.assertIsInstance(requestor.betamax, betamax.Betamax)
        self.assertEqual(requestor.cacheable_methods, {'GET'})
        session = mock.Mock(headers={})
        requestor = CassetteRequestor(UA, session=session, cacheable_methods=1)
        self.assertIs(requestor._http, session)
        self.assertEqual(requestor.cacheable_methods, 1)

        nasty = 'Çç¨:~^phony_name\\\n23*&"""´´s..@@'
        filtered = CassetteRequestor.get_cassette_name_from_url(nasty)
        self.assertEqual(filtered, 'phony_name_23s____')
        with_oauth = 'https://oauth.reddit.com/blahblahblah'
        filtered = CassetteRequestor.get_cassette_name_from_url(with_oauth)
        self.assertEqual(filtered, 'blahblahblah')
        with_http = 'http://oauth.reddit.com/blahblahblah'
        filtered = CassetteRequestor.get_cassette_name_from_url(with_http)
        self.assertEqual(filtered, 'http__oauth_reddit_com_blahblahblah')

        requestor = CassetteRequestor(UA, cacheable_methods=('PUT',))
        response = requestor.request(*('GET', 'https://httpbin.org/get'))
        self.assertTrue(response.ok)
        self.assertRaises(RequestException, requestor.request,
                          *('GET', 'ahttps://httpbin.org/get'))

        self.config.cassette_library_dir = 'cassettes'
        cassettes = self.config.cassette_library_dir
        url_1 = 'https://httpbin.org/get'
        url_2 = with_http
        cassette1_name = requestor.get_cassette_name_from_url(url_1) + '.json'
        cassette2_name = requestor.get_cassette_name_from_url(url_2) + '.json'

        cassette1_path = path.join('tests', cassettes, cassette1_name)
        cassette2_path = path.join('tests', cassettes, cassette2_name)
        dir_exists = False
        if path.exists(cassette1_path):
            os.unlink(cassette1_path)
            dir_exists = True
        if path.exists(cassette2_path):
            os.unlink(cassette2_path)
            dir_exists = True
        if dir_exists:
            os.rmdir(path.join('tests', cassettes))
        requestor = CassetteRequestor(UA, cacheable_methods=('GET',),
                                      **dict(cassette_library_dir=path.join('tests', cassettes)))


        requestor.request(*('GET', url_1))
        requestor.request(*('GET', url_2))
        self.assertTrue(path.exists(cassette1_path))
        self.assertTrue(path.exists(cassette2_path))
        os.unlink(cassette1_path)
        os.unlink(cassette2_path)
        os.rmdir(path.join('tests', cassettes))

    def test_get_betamax_cache(self):
        pass

    def test_filter_access_token(self):
        filter_access_token = praw_memories.cache.betamax.filter_access_token
        interaction = SimpleNamespace()
        interaction.data = {
            'request': {'uri': 'abc'}, 'response': {
                'status': {'code': 200}, 'body': {'string': ''}}}
        self.assertIs(filter_access_token(interaction, None), None)
        interaction.data['response']['status']['code'] = 300
        self.assertIs(filter_access_token(interaction, None), None)
        interaction.data['response']['status']['code'] = 200
        interaction.data['request']['uri'] = 'api/v1/access_token'
        self.assertIs(filter_access_token(interaction, None), None)
        token = json.dumps({'access_token': 12345})
        interaction.data['response']['body']['string'] = token
        cassette = SimpleNamespace()
        cassette.placeholders = []
        self.assertIs(filter_access_token(interaction, cassette), None)
        self.assertEqual(len(cassette.placeholders), 1)


class TestCacheControl(unittest.TestCase):
    def test_radical_cache_controller(self):
        pass

    def test_extended_cache_control(self):
        pass

    def test_get_cachecontrol_cacher(self):
        pass


class TestRequestsCache(unittest.TestCase):
    def test_get_requestscache_cache(self):
        pass


if __name__ == '__main__':
    unittest.main()
