import praw
from packaging.version import Version


class LegacyCachingReddit(praw.Reddit):
    def __init__(self, site_name=None, caching_session=None,
                 requestor_class=None, requestor_kwargs=None,
                 **config_settings):
        super().__init__(site_name=site_name, **config_settings)

        if caching_session:
            self._core._requestor._http = caching_session

    def _prepare_prawcore(self, *args, **kwargs):
        super()._prepare_prawcore(*args, **kwargs)


class ModernCachingReddit(praw.Reddit):
    def __init__(self, site_name=None, requestor_class=None,
                 requestor_kwargs=None, caching_session=None,
                 **config_settings):
        if not requestor_kwargs:
            requestor_kwargs = {}
        requestor_kwargs['session'] = caching_session
        super().__init__(site_name, requestor_class, requestor_kwargs,
                         **config_settings)


_ver = Version(praw.__version__)
_minver = Version('4.4.0')
CachingReddit = ModernCachingReddit if _ver >= _minver else LegacyCachingReddit
