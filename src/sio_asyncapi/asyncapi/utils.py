# def get_asycnapi_spec(
#     *,
#     title: str,
#     version: str,
#     openapi_version: str = "3.0.2",
#     description: Optional[str] = None,
#     routes: Sequence[BaseRoute],
#     tags: Optional[List[Dict[str, Any]]] = None,
#     servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
#     terms_of_service: Optional[str] = None,
#     contact: Optional[Dict[str, Union[str, Any]]] = None,
#     license_info: Optional[Dict[str, Union[str, Any]]] = None,
# ) -> Dict[str, Any]:
#     """Returns the AsyncAPI document as a string."""
#     global asyncapi_doc
#     return yaml.dump(asyncapi_doc, sort_keys=False)

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

