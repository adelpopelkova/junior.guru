from datetime import date, datetime, time

import pytest

import juniorguru.models.base as models_base
from juniorguru.scrapers.items import Job


@pytest.mark.parametrize('o,expected', [
    ([1, 2, 3], '[1, 2, 3]'),
    (datetime(2020, 4, 30, 14, 35, 10), '"2020-04-30T14:35:10"'),
    (date(2020, 4, 30), '"2020-04-30"'),
    (time(14, 35, 10), '"14:35:10"'),
    ([1, 2, datetime(2020, 4, 30, 14, 35, 10)], '[1, 2, "2020-04-30T14:35:10"]'),
    ({'posted_at': datetime(2020, 4, 30, 14, 35, 10)}, '{"posted_at": "2020-04-30T14:35:10"}'),
])
def test_json_dumps(o, expected):
    assert models_base.json_dumps(o) == expected


def test_json_dumps_item():
    job = Job(posted_at=datetime(2020, 4, 30, 14, 35, 10),
              title='Junior developer')

    assert models_base.json_dumps(job) == '''
        {"posted_at": "2020-04-30T14:35:10", "title": "Junior developer"}
    '''.strip()
