from hypothesis_auto import auto_pytest_magic
from sio_asyncapi.asyncapi.utils import insert_prepath
from sio_asyncapi.asyncapi.utils import add_ref_prepath

auto_pytest_magic(insert_prepath)
auto_pytest_magic(add_ref_prepath)

def test_add_ref_prepath():
    # Test adding prepath to a single $ref field
    dict_obj = {'$ref': '#/definitions/Test'}
    add_ref_prepath(dict_obj, '/new')
    assert dict_obj == {'$ref': '#/new/definitions/Test'}

    # Test adding prepath to multiple $ref fields in a single dict
    dict_obj = {
        '$ref': '#/definitions/Test',
        'properties': {
            'field1': {'$ref': '#/definitions/Field1'},
            'field2': {'$ref': '#/definitions/Field2'}
        }
    }
    add_ref_prepath(dict_obj, '/new')
    assert dict_obj == {
        '$ref': '#/new/definitions/Test',
        'properties': {
            'field1': {'$ref': '#/new/definitions/Field1'},
            'field2': {'$ref': '#/new/definitions/Field2'}
        }
    }

    # Test adding prepath to a single $ref field in a list
    dict_obj = {'items': [{'$ref': '#/definitions/Test'}]}
    add_ref_prepath(dict_obj, '/new')
    assert dict_obj == {'items': [{'$ref': '#/new/definitions/Test'}]}

    # Test adding prepath to multiple $ref fields in a list of dicts
    dict_obj = {
        'items': [
            {'$ref': '#/definitions/Test1'},
            {'$ref': '#/definitions/Test2'},
            {'properties': {'field': {'$ref': '#/definitions/Field'}}}
        ]
    }
    add_ref_prepath(dict_obj, '/new')
    assert dict_obj == {
        'items': [
            {'$ref': '#/new/definitions/Test1'},
            {'$ref': '#/new/definitions/Test2'},
            {'properties': {'field': {'$ref': '#/new/definitions/Field'}}}
        ]
    }
