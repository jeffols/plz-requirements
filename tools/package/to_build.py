import io
import subprocess
from typing import (
    List,
    Dict,
    NoReturn,
)

import click
import jinja2

from tools.package.build_util import (
    BuildPipLibrary,
    BuildSpec,
)
from tools.package import pipenv_graph_parser
from tools.package import pip_show_parser

jinja2_env = jinja2.Environment(trim_blocks=True)


class Package:
    """
    Output BUILD pip_library given some package properties
    """
    NAME_VERSION = jinja2_env.from_string(
            'pip_library(\n'
            '    name = "{{name}}",\n'
            '    version = "{{version}}",\n\n'
        )
    DEPS = jinja2_env.from_string(
            '    deps = [\n'
            '{% for dep in deps %}        ":{{dep.lower()}}",\n{% endfor %}\n'
            '    ],\n\n'
        )
    NO_LICENSE = '    licences = ["UNKNOWN"],\n'
    TAIL = ')\n\n'

    def __init__(self, name=None, version=None, requires=None, license=None, **kwargs):
        self.name = name
        self.version = version
        self.requires = requires
        self.unknown_licence = license == "UNKNOWN"
        self.other = kwargs

    def output(self) -> str:
        output = self.NAME_VERSION.render(name=self.name, version=self.version)
        if self.requires:
            output += self.DEPS.render(deps=self.requires)
        if self.unknown_licence:
            output += self.NO_LICENSE
        output += self.TAIL
        return output


class Requirements:
    def __init__(self):
        self.packages = {}

    def process(self) -> NoReturn:
        for props in pipenv_graph_parser.process():
            package = Package(**props)
            self.packages[package.name] = package

    def output(self) -> str:
        with io.StringIO() as f:
            for r in sorted(self.packages, key=str.lower):
                f.write(self.package[r].output())
            f.seek(0)
            return f.read()


@click.command("to-build")
@click.argument('MASTER_BUILD_FILE', type=click.File("rt"))
@click.argument('BUILD_FILE', type=click.File("wt"), default='-')
def cli(master_build_file, build_file):
    reqs = Requirements()
    reqs.process()

    master_spec = BuildSpec().populate_from_source(master_build_file)

    spec = BuildSpec()
    for name, package in reqs.packages.items():
        spec.add_pip_able(BuildPipLibrary.from_source(package.output()))

    for pip_able in spec._pips:
        if pip_able in master_spec._pips:
            master_pkg = master_spec._pips[pip_able]
            new_pkg = spec._pips[pip_able]
            if master_pkg.version != new_pkg.version:
                print(f"Version Change {new_pkg.name} {master_pkg.version} => {new_pkg.version}")
        else:
            new_pkg = spec._pips[pip_able]
            print(f"New: {new_pkg.name} {new_pkg.version}")

    build_file.write(spec.output())


if __name__ == "__main__":
    cli()
