"""MT940 transaction source.

This imports transactions from MT940 files using the mt940 module, seee
https://github.com/WoLpH/mt940.

Data format
===========

To use, first download MT940 transactions and balance information to the
filesystem from your bank. In the examples I use the dutch ASN Bank where the
downloaded files end with suffix .940.

You might have a directory structure like:

    financial/
      data/
        ASNB/
          <file>.940

The MT940 files includes transaction and balance information.

This is an example:

  {1:F01ASNBNL21XXXX0000000000}{2:O940ASNBNL21XXXXN}{3:}{4:
  :20:0000000000
  :25:NL81ASNB9999999999
  :28C:1/1
  :60F:C200101EUR444,29
  :61:2001010101D65,00NOVBNL47INGB9999999999
  hr gjlm paulissen
  :86:NL47INGB9999999999 hr gjlm paulissen
                                                                   
  Betaling sieraden                                                
                                                                   
                                                                   
                                                                   
  :62F:C200101EUR379,29
  -}{5:}
  {1:F01ASNBNL21XXXX0000000000}{2:O940ASNBNL21XXXXN}{3:}{4:
  :20:0000000000
  :25:NL81ASNB9999999999
  :28C:2/1
  :60F:C200102EUR379,29
  :62F:C200102EUR379,29
  -}{5:}
  {1:F01ASNBNL21XXXX0000000000}{2:O940ASNBNL21XXXXN}{3:}{4:
  :20:0000000000
  :25:NL81ASNB9999999999
  :28C:30/1
  :60F:C200130EUR404,81
  :62F:C200130EUR404,81
  -}{5:}
  {1:F01ASNBNL21XXXX0000000000}{2:O940ASNBNL21XXXXN}{3:}{4:
  :20:0000000000
  :25:NL81ASNB9999999999
  :28C:31/1
  :60F:C200131EUR404,81
  :61:2001310131C1000,18NIOBNL56ASNB9999999999
  paulissen g j l m
  :86:NL56ASNB9999999999 paulissen g j l m
                                                                   
  INTERNE OVERBOEKING VIA MOBIEL                                   
                                                                   
                                                                   
                                                                   
  :61:2001310131D903,76NIDBNL08ABNA9999999999
  international card services 
  :86:NL08ABNA9999999999 international card services 
                                                                   
  000000000000000000000000000000000 0000000000000000 Betaling aan I
  CS 99999999999 ICS Referentie: 2020-01-31 21:27 000000000000000  
                                                                   
                                                                   
  :62F:C200131EUR501,23
  -}{5:}


See also https://www.sepaforcorporates.com/swift-for-corporates for the MT940 format.

Specifying the source to beancount_import
=========================================

Within your Python script for invoking beancount_import, you might use an
expression like the following to specify the MT940 source:

    dict(module='beancount_import.source.mt940',
         filenames=[os.path.join(journal_dir, 'data', 'mt940', '<file>.940')],
         mt940_bank=ASNB
    )

where `journal_dir` refers to the financial/ directory. The mt940_bank is
optional and allows for a special MT940 configuration.

Associating MT940 accounts with Beancount accounts
=================================================

This data source only imports transactions from accounts known to MT940 with
which a Beancount account has been explicitly associated using the `mt940_id`
metadata field of the account open directive.  The `mt940_id` corresponds to the
tag 25 (NL81ASNB9999999999 in the example). For example:

    1900-01-01 open Assets:Checking  EUR
      mt940_id: "NL81ASNB9999999999"

Imported transaction format:
============================

Each transaction (tag 61) in the transactions file corresponds to a single imported
transaction.

Transaction identification
--------------------------

The `date` and `source_desc` metadata fields (along with the account, payee and
amount) associate postings in the journal with corresponding rows in the
transactions file.  These fields correspond to the "date" and "transaction_details"
fields in the transactions file, respectively.  It is possible for multiple
real transactions to have an identical combination of account, amount, "date",
and "transaction_details" (corresponding to multiple identical rows in the
transactions file), but that is handled appropriately: this data source will
simply generate a separate transaction for each such row.

"""

from typing import List, Union, Optional, Set
import mt940
from mt940.tags import StatementASNB
import datetime
import collections
import re
import os

from beancount.core.data import Transaction, Posting, Balance, EMPTY_SET
from beancount.core.amount import Amount
from beancount.core.flags import FLAG_OKAY
from beancount.core.number import MISSING, D, ZERO

from . import description_based_source
from . import ImportResult, SourceResults
from ..matching import FIXME_ACCOUNT
from ..journal_editor import JournalEditor

# account may be either the mt940_id or the journal account name
MT940Entry = collections.namedtuple(
    'MT940Entry',
    ['account', 'date', 'amount', 'payee', 'source_desc', 'filename', 'line'])
RawBalance = collections.namedtuple(
    'RawBalance', ['account', 'date', 'amount', 'filename', 'line'])


def get_info(raw_entry: Union[MT940Entry, RawBalance]) -> dict:
    return dict(
        type='text/plain',
        filename=raw_entry.filename,
        line=raw_entry.line,
    )


def load_transactions(filename: str, mt940_bank: str, currency: str = 'EUR') -> [List[MT940Entry], List[RawBalance]]:
    """
    (Pdb) pp trs.data
{'account_identification': 'NL81ASNB9999999999',
 'final_closing_balance': <<501.23 EUR> @ 2020-01-31>,
 'final_opening_balance': <<404.81 EUR> @ 2020-01-31>,
 'sequence_number': '1',
 'statement_number': '31',
 'transaction_reference': '0000000000'}

    (Pdb) pp str(trs.transactions[0].data)
("{'status': 'D', 'funds_code': None, 'amount': <-65.00 EUR>, 'id': 'NOVB', "
 "'customer_reference': 'NL47INGB9999999999', 'bank_reference': None, "
 "'extra_details': 'hr gjlm paulissen', 'currency': 'EUR', 'date': Date(2020, "
 "1, 1), 'entry_date': Date(2020, 1, 1), 'guessed_entry_date': Date(2020, 1, "
 "1), 'transaction_details': 'NL47INGB9999999999 hr gjlm paulissen\\nBetaling "
 "sieraden'}")
    """

    try:
        entries = []
        balances = []
        filename = os.path.abspath(filename)
        tag_parser = None
        if mt940_bank == 'ASNB':
            tag_parser = StatementASNB()
        else:
            tag_parser = Statement()
            
        trs = mt940.models.Transactions(tags={
            tag_parser.id: tag_parser
        })
        
        with open(filename) as fh:
            data = fh.read()
            trs.parse(data)
            account = trs.data['account_identification']
            number = D(str(trs.data['final_closing_balance'].amount.amount)) # Use str() to prevent rounding errors
            currency = trs.data['final_closing_balance'].amount.currency
            balances.append(
                RawBalance(
                    account=account,
                    date=trs.data['final_closing_balance'].date,
                    amount=Amount(number=number, currency=currency),
                    filename=filename,
                    line=0))
            for line_i, transaction in enumerate(trs, start=1):
                number = D(str(transaction.data['amount'].amount)) # Use str() to prevent rounding errors
                if number == ZERO:
                    # Skip zero-dollar transactions.
                    # Some banks produce these, e.g. for an annual fee that is waived.
                    continue
                currency = transaction.data['amount'].currency
                payee = "{1} ({0})".format(transaction.data['customer_reference'], transaction.data['extra_details'])
                source_desc = transaction.data['transaction_details']
                source_desc = source_desc.replace(transaction.data['customer_reference'], '')
                source_desc = source_desc.replace(transaction.data['extra_details'], '')
                source_desc = source_desc.replace("\n", '').strip()
                source_desc = source_desc if source_desc != '' else 'UNKNOWN'
                entries.append(
                    MT940Entry(
                        account=account,
                        date=transaction.data['date'],
                        payee=payee,
                        source_desc=source_desc,
                        amount=Amount(number=number, currency=currency),
                        filename=filename,
                        line=line_i))
        return entries, balances

    except Exception as e:
        raise RuntimeError('MT940 file has incorrect format', filename) from e


def _get_key_from_posting(entry: Transaction, posting: Posting,
                          source_postings: List[Posting], source_desc: str,
                          posting_date: datetime.date):
    del entry
    del source_postings
    return (posting.account, posting_date, posting.units, source_desc)


def _get_key_from_entry(x: MT940Entry):
    return (x.account, x.date, x.amount, x.source_desc)


def _make_import_result(mt940_entry: MT940Entry) -> ImportResult:
    transaction = Transaction(
        meta=None,
        date=mt940_entry.date,
        flag=FLAG_OKAY,
        payee=mt940_entry.payee,
        narration=mt940_entry.source_desc,
        tags=EMPTY_SET,
        links=EMPTY_SET,
        postings=[
            Posting(
                account=mt940_entry.account,
                units=mt940_entry.amount,
                cost=None,
                price=None,
                flag=None,
                meta=collections.OrderedDict(
                    source_desc=mt940_entry.source_desc,
                    date=mt940_entry.date,
                )),
            Posting(
                account=FIXME_ACCOUNT,
                units=-mt940_entry.amount,
                cost=None,
                price=None,
                flag=None,
                meta=None,
            ),
        ])
    return ImportResult(
        date=mt940_entry.date, info=get_info(mt940_entry), entries=[transaction])


class MT940Source(description_based_source.DescriptionBasedSource):
    def __init__(self,
                 filenames: List[str],
                 mt940_bank: Optional[str] = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)

        # In these entries, account refers to the mt940_id, not the journal account.
        self.mt940_entries = []
        self.balances = []
        for filename in filenames:
            self.log_status('mt940: loading %s' % filename)
            mt940_entries, balances = load_transactions(filename, mt940_bank)
            self.mt940_entries.extend(mt940_entries)
            self.balances.extend(balances)

    def prepare(self, journal: JournalEditor, results: SourceResults) -> None:
        account_to_mt940_id, mt940_id_to_account = description_based_source.get_account_mapping(
            journal.accounts, 'mt940_id')
        missing_accounts = set()  # type: Set[str]

        def get_converted_mt940_entries(entries):
            for raw_mt940_entry in entries:
                account = mt940_id_to_account.get(raw_mt940_entry.account)
                if not account:
                    missing_accounts.add(raw_mt940_entry.account)
                    continue
                match_entry = raw_mt940_entry._replace(account=account)
                yield match_entry

        description_based_source.get_pending_and_invalid_entries(
            raw_entries=get_converted_mt940_entries(self.mt940_entries),
            journal_entries=journal.all_entries,
            account_set=account_to_mt940_id.keys(),
            get_key_from_posting=_get_key_from_posting,
            get_key_from_raw_entry=_get_key_from_entry,
            make_import_result=_make_import_result,
            results=results)

        for mt940_account in missing_accounts:
            results.add_warning(
                'No Beancount account associated with MT940 account %r.' %
                (mt940_account, ))

        for raw_balance in get_converted_mt940_entries(self.balances):
            date = raw_balance.date + datetime.timedelta(days=1)
            results.add_pending_entry(
                ImportResult(
                    date=date,
                    info=get_info(raw_balance),
                    entries=[
                        Balance(
                            account=raw_balance.account,
                            date=date,
                            meta=None,
                            amount=raw_balance.amount,
                            tolerance=None,
                            diff_amount=None)
                    ]))

    @property
    def name(self):
        return 'mt940'


def load(spec, log_status):
    return MT940Source(log_status=log_status, **spec)
