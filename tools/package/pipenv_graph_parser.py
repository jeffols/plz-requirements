import json
import subprocess

from typing import (
    List,
    Dict,
    NoReturn,
)


def normalize_package_name(package_name: str) -> str:
    return package_name.lower().replace('-', '_')


def normalize_requires(requires: str) -> List[str]:
    return sorted(
        [
            normalize_package_name(package.strip())
            for package in requires.strip().split(',') if package
        ],
        key=str.lower,
    )


def process():
    p = subprocess.run(
        ["pipenv", "graph", "--json"],
        stdout=subprocess.PIPE,
        check=True,
    )
    buffer = p.stdout.decode('utf-8')
    entries = json.loads(buffer)
    for entry in sorted(entries, key=lambda x: x['package']['package_name'].lower()):
        dependencies = sorted([
            normalize_package_name(dependency['package_name']) 
            for dependency in entry['dependencies']
            ])
        props = {
            'name': normalize_package_name(entry['package']['package_name']),
            'version': entry['package']['installed_version'],
            'requires': dependencies,
        }
        yield props

