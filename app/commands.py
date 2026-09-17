import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models.user import User


def register_commands(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(set_role)


@click.command("create-admin")
@click.argument("username")
@click.argument("email")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
)
@with_appcontext
def create_admin(
    username,
    email,
    password,
):
    username = username.strip()
    email = email.strip().lower()

    existing_username = User.query.filter_by(
        username=username,
    ).first()

    if existing_username is not None:
        raise click.ClickException(
            "Пользователь с таким username уже существует."
        )

    existing_email = User.query.filter_by(
        email=email,
    ).first()

    if existing_email is not None:
        raise click.ClickException(
            "Пользователь с таким email уже существует."
        )

    if len(password) < 8:
        raise click.ClickException(
            "Пароль должен содержать минимум 8 символов."
        )

    user = User(
        username=username,
        email=email,
        role=User.ROLE_ADMIN,
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    click.echo(
        f"Администратор {username} создан."
    )


@click.command("set-role")
@click.argument("username")
@click.argument(
    "role",
    type=click.Choice(
        [
            User.ROLE_STUDENT,
            User.ROLE_TEACHER,
            User.ROLE_ADMIN,
        ],
        case_sensitive=False,
    ),
)
@with_appcontext
def set_role(
    username,
    role,
):
    user = User.query.filter_by(
        username=username,
    ).first()

    if user is None:
        raise click.ClickException(
            "Пользователь не найден."
        )

    user.role = role.lower()

    db.session.commit()

    click.echo(
        f"Пользователю {username} назначена роль {user.role}."
    )