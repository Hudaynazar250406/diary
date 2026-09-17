from functools import wraps

from flask import abort, g, redirect, url_for


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(
                url_for("auth.login"),
            )

        return view(*args, **kwargs)

    return wrapped_view


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                return redirect(
                    url_for("auth.login"),
                )

            if g.user.role not in roles:
                abort(
                    403,
                    description="Недостаточно прав для выполнения операции",
                )

            return view(*args, **kwargs)

        return wrapped_view

    return decorator