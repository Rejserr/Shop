from flask.cli import with_appcontext
import click
from app.utils.init_permissions import init_permissions
from flask import current_app

@click.command('init-permissions')
@with_appcontext
def init_permissions_command():
    with current_app.app_context():
        init_permissions()
        click.echo('Initialized permissions.')