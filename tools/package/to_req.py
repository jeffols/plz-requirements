import ast

import click


@click.command("to-req", help="Generate requirements.txt from BUILD")
@click.argument("BUILD_PATH", type=click.File("rb"))
@click.argument("REQUIREMENTS_PATH", type=click.File("wb"), default="-")
def cli(build_path, requirements_path):
    source = build_path.read()
    tree = ast.parse(source)

    expr = filter(lambda part: type(part) == ast.Expr, tree.body)
    pips = filter(lambda part: part.value.func.id in ['pip_library', 'python_wheel'], expr)

    for part in pips:
        helper = {keyword.arg: keyword.value for keyword in part.value.keywords}
        package_name = helper['package_name'].s if 'package_name' in helper else helper['name'].s
        repo = f"-f {helper['repo'].s}\n" if 'repo' in helper else ""
        requirements_path.write(f"{repo}{package_name}=={helper['version'].s}\n".encode('utf-8'))
