import ssl

from requests.adapters import HTTPAdapter


class LenientHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT")
        super().init_poolmanager(connections, maxsize, block, **pool_kwargs, ssl_context=context)
