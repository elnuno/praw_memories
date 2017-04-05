import requests
from cachecontrol import controller, heuristics, adapter as adapters
from cachecontrol.caches import file_cache


class RadicalCacheController(controller.CacheController):
    """Cache 302 redirects, 403 and 404 errors plus those in base class."""

    def __init__(self, cache=None, cache_etags=True, serializer=None,
                 status_codes=None):

        status_codes = status_codes or {200, 203, 300, 301, 302, 403, 404}
        super().__init__(cache, cache_etags, serializer, status_codes)

    @classmethod
    def _urlnorm(cls, uri):
        """Normalize the URL to create a safe key for the cache.
        
        Hacked version from upstream that sorts query parameters."""
        (scheme, authority, path, query, fragment) = controller.parse_uri(uri)
        if not scheme or not authority:
            raise Exception("Only absolute URIs are allowed. uri = %s" % uri)

        scheme = scheme.lower()
        authority = authority.lower()

        if not path:
            path = "/"
        if query:
            query = '&'.join(sorted(query.split('&')))
        # Could do syntax based normalization of the URI before
        # computing the digest. See Section 6.2.2 of Std 66.
        request_uri = query and "?".join([path, query]) or path
        defrag_uri = scheme + "://" + authority + request_uri

        return defrag_uri


def ExtendedCacheControl(sess, cache=None, cache_etags=True, serializer=None,
                         heuristic=None, controller_class=None,
                         adapter_class=None, cacheable_methods=None):
    cache = cache or controller.DictCache()
    adapter_class = adapter_class or adapters.CacheControlAdapter
    adapter = adapter_class(cache, cache_etags=cache_etags,
                            serializer=serializer, heuristic=heuristic,
                            controller_class=controller_class)
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)

    return sess


def get_cachecontrol_cache(session=None, cache=None, heuristic=None,
                           controller_class=None, path='.praw_cache',
                           forever=True):
    session = session or requests.Session()
    cache = cache or file_cache.FileCache(path, forever=forever,
                                          use_dir_lock=True)
    controller_class = controller_class or RadicalCacheController
    heuristic = heuristic or heuristics.ExpiresAfter(days=1)
    sess = ExtendedCacheControl(session, cache=cache,
                                heuristic=heuristic,
                                controller_class=controller_class)
    return sess
