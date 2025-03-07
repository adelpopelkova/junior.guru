import json
from pathlib import Path

import pytest
from strictyaml import load


PROJECT_DIR = Path(__file__).parent.parent


def load_yaml(s, schema):
    """
    Uses json.loads/json.dumps to recursively convert all ordered dicts
    to dicts, which significantly improves readability of the pytest diff
    """
    return json.loads(json.dumps(load(s, schema).data))


def startswith_skip(path):
    """
    Tests whether the given path's basename starts with the word SKIP
    """
    return Path(path).name.lower().startswith('skip')


def param_startswith_skip(path, values=2):
    """
    Creates a @pytes.mark.parametrize() param, which is marked as skipped
    because the path startswith the word SKIP

    The 'values' parameter specifies how many value arguments the marker
    needs to fake so that pytest doesn't complain that the param doesn't fit
    the declared number of values. It's usually 2 (input and expected output),
    so 2 is the default.

    The skip reason can be displayed by running 'pytest -r s'
    """
    args = ['' for i in range(values)]
    path_relative = path.relative_to(PROJECT_DIR)
    marks = pytest.mark.skip(f'starts with SKIP: {path_relative}')
    return pytest.param(*args, id=Path(path).name, marks=marks)


def param_xfail_missing(path, values=2):
    """
    Creates a @pytes.mark.parametrize() param, which is marked as failed
    because of a fixture path missing

    The 'values' parameter specifies how many value arguments the marker
    needs to fake so that pytest doesn't complain that the param doesn't fit
    the declared number of values. It's usually 2 (input and expected output),
    so 2 is the default.

    The skip reason can be displayed by running 'pytest -r x'
    """
    args = ['' for i in range(values)]
    path_relative = path.relative_to(PROJECT_DIR)
    marks = pytest.mark.xfail(f'missing: {path_relative}')
    return pytest.param(*args, id=Path(path).name, marks=marks)
