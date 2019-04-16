import re
import json
import daiquiri
import logging

_PAGINATION_RE = re.compile('.*[?!]page=(\d+).*')
_DEFAULT_NO_COLOR_FORMAT = "%(asctime)s [%(process)d] %(levelname)-8.8s %(name)s: %(message)s"
_DEFAULT_COLOR_FORMAT = "%(asctime)s [%(process)d] %(color)s%(levelname)-8.8s %(name)s: %(message)s%(color_stop)s"


def setup_logging(verbose, no_color):
    """Set up logging facilities.

    :param verbose: verbosity level
    :type verbose: int
    :param no_color: do not use color in output
    :type no_color: bool
    """
    level = logging.WARNING
    if verbose == 1:
        level = logging.INFO
    elif verbose > 1:
        level = logging.DEBUG

    formatter = daiquiri.formatter.ColorFormatter(fmt=_DEFAULT_COLOR_FORMAT)
    if no_color:
        formatter = logging.Formatter(fmt=_DEFAULT_NO_COLOR_FORMAT)

    daiquiri.setup(level=level, outputs=(
        daiquiri.output.Stream(formatter=formatter),
    ))


def dict2json(dict_, pretty=True):
    """Convert dict to json (string).

    :param dict_: dictionary to be converted
    :type dict_: dict
    :param pretty: if True, nice formatting will be used
    :type pretty: bool
    :return: formatted dict in json
    :rtype: str
    """
    kwargs = {}
    if pretty:
        kwargs['sort_keys'] = True
        kwargs['separators'] = (',', ': ')
        kwargs['indent'] = 2

    return json.dumps(dict_, **kwargs)


def next_pagination_page(headers):
    """Parse next paginated page from headers.

    :param headers: response headers that were returned by GitHub
    """
    link = headers.get('Link')
    if link is None:
        # If there is no next page, GitHub does not provide 'Link'
        return

    parts = link.split(',')
    for part in parts:
        if not part.endswith('rel="next"'):
            continue

        matched = _PAGINATION_RE.match(part)
        return int(matched.group(1))
