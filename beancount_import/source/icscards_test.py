import os

import pytest

from .source_test import check_source_example

testdata_dir = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__), '..', '..', 'testdata', 'source', 'icscards'))

examples = [
    'test_basic',
#    'test_training_examples',
#    'test_invalid',    
]


@pytest.mark.parametrize('name', examples)
def test_source(name: str):
    breakpoint()
    check_source_example(
        example_dir=os.path.join(testdata_dir, name),
        source_spec={
            'module': 'beancount_import.source.icscards',
            'filename': os.path.join(testdata_dir, 'icscards.xlsx'),
        },
        replacements=[(testdata_dir, '<testdata>')])

