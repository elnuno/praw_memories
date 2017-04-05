import unittest

import praw_memories
import praw_memories.cache
from praw_memories.cache import betamax, cachecontrol, requests_cache


class BogusTest(unittest.TestCase):
    def test_something(self):
        c = praw_memories.get_config(section='mainuser')
        v = praw_memories.cache.CachingReddit(
            requestor_class=praw_memories.cache.betamax.CassetteRequestor, **c)
        v.redditor('elnuno')._fetch()
        v.redditor('ambersonata')._fetch()

        cache_session = praw_memories.cache.requests_cache.get_requestscache_cache()
        kwargs = dict(session=cache_session)
        v = praw_memories.cache.ModernCachingReddit(requestor_kwargs=kwargs, **c)
        v.redditor('elnuno')._fetch()
        v.redditor('ambersonata')._fetch()

        cache_session = praw_memories.cache.cachecontrol.get_cachecontrol_cache()
        kwargs = dict(session=cache_session)
        v = praw_memories.cache.ModernCachingReddit(caching_session=cache_session, **c)
        v.redditor('elnuno')._fetch()
        v.redditor('ambersonata')._fetch()


if __name__ == '__main__':
    unittest.main()
