import sys
from subprocess import STDOUT
from subprocess import CalledProcessError
from subprocess import call
from subprocess import check_output

if sys.version_info[0] > 2:
    NOT_A_GIT_REPO_STDERR = b'Not a git repository'
else:
    NOT_A_GIT_REPO_STDERR = 'Not a git repository'


class GitRepoNotFound(CalledProcessError):
    """Raised when trying to instantiate a GitRepo object on a file path that is not a git repo."""
    pass


class GitCommandException(CalledProcessError):
    """Raised for any other git command failures."""
    pass


# def is_git_url(url=None):
#     return bool(re.match(r'((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?'), url)


class GitRepo(object):
    def __init__(self, path=None):
        self._path = path
        self.base_command = ['git']
        if path is not None:
            self.base_command += ['-C', path]
        try:
            # Ensure that either the current working directory, or the specified path, is part of a git repository.
            self._check_output(['rev-parse'])
        except GitCommandException as command_error:
            if NOT_A_GIT_REPO_STDERR in command_error.output:
                raise GitRepoNotFound(*command_error.args)

    def _check_output(self, command):
        """Wrap the call to subprocess.check_output() to raise customized exceptions and always return strings."""
        try:
            if sys.version_info[0] > 2:
                return check_output(self.base_command + command, stderr=STDOUT).decode('utf8')
            else:
                return check_output(self.base_command + command, stderr=STDOUT)
        except CalledProcessError as command_error:
            raise GitCommandException(*command_error.args)

    def _call(self, command):
        return call(self.base_command + command)

    @property
    def top_level_directory_path(self):
        """What is the top level directory of the git repo."""
        return self._check_output(['rev-parse', '--show-toplevel'])

    @property
    def is_dirty(self):
        return bool(self._call(['diff', '--cached', '--quiet']))

    @property
    def branch(self):
        return self._check_output(['branch'])[2:-1]

    @property
    def configured_options(self):
        """What are the configured options in the git repo."""
        stdout_lines = self._check_output(['config', '--list']).splitlines()
        return {key: value for key, value in [line.split('=') for line in stdout_lines]}

    @property
    def remotes(self):
        return list(set(
            [conf_var[1] for conf_var in [key.split('.') for key in self.configured_options.keys()]
                if conf_var[0] == 'remote']
        ))

    @property
    def remote_urls(self):
        return {remote: self.configured_options.get('remote.{}.url'.format(remote)) for remote in self.remotes}
