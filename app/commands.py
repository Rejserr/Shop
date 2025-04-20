import click
from app.models.permission import Permission

@click.command('init-permissions')
def init_permissions():
    Permission.initialize_permissions()
    click.echo('Permissions initialized.')
