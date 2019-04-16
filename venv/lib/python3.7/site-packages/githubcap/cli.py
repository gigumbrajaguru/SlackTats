#!/usr/bin/env python3

import sys
import click
import attr

from githubcap import __version__ as githubcap_version
from githubcap import Configuration
from githubcap.resources import IssuesHandler
from githubcap.resources import IssueHandler
from githubcap.utils import dict2json
from githubcap.utils import setup_logging
import logging
from functools import partial

_ISSUES = IssuesHandler()
_LOG = logging.getLogger(__name__)


def _print_version(ctx, _, value):
    """Print version information and exit."""
    if not value or ctx.resilient_parsing:
        return

    click.echo("{!s}".format(githubcap_version))
    ctx.exit()


def _print_result(result, pretty=True):
    """Print results.

    :param result: a result to be printed
    :param pretty: print result in a pretty way
    :type pretty: bool
    """
    if pretty:
        result = dict2json(result)

    click.echo("{!s}".format(result))


def get_type(class_, attr_name):
    """Get type of attribute in a class."""
    return getattr(attr.fields(class_), attr_name).type


def get_choices(class_, attr_name):
    """Get all choices for an enum."""
    return get_type(class_, attr_name).all_names()


def _parse_cli_headers(text_headers):
    """Parse headers supplied from command line.

    :param text_headers: headers supplied as a text
    :type text_headers: str
    :return: a dictionary representation of headers
    :rtype: dict
    """
    headers = {}
    for header in text_headers.split(','):
        parts = header.split(':', maxsplit=1)
        if len(parts) != 2:
            raise ValueError("Unknown header supplied {!r}, headers should be set as key:value".format(header))

        headers[parts[0]] = parts[1]

    return headers


def _issues_choice_callback(enum, _, param, value):
    """Translate the given value to enum representation."""
    if value is None:
        return
    return getattr(enum, value)


@click.group()
@click.pass_context
@click.option('-v', '--verbose', count=True,
              help="Be verbose about what's going on (can be supplied multiple times).")
@click.option('--version', is_flag=True, is_eager=True, callback=_print_version, expose_value=False,
              help="Print githubcap version and exit.")
@click.option('--no-color', '-C', is_flag=True,
              help="Suppress colorized logging output.")
@click.option('-u', '--user', type=str, envvar='GITHUB_USER', metavar='GITHUB_USER',
              help="GitHub user name.")
@click.option('-p', '--password', type=str, envvar='GITHUB_PASSWORD', metavar='GITHUB_PASSWORD',
              help="GitHub password.")
@click.option('-t', '--token', type=str, envvar='GITHUB_TOKEN', metavar='TOKEN',
              help="Github OAuth2 token.")
@click.option('-R', '--no-omit-rate-limiting', is_flag=True,
              help="Do not omit rate limiting - raise an exception if rate limit exceeds.")
@click.option('-P', '--no-pagination', is_flag=True,
              help="Respect pagination - perform multiple API calls on paginated response.")
@click.option('-H', '--headers', type=str,
              help="A comma separated list of headers to be sent.")
@click.option('-l', '--per_page_listing', type=int, show_default=True, default=Configuration().per_page_listing,
              help="Number of entries in page listing in a single API call.")
@click.option('--github-api', type=str, default=Configuration().github_api, show_default=True,
              help="GitHub API endpoint.")
@click.option('--no-validate-schemas', '-S', is_flag=True,
              help="GitHub API endpoint.")
def cli(ctx=None, verbose=0, no_color=True, user=None, password=None, token=None, no_validate_schemas=False,
        no_omit_rate_limiting=False, no_pagination=False, headers=None, per_page_listing=None, github_api=None):
    """Githubcap command line interface."""
    if ctx:
        ctx.auto_envvar_prefix = 'GITHUBCAP'

    setup_logging(verbose, no_color)

    if user is not None:
        Configuration().user = user
    if password is not None:
        Configuration().password = password
    if token is not None:
        Configuration().token = token
    if per_page_listing is not None:
        Configuration().per_page_listing = per_page_listing
    if github_api is not None:
        Configuration().github_api = github_api
    if headers is not None:
        Configuration().headers = _parse_cli_headers(headers)

    Configuration().omit_rate_limiting = not no_omit_rate_limiting
    Configuration().pagination = not no_pagination
    Configuration().validate_schemas = not no_validate_schemas
    _LOG.debug("Configuration: %s", attr.asdict(Configuration().instance))


@cli.command('issues-listing')
@click.option('--no-pretty', is_flag=True,
              help="Print results in a well formatted manner.")
@click.option('--organization', '-o', type=str, default=None, metavar='ORGANIZATION',
              help="GitHub owner - GitHub user name or organization name.")
@click.option('--project', '-p', type=str, default=None, metavar='PROJECT_NAME',
              help="GitHub project name.")
@click.option('--page', default=_ISSUES.page, show_default=True,
              help="Page in paginating to start with.")
@click.option('--filter', '-f', default=_ISSUES.filter.name, type=click.Choice(get_choices(IssuesHandler, 'filter')),
              callback=partial(_issues_choice_callback, get_type(IssuesHandler, 'filter')), show_default=True,
              help="Filter issues based on assigned state.")
@click.option('--state', '-s', default=_ISSUES.state.name, type=click.Choice(get_choices(IssuesHandler, 'state')),
              callback=partial(_issues_choice_callback, get_type(IssuesHandler, 'state')), show_default=True,
              help="Filter issues based on issue state.")
@click.option('--labels', default=_ISSUES.labels, type=str, show_default=True,
              help="Filter issues based on labels - a comma separated list.")
@click.option('--sort', default=_ISSUES.sort.name, type=click.Choice(get_choices(IssuesHandler, 'sort')),
              callback=partial(_issues_choice_callback, get_type(IssuesHandler, 'sort')), show_default=True,
              help="Sorting criteria.")
@click.option('--direction', default=_ISSUES.direction.name, type=click.Choice(get_choices(IssuesHandler, 'direction')),
              callback=partial(_issues_choice_callback, get_type(IssuesHandler, 'direction')), show_default=True,
              help="Sorting direction.")
@click.option('--since', default=_ISSUES.since, type=str, show_default=True,
              help="List issues updated at or after the given time.")
@click.option('--milestone', '-m', default=_ISSUES.milestone, type=str, show_default=True,
              help="List issues with the given milestone.")
@click.option('--assignee', '-a', default=_ISSUES.assignee, type=str, metavar="USER", show_default=True,
              help="Filter issues based on assignee.")
@click.option('--creator', '-c', default=_ISSUES.creator, type=str, metavar="USER", show_default=True,
              help="Filter issues based on creator.")
@click.option('--mentioned', '-m', default=_ISSUES.mentioned, type=str, metavar="USER", show_default=True,
              help="Filter issues based on mentioned user.")
def issues_listing(organization=None, project=None, no_pretty=False, **issues_attributes):
    """List GitHub issues."""
    issues = IssuesHandler(**issues_attributes)
    _LOG.debug("Issues listing query: %s", issues)
    if project is None:
        reported_issues = issues.list_assigned_issues(organization)
    else:
        reported_issues = issues.list_issues(organization, project)
    _print_result(list(reported_issues), not no_pretty)


@cli.command('issue')
@click.option('--no-pretty', is_flag=True,
              help="Print results in a well formatted manner.")
@click.option('--organization', '-o', type=str, default=None, metavar='ORGANIZATION', required=True,
              help="GitHub owner - GitHub user name or organization name.")
@click.option('--project', '-p', type=str, default=None, metavar='PROJECT_NAME', required=True,
              help="GitHub project name.")
@click.option('--number', '-i', type=int, metavar='ID',
              help="Issue number (issue identifier).")
@click.option('--title', '-t', type=str, metavar='TITLE',
              help="")
@click.option('--body', '-b', type=str, metavar='DESCRIPTION',
              help="")
@click.option('--milestone', '-m', type=str, metavar='MILESTONE_ID',
              help="")
@click.option('--labels', '-l', type=str, metavar='LABEL1,LABEL2,..',
              help="")
@click.option('--assignees', '-a', type=str, metavar='USER1,USER2,..',
              help="")
@click.option('--state', '-s', default=None, type=click.Choice(get_choices(IssuesHandler, 'state')),
              callback=partial(_issues_choice_callback, get_type(IssuesHandler, 'state')), show_default=True,
              help="Filter issues based on issue state.")
def cli_issue(no_pretty=False, organization=None, project=None, number=None, **issue_attributes):
    """Retrieve or modify a GitHub issue."""
    _LOG.debug("Issue query: %s", issue_attributes)

    #issue = IssueHandler(**issue_attributes).modify(organization, project, number)
    #_print_result(issue, not no_pretty)

    if all(val is None for val in issue_attributes.values()):
        if number is None:
            raise ValueError("Wrong issue ID supplied")
        issue = IssueHandler.by_id(organization, project, number)
        _print_result(issue, not no_pretty)
    else:
        raise NotImplementedError

    #else:
    #    if issue_attributes['title'] is None:
    #        raise ValueError
    #    issue = IssueHandler(**issue_attributes).create(organization, project)
    #    _print_result(issue, not no_pretty)


if __name__ == '__main__':
    sys.exit(cli())
