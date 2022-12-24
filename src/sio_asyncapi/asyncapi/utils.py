from typing import Dict


def insert_prepath(prepath: str, path) -> str:
    """
    Takes a path and inserts a prepath after the first #.
    """
    return path.replace('#', "#" + prepath, 1)


def add_ref_prepath(dict_obj: Dict[str, str], prepath: str):
    """
    Takes a dict with nested lists and dicts,
    and adds a prepath to all $ref fields.
    """
    for key, value in dict_obj.items():

        if key == '$ref':
            path = dict_obj[key]
            dict_obj[key] = insert_prepath(prepath, path)

        elif isinstance(value, dict):
            add_ref_prepath(value, prepath)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    add_ref_prepath(item, prepath)

