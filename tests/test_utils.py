from hypothesis_auto import auto_pytest_magic
from sio_asyncapi.asyncapi.utils import insert_prepath
from sio_asyncapi.asyncapi.utils import add_ref_prepath

auto_pytest_magic(insert_prepath)
auto_pytest_magic(add_ref_prepath)
