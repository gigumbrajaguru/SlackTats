from voluptuous import Schema, Url


LABEL_SCHEMA = Schema({
    "id": int,
    "url": Url(),
    "name": str,
    "color": str,
    "default": bool
})
