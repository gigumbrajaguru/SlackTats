from voluptuous import Required, Url, Range, All


USER_SCHEMA = {
    Required("login"): str,
    Required("id"): All(int, Range(min=1)),
    Required("avatar_url"): Url(),
    Required("gravatar_id"): str,
    Required("url"): Url(),
    Required("html_url"): Url(),
    Required("followers_url"): Url(),
    Required("following_url"): Url(),
    Required("gists_url"): Url(),
    Required("starred_url"): Url(),
    Required("subscriptions_url"): Url(),
    Required("organizations_url"): Url(),
    Required("repos_url"): Url(),
    Required("events_url"): Url(),
    Required("received_events_url"): Url(),
    Required("type"): str,
    Required("site_admin"): bool
}
