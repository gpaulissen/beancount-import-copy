import os

import pytest

from .source_test import check_source_example

testdata_dir = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__), '..', '..', 'testdata', 'source', 'icscards'))

examples = [
    'test_basic'
]


@pytest.mark.parametrize('name', examples)
def test_source(name: str):
    check_source_example(
        example_dir=os.path.join(testdata_dir, name),
        source_spec={
            'module': 'beancount_import.source.icscards',
            'filename': os.path.join(testdata_dir, 'Rekeningoverzicht-54280230027-2020-01.csv'),
        },
        replacements=[(testdata_dir, '<testdata>')])
#    f_in = csv.reader(open(os.path.join(testdata_dir, icscards_filename)), quotechar='"', newline='')
#    for line in f_in:
#        print(line)
    assert False
