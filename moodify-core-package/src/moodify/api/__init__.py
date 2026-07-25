"""REST API package with lazy application loading."""


def __getattr__(name: str):
    if name == "app":
        from moodify.api.main import app

        return app
    raise AttributeError(name)


__all__ = ["app"]
