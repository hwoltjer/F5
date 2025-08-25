import click

from settings import Settings
import _commands as cert_commands

@click.group()
@click.pass_context
@click.option('-c', '--confirm-saved/--no-confirm', type=bool, default=False, 
              help='Use saved settings without confirming (Credentials, '\
                   'Full Name, etc)')
@click.option('-d', '--debug', is_flag=True, default=False)
def parasol(ctx, confirm_saved, debug):
    ctx.obj = Settings(app_name      = 'parasol',
                       log_debug     = debug,
                       confirm_saved = confirm_saved,
                       )

parasol.add_command(cert_commands.cert)

def main():
    parasol()


if __name__ == '__main__':
    main()