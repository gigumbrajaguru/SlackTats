import requests
import os
import locale
import click
import json
from sys import exit
from importlib import import_module
from subprocess import call
from functools import partial


# HELPER FUNCTIONS
def _localization():
    '''Returns a module object containing all the help strings according to the
       locale of the user'''
    try:
        locale.setlocale(locale.LC_ALL, '')
        return import_module('.locales.{}'.format(locale.getlocale()[0]),
                             package='gitman')
    except ImportError:
        return import_module('.locales.en_US', package='gitman')


loc = _localization()


def api_call(method, token=None, verb=None):
    '''Sends an api call to github.com and returns the json contained.

    Args:
        method (str): Represents the URI to query for data.
        token (str or None): If provided, provides authorization for queries.

    Returns:
        tuple: Status code of the query and the json contained in the response.
    '''

    if token:
        token = {'Authorization': 'token {}'.format(token)}
    data = verb('https://api.github.com/{}'.format(method),
                headers=token)
    try:
        return data.status_code, data.json()
    except json.decoder.JSONDecodeError:
        click.echo(loc.API_ERROR)
        exit(1)


api_get = partial(api_call, verb=requests.get)
api_post = partial(api_call, verb=requests.post)
# END HELPER FUNCTIONS


@click.group(help=loc.DESCRIPTION)
@click.pass_context
def main(ctx):
    '''Entry point.'''
    if not os.path.exists(os.path.expanduser('~/.gitman')):
        _git_setup()

    with open(os.path.join(os.environ['HOME'], '.gitman'), 'r') as cf:
        ctx.obj = cf.readline()


@main.command(name='list', help=loc.LIST_HELP)
@click.pass_obj
@click.argument('user', nargs=1, required=False)
def git_list(token, user):
    '''Lists the repositories of a user.

    Args:
        token (str): To provide authorization for the call if needed.
        user (str): User to target in Github.

    Outputs:
        The list of the repositories belonging to the user to stdin.'''
    if user:
        status_code, repos_data = api_get('users/{}/repos'.format(user))
    else:
        status_code, repos_data = api_get('user/repos', token=token)

    if status_code == 200:
        click.echo(loc.LIST_USERNAME.format(repos_data[0]['owner']['login']))
        for repo in repos_data:
            click.echo('* {} - {}'.format(repo['full_name'], repo['description']))
    else:
        click.echo(loc.LIST_NOTFOUND.format(user))


def _git_setup():
    '''Stores the token provided by the user for future use.

    Inputs:
        A string from stdout representing the Github OAuth token of the caller.
        Required at least the "repos" permission, for now.

    Outputs:
        A file ".gitman" on the $HOME of the user containing this token string.

    TODO:
        - Maybe allow the user to delete his own repositories if given a valid
        token.
    '''
    with open(os.path.expanduser('~/.gitman'), 'w') as cf:
        click.echo(loc.SETUP_INSTRUCTIONS)
        token = click.prompt(loc.SETUP_INPUT, type=str)
        if click.confirm(loc.SETUP_CONFIRM, abort=True):
            cf.write(token)

@main.command(name='setup', help=loc.SETUP_HELP)
def git_setup():
    '''CLI wrapper for _git_setup.'''
    _git_setup()


@main.command(name='clone', help=loc.CLONE_HELP)
@click.pass_obj
@click.argument('repo', metavar='[USERNAME/]REPO')
def git_clone(token, repo):
    '''Clones a given repository.

    Args:
        token (str): Always passed by the main software, serves to identify the
                     user in case it is not specified in the repo name.
        repo (str): Name of the repository to clone, in the format
                    <username?>/<repo_name>.

    Outputs:
        Calls 'git' and clones the specified repository in the CWD.

    '''
    if len(repo.split('/')) == 1:
        _, user_data = api_get('user', token)
        repo = '{}/{}'.format(user_data['login'], repo)
    try:
        call(['git', 'clone', 'https://github.com/{}'.format(repo)])
    except FileNotFoundError:
        click.echo(loc.CLONE_NOTFOUND)


@main.command(name='fork', help=loc.FORK_HELP)
@click.pass_obj
@click.argument('repo', metavar='USERNAME/REPO')
def git_fork(token, repo):
    '''Forks the repository of a user into the authenticated user.

    Args:
        token (str): Passed down by the main software, necessary to ID the user
                     requesting the fork.
        repo (str): In the format <username>/<repository>, targets the repo to
                    fork.
    '''
    repo_data = repo.split('/')
    if len(repo_data) != 2:
        click.echo(loc.FORK_SYNTAXERROR)
        exit(1)
    status_code, result = api_post('repos/{0}/forks'.format(repo), token)
    if status_code == 202 and result['owner']['login'] != repo_data[0]:
        click.echo(loc.FORK_SUCCESS.format(result['full_name'], repo))
    elif result['owner']['login'] == repo_data[0]:
        click.echo(loc.FORK_SELFERROR)
    else:
        click.echo(loc.FORK_NOTFOUND.format(repo))


if __name__ == '__main__':
    main()
