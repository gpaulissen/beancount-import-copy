import os

import pytest

from .source_test import check_source_example

testdata_dir = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__), '..', '..', 'testdata', 'source', 'icscards'))

examples = [
    ('test_balance_wrong', 'icscards_balance_wrong.xlsx'),
    ('test_basic', 'icscards.xlsx'),
    ('test_big', 'icscards_big.xlsx'),
    ('test_invalid', 'icscards.xlsx'),
    ('test_training_examples', 'icscards.xlsx'),
    ('test_missing', 'icscards_missing.xlsx'),
]


@pytest.mark.parametrize('name,icscards_filename', examples)
def test_source(name: str, icscards_filename: str):
    check_source_example(
        example_dir=os.path.join(testdata_dir, name),
        source_spec={
            'module': 'beancount_import.source.icscards',
            'filenames': [os.path.join(testdata_dir, icscards_filename)],
        },
        replacements=[(testdata_dir, '<testdata>')])
