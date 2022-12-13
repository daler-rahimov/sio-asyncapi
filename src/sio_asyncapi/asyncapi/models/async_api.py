import os
import yaml
from .async_api_base import AsyncAPIBase


class AsyncAPI(AsyncAPIBase):

    def load_from_file(filename):
        unresolved_data = AsyncAPI.load_data_from_file(filename)
        data = AsyncAPI.resolve_external_references(unresolved_data, os.path.dirname(filename))
        return AsyncAPI.parse_obj(data)

    @staticmethod
    def load_data_from_file(filename):
        # Currently only load data from YAML files
        with open(filename) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data

    @staticmethod
    def resolve_external_references(data, files_folder):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == '$ref' and not value.startswith("#/components") and value.endswith(".yaml"):
                    data = AsyncAPI.resolve_external_references(AsyncAPI.load_data_from_file(os.path.join(files_folder, value)), files_folder)
                else:
                    data[key] = AsyncAPI.resolve_external_references(value, files_folder)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                data[index] = AsyncAPI.resolve_external_references(value, files_folder)
        return data
