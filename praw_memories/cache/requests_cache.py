"""HTTP Caching for PRAW."""

import requests_cache


def get_requestscache_cache(cache_name='.cache', backend=None,
                            expire_after=None, allowable_codes=None,
                            allowable_methods=('GET',),
                            old_data_on_error=False, **backend_options):
    allowable_codes = allowable_codes or {200, 203, 300, 301, 302, 403, 404}
    cached_session = requests_cache.core.CachedSession(cache_name, backend,
                                                       expire_after,
                                                       allowable_codes,
                                                       allowable_methods,
                                                       old_data_on_error,
                                                       **backend_options)
    return cached_session


