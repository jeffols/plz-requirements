import click

import tools.package.to_req
import tools.package.to_build

@click.group()
@click.version_option()
def commands():
    pass


commands.add_command(tools.package.to_req.cli)
commands.add_command(tools.package.to_build.cli)


if __name__ == "__main__":
    commands()
