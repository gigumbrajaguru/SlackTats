import attr

from datetime import datetime
import time
import typing
import logging
from .configuration import Configuration
import requests
import copy
from .exceptions import MissingPassword
from .exceptions import HTTPError
from .utils import next_pagination_page

_LOG = logging.getLogger(__name__)


@attr.s
class GitHubHandlerBase(object):
    DEFAULT_PER_PAGE: typing.ClassVar[int] = Configuration().per_page_listing
    config: typing.ClassVar[Configuration] = Configuration()

    @classmethod
    def call(cls, uri, payload=None, method=None):
        requests_kwargs = {
            'headers': copy.copy(Configuration().headers)
        }

        if Configuration().token:
            _LOG.debug("Using OAuth2 token '%s***' for GitHub call", Configuration().token[:4])
            requests_kwargs['headers']['Authorization'] = 'token {!s}'.format(Configuration().token)
        elif Configuration().user:
            if not Configuration().password:
                raise MissingPassword("No password set for user {!s}".format(Configuration().user))

            _LOG.debug("Using basic authentication for user %s", Configuration().user)
            requests_kwargs['auth'].append((Configuration().user, Configuration().password))
        else:
            _LOG.debug("No authentication is used")

        url = "{!s}/{!s}".format(Configuration().github_api, uri)
        requests_func = getattr(requests, method.lower())
        if payload:
            requests_kwargs['json'] = payload

        while True:
            _LOG.debug("%s %s", method, url)
            response = requests_func(url, **requests_kwargs)

            _LOG.debug("Request took %s and the HTTP status code for response was %d",
                       response.elapsed, response.status_code)

            if not (response.status_code == 403 and
                    response.json()['message'].startswith("API rate limit exceeded") and
                    cls.config.omit_rate_limiting):
                break

            reset_datetime = datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
            sleep_time = (reset_datetime - datetime.now()).total_seconds()
            _LOG.debug("API rate limit hit, retrying in %d seconds...", sleep_time)
            time.sleep(sleep_time)

        try:
            # Rely on request's checks here
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise HTTPError(response.json(), response.status_code) from exc

        return response.json(), response.headers

    @classmethod
    def head(cls, *args, **kwargs):
        return cls.call(*args, **kwargs, method='HEAD')

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.call(*args, **kwargs, method='GET')

    @classmethod
    def post(cls, *args, **kwargs):
        return cls.call(*args, **kwargs, method='POST')

    @classmethod
    def patch(cls, *args, **kwargs):
        return cls.call(*args, **kwargs, method='PATCH')

    @classmethod
    def put(cls, *args, **kwargs):
        return cls.call(*args, **kwargs, method='PUT')

    @classmethod
    def delete(cls, *args, **kwargs):
        return cls.call(*args, **kwargs, method='DELETE')

    def _do_listing(self, base_uri):
        while True:
            uri = '{!s}?{!s}'.format(base_uri, self._get_query_string())
            response, headers = self.get(uri)

            for entry in response:
                yield entry

            if not self.config.pagination:
                return

            next_page = next_pagination_page(headers)
            if next_page is None:
                return
            self.page = next_page


class GitHubBase(object):
    pass
