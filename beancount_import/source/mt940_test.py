import os

import pytest

from .source_test import check_source_example

testdata_dir = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__), '..', '..', 'testdata', 'source', 'mt940'))

examples = [
    ('test_basic', '0708271685_09022020_164516.940'),
]


@pytest.mark.parametrize('name,mt940_filename', examples)
def test_source(name: str, mt940_filename: str):
    check_source_example(
        example_dir=os.path.join(testdata_dir, name),
        source_spec={
            'module': 'beancount_import.source.mt940',
            'filenames': [os.path.join(testdata_dir, mt940_filename)],
            'mt940_bank': 'ASNB',
        },
        replacements=[(testdata_dir, '<testdata>')])

