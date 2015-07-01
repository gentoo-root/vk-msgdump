from oauthlib import oauth2
from requests_oauthlib import OAuth2Session
from time import monotonic, sleep

class VKError(Exception):
    pass

class VK(object):
    url_auth = 'https://oauth.vk.com/authorize'
    url_redirect = 'https://oauth.vk.com/blank.html'
    url_api = 'https://api.vk.com/method/{method:s}'

    def __init__(self, client_id, scope, api_ver='5.28'):
        assert isinstance(client_id, int)
        assert isinstance(scope, list)
        self._last_time = -1
        self._api_ver = api_ver
        self._params = {}
        self._session = OAuth2Session(scope=','.join(scope), redirect_uri=VK.url_redirect, client=oauth2.MobileApplicationClient(client_id=client_id, default_token_placement='query'))

    def auth_url(self, display='popup'):
        assert display in ['mobile', 'page', 'popup']
        url, state = self._session.authorization_url(VK.url_auth, v=self._api_ver, display=display)
        return url

    def auth_response(self, url):
        self._session.token_from_fragment(url)

    def set_params(self, params):
        # Useful params are lang, v, https and test_mode
        self._params = params
        self._params.setdefault('v', self._api_ver)

    def call(self, method, **kwargs):
        params = self._params.copy()
        params.update(kwargs)

        sleep(max(0, 1/3 - (monotonic() - self._last_time))) # burst limit 3/s
        reply = self._session.get(VK.url_api.format(method=method), params=params)
        self._last_time = monotonic()
        reply.raise_for_status()

        j = reply.json()
        if 'error' in j:
            raise VKError(j['error']['error_code'], j['error']['error_msg'])
        return j['response']

    def __getattr__(self, attr):
        return _VKMethodGroup(self, attr)

class _VKMethodGroup(object):
    def __init__(self, vk, group):
        self._vk = vk
        self._group = group

    def __getattr__(self, attr):
        return _VKMethod(self._vk, self._group, attr)

class _VKMethod(object):
    def __init__(self, vk, group, method):
        self._vk = vk
        self._group = group
        self._method = method

    def __call__(self, **params):
        return self._vk.call(self._group + '.' + self._method, **params)
