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


def extract_props(section: str) -> Dict[str, str]:
    def split_prop(line: str) -> Dict[str, str]:
        pos = line.find(':')
        return line[:pos].lower(), line[pos:].lstrip(':').strip()

    return dict(split_prop(line) for line in section.split("\n") if line.strip())


def process(packages: List[str]) -> Dict:
    packages = list(map(normalize_package_name, packages))
    p = subprocess.run(
        ["python", "-m", "pip", "show"] + packages,
        stdout=subprocess.PIPE,
        check=True,
    )
    buffer = p.stdout.decode('utf-8')
    sections = buffer.split('---\n')
    seen = set()
    for section in sections:
        props = extract_props(section)
        props["name"] = normalize_package_name(props["name"])
        props["requires"] = normalize_requires(props["requires"])
        seen.add(props["name"])
        yield props
    if set(packages).difference(seen):
        print("Packages missing from envionment.  Did you forget to activate a virtual environment?")
        print(sorted(set(packages).difference(seen)))
        exit(1)
