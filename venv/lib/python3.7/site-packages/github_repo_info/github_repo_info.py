import re

from git_repo_info.git_repo_info import GitRepo

# The regex used in these functions is easiest studied here - https://www.debuggex.com/r/B2hlqrSnNZJrTdoD
REPO_URL_REGEX = re.compile(
    r'''(?:git@|https://)(?:\w+@)?  # Match URL variations up to the hostname.
        (?P<hostname>\w+\.\w+)      # Match the git host's hostname.
        (?:/|:)                     # Match the different possible separators.
        (?P<username>[\w,\-,\_]+)      # Match the git repositories owner
        /                           # Match the separator.
        (?P<repo>[\w,\-,\_]+)       # Match the repo name
        (?:.git)?(?:/)?             # Match the URL variations after the repo name.''',
    re.VERBOSE
)


class GitHubRepo(GitRepo):
    def __init__(self, path=None):
        super(GitHubRepo, self).__init__(path=path)

    @property
    def is_github_repository(self, remote=None):
        if remote is None:
            if len(self.remotes) == 1:
                remote = self.remotes[0]
            if len(self.remotes) > 1:
                ValueError('''Multiple Git remotes found, please specify which Git remote to use.''')
        if remote is not None:
            return 'github.com' in REPO_URL_REGEX.match(self.remote_urls.get(remote)).group('hostname')
        else:
            return False

    @property
    def github_username(self, remote=None):
        if remote is None:
            if len(self.remotes) == 1:
                remote = self.remotes[0]
            if len(self.remotes) > 1:
                ValueError('''Multiple Git remotes found, please specify which Git remote to use.''')
        return REPO_URL_REGEX.match(self.remote_urls.get(remote)).group('username')

    @property
    def github_repo_name(self, remote=None):
        if remote is None:
            if len(self.remotes) == 1:
                remote = self.remotes[0]
            if len(self.remotes) > 1:
                ValueError('''Multiple Git remotes found, please specify which Git remote to use.''')
        return REPO_URL_REGEX.match(self.remote_urls[remote]).group('repo')
