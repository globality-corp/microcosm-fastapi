from pathlib import Path

from pkg_resources import resource_filename


def get_template(template_name: str) -> str:
    path = Path(resource_filename(__name__, template_name))

    with open(path) as file:
        return file.read()
