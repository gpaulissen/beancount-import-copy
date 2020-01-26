# -*-coding: utf-8-*-

"""ICScards.nl transaction and balance source.

Data format
===========

To use, first download transaction (and balance) data into a directory on the
filesystem.  The easiest way to download data from ICScards in the requisite format
is to use the finance_dl.icscards module. 

The transactions files are in PDF format and although it is possible to use
Python to create a CSV file from it (for example using the pdftotext script as
in other beanimport modules), the result is not at all good enough to use
it. I therefore suggest that you install 'WPS PDF to Word' (also converts to
Excel XLSX) from https://wps.com and later use Python module xlsx2cxv
(http://github.com/dilshod/xlsx2csv) to convert that to CSV.

So the suggested workflow is:
1) Download the transaction statements from https://icscards.nl either
manually or automatically.
2) Use 'WPS PDF to Word' to create XLSX files.
3) Place those XLSX files in the data directory structure (see below).
4) Then this beancount_import module will take care of the rest.

You might have a directory structure like:

    financial/
      data/
        icscards/
          account_id/
            Rekeningoverzicht-54280230027-2020-01.xlsx


The `Rekeningoverzicht-54280230027-2020-01.xlsx` file should be a XLSX file
containing all downloaded transactions, in the normal PDF download format
provided by ICScards.  See the `testdata/source/icscards` directory for an
example.

The `Rekeningoverzicht-54280230027-2020-01.csv` file should be of the form:

Line Text

1    "International Card Services BV Postbus 23225
     1100 DS Diemen
     Telefoon 020 - 6 600 600
     Kvk Amsterdam nr. 33.200.596",,,,,"www.icscards.nl
     Bankrek. NL99ABNA9999999999 BIC: ABNANL2A
     ICS identificatienummer bij incasso: NL99ZZZ999999999999",,,,,,,
2    Datum                                          ICS-klantnummer                         Volgnummer                                Bladnummer,,,,,,,,,,,,
3    17 januari 2020                           99999999999                               1                                                   1  van 1,,,,,,,,,,,,
4    "Vorig openstaand saldo               Totaal ontvangen betalingen       Totaal nieuwe uitgaven                Nieuw openstaand saldo
     € 1.801,55                          Af      € 1.827,97                          Bij      € 1.930,18                           Af     € 1.903,76                          Af",,,,,,,,,,,,
5    "Datum
     transactie",,"Datum
     boeking",,"Omschrijving                                                                                           Bedrag in
     vreemde valuta",,,,,,"Bedrag
     in euro's",,
6    24 dec,24 dec,,"IDEAL BETALING, DANK U",,,,,1000,,,Bij,
7    05 jan,05 jan,,"IDEAL BETALING, DANK U",,,,,801.55,,,Bij,
8    "Uw Card met als laatste vier cijfers 0467
     G.J.L.M. PAULISSEN",,,,,,,,,,,,
9    16 dec,18 dec,,SARL THONIC,,,ZZZZ,FR,,,65.00,Af,
10   16 dec,18 dec,,SODEXO,,,ZZZZZZZZZZZZZ,FR,,,10.00,Af,
11   18 dec,19 dec,,OW125692REDHIP12,,,ZZZZZZZZZZZZZ,FR,,,32.00,Af,
12   18 dec,19 dec,,SODEXO,,,ZZZZZZZZZZZZZ,FR,,,10.00,Af,
13   18 dec,19 dec,,HOTEL MERCURE,,,ZZZZZZZZZZZZZ,FR,,,422.05,Af,
14   18 dec,20 dec,,G7,,,ZZZZZZ,FR,,,50.00,Af,
15   20 dec,21 dec,,NETFLIX.COM,,,999-999-9999,NL,,,7.99,Af,
16   23 dec,24 dec,,SPA,,,ZZZZZZ,BE,,,76.20,Af,
17   25 dec,27 dec,,RESTAURANT,,,ZZZZZ,NL,,,475.00,Af,
18   26 dec,27 dec,,FLETCHER HOTEL,,,ZZZZZZZZZZ,NL,,,154.45,Af,
19   02 jan,03 jan,,QUICKEN INC,,,9999999999,US,,29.990000000,27.41,Af,
20   ,,,Wisselkoers USD,,,1.09413,,,,,,
21   08 jan,09 jan,,SODEXO,,,ZZZZZZZZZZZZZ,FR,,,10.00,Af,
22   08 jan,09 jan,,HOTEL MERCURE,,,ZZZZZZZZZZZZZ,FR,,,359.34,Af,
23   08 jan,09 jan,,UBER TRIP HELP.UBER.COM,,,ZZZZZZZZZZZZZ,FR,,,49.59,Af,
24   08 jan,09 jan,,SNCF,,,ZZZZZZZZZZ,FR,,,6.15,Af,
25   10 jan,10 jan,,QUICKEN INC,,,9999999999,US,,29.990000000,26.42,Bij,
26   ,,,Wisselkoers USD,,,1.13512,,,,,,
27   13 jan,14 jan,,SNCF OUIGO,,,ZZZZZZZ,FR,,,45.00,Af,
28   14 jan,15 jan,,SNCF WEB MOBILE,,,ZZZZZZZZ,FR,,,130.00,Af,
29   "Uw betalingen aan International Card Services BV zijn bijgewerkt tot 17 januari 2020.
     Het minimaal te betalen bedrag ad € 1.903,76 verwachten wij voor 7 februari 2020 op rekening NL99 ABNA 9999 9999 99 t.n.v. ICS in Diemen. Vermeld bij uw betaling altijd uw ICS-klantnummer 99999999999.",,,,,,,,,,,,
30   Bestedingslimiet                                                Minimaal te betalen bedrag,,,,,,,,,,,,
31   "€ 2.500                                                               € 1.903,76",,,,,,,,,,,,
32   Dit product valt onder het depositogarantiestelsel. Meer informatie vindt u op www.icscards.nl/depositogarantiestelsel en op het informatieblad dat u jaarlijks ontvangt.,,,,,,,,,,,,

The associated bank account is specified in row 1, column 2 after 'Bankrek.' and before 'BIC'.

Rows 2 and 3 are repeated every page and show the page number.

The balances are in the fourth row in the first column surrounded by double quotes.

The payments to your ICScards card are in rows 6 and 7.

The payments from your ICScards are in row 9 till 28 where rows 20 and 26
are just information about currency conversions.

Specifying the source to beancount_import
=========================================

Within your Python script for invoking beancount_import, you might use an
expression like the following to specify the icscards source:

    dict(module='beancount_import.source.icscards',
         directory=os.path.join(journal_dir, 'data', 'icscards', 'account_id'),
         assets_account='Assets:Icscards',
    )

where `journal_dir` refers to the financial/ directory.

Imported transaction format
===========================

If you receive a payment, or make a payment from your Icscards balance, a single
transaction of the following form is generated:

    2017-09-06 * "Sally Smith" "Rent"
      Assets:Icscards     1150.00 USD
        date: 2017-09-06
        icscards_description: "Rent"
        icscards_payer: "Sally Smith"
        icscards_payment_id: "0454063333607815882"
        icscards_type: "Payment"
      Expenses:FIXME  -1150.00 USD

If you transfer funds from your Venmo balance to a bank account, a single
transaction is generated:

    2017-09-06 * "Venmo" "Transfer"
      Assets:Venmo    -1150.00 USD
        date: 2017-09-06
        venmo_account_description: "My Bank *8967"
        venmo_transfer_id: "355418184"
        venmo_type: "Standard Transfer"
      Expenses:FIXME   1150.00 USD

The `venmo_payment_id` and `venmo_transfer_id` metadata fields are used to
associate transactions in the Beancount journal with rows in the
`transactions.csv` file.

For transfer transactions (transactions with a `venmo_transfer_id` metadata
field), the `venmo_type` and `venmo_account_description` metadata fields provide
features for predicting the unknown account.

For payment transactions (transactions with a `venmo_payment_id` metadata
field), the `venmo_type`, `venmo_description`, and `venmo_payee`/`venmo_payer`
metadata fields provide features for predicting the unknown account.
"""

from typing import List, Union, Optional, Set
import csv
import datetime
import collections
import re
import os
import locale

from beancount.core.data import Transaction, Posting, Balance, EMPTY_SET
from beancount.core.amount import Amount
from beancount.core.flags import FLAG_OKAY
from beancount.core.number import MISSING, D, ZERO

from . import description_based_source
from . import ImportResult, SourceResults
from ..matching import FIXME_ACCOUNT
from ..journal_editor import JournalEditor

DEBUG = True

def convert_str_to_list(str, max_items, sep=r'\s\s+'):
    return [x for x in re.split(sep, str)[0:max_items]]

def convert_str_to_id_list(str, max_items, sep=r'\s\s+'):
    return [x.replace(' ', '_') for x in re.split(sep, str)[0:max_items]]

# account may be either the icscards_id or the journal account name
ICScardsEntry = collections.namedtuple(
    'ICScardsEntry',
    ['account', 'date', 'amount', 'source_desc', 'filename', 'line'])
RawBalance = collections.namedtuple(
    'RawBalance', convert_str_to_id_list("Vorig openstaand saldo               Totaal ontvangen betalingen       Totaal nieuwe uitgaven                Nieuw openstaand saldo", 4))

def get_info(raw_entry: Union[ICScardsEntry, RawBalance]) -> dict:
    return dict(
        type='text/csv',
        filename=raw_entry.filename,
        line=raw_entry.line,
    )

def load_transactions(filename: str, currency: str = 'USD') -> List[ICScardsEntry]:
    def add_years(d, years):
        """Return a date that's `years` years after the date (or datetime)
        object `d`. Return the same calendar date (month and day) in the
        destination year, if it exists, otherwise use the following day
        (thus changing February 29 to March 1).

        """
        try:
            return d.replace(year = d.year + years)
        except ValueError:
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

    def get_date(s: str):
        d = datetime.datetime.strptime(s, '%d %b')
        # Without a year it will be 1900 so augment
        while d <= page_date:
            d = add_years(d, 1)
        return add_years(d, -1)

    # As from the CSV
    expected_field_names = [
        "Datum transactie",
        "Datum boeking",
        "Omschrijving Bedrag in vreemde valuta", # actually two fields but hey any PDF converter can have errors in it
        "Bedrag in euro's"
    ]
    # Actual fields
    actual_field_names = [
        "Datum transactie",
        "Datum boeking",
        "Omschrijving",
        "Plaats", # Optional together with the next
        "Land", # Optional together with the previous
        "Bedrag in vreemde valuta", # Optional
        "Bedrag in euro's",
        "Bij/Af"
    ]
    NewPageCell = 'Datum                                          ICS-klantnummer                         Volgnummer                                Bladnummer'
    page_date = None

    locale.setlocale(category=locale.LC_ALL, locale="Dutch") # Need to parse "05 mei" i.e. "05 may"

    try:
        entries = []
        account = None
        new_page = False
        filename = os.path.abspath(filename)
        with open(filename, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile, quotechar='"') 
            for line_i, row in enumerate(reader, start=1):
                # Handle new pages
                if new_page:
                    new_page = False
                    if page_date == None:
                        page_date = datetime.datetime.strptime(convert_str_to_list(row[0], 1)[0], '%d %B %Y')
                elif row[0] == NewPageCell:
                    new_page = True
                else:
                    # Only keep the non null items
                    row = [x for x in row if x != '']

                    if DEBUG:
                        print("[%s] %s\n" % (line_i, row))

                    if line_i == 1:
                        account = re.search('Bankrek. (.+) BIC:', row[1]).group(1)
                    elif line_i == 5:
                        field_names = [re.sub(r'\s+', ' ', x).strip() for x in row]
                        if field_names != expected_field_names:
                            raise RuntimeError(
                                'Actual field names %r != expected field names %r' %
                                (field_names, expected_field_names))
                    elif not(len(row) >= 5 and len(row) <= 8):
                        continue
                    else:
                        # Use transaction date, skip booking date
                        try:
                            date = get_date(row[0])
                        except Exception as e:
                            raise RuntimeError('Invalid date: %r' % row[0]) from e

                        # Description
                        source_desc = row[2]

                        # Add place and country
                        if len(row) >= 7:
                            source_desc += ", %s (%s)" % (row[3], row[4])

                        # Skip amount in foreign currency
                        number = D(row[-2])
                        if number == ZERO:
                            # Skip zero-dollar transactions.
                            # Some banks produce these, e.g. for an annual fee that is waived.
                            continue
                        
                        transaction_type = row[-1]
                        if transaction_type == 'Af':
                            number = -number
                        elif transaction_type != 'Bij':
                            raise RuntimeError('Unknown transaction type: %r in row %r'
                                               % (transaction_type, row))

                        entry = ICScardsEntry(account=account,
                                              date=date,
                                              source_desc=source_desc,
                                              amount=Amount(number=number, currency='EUR'),
                                              filename=filename,
                                              line=line_i)
                        if DEBUG:
                            print(entry)
                        entries.append(entry)
                        
        entries.reverse()
        entries.sort(key=lambda x: x.line)  # sort by date first, line next
        if DEBUG:
            print(entries)
        return entries

    except Exception as e:
        raise RuntimeError('CSV file has incorrect format', filename) from e


def load_balances(filename: str) -> List[RawBalance]:
    expected_field_names = [
        'Name', 'Currency', 'Balance', 'Last Updated', 'State',
        'Last Transaction'
    ]
    balances = []
    filename = os.path.abspath(filename)
    with open(filename, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames != expected_field_names:
            raise RuntimeError(
                'Actual field names %r != expected field names %r' %
                (reader.fieldnames, expected_field_names))
        for line_i, row in enumerate(reader):
            date_str = row['Last Transaction'].strip()
            if not date_str:
                continue
            date = datetime.datetime.strptime(date_str, icscards_date_format).date()
            balances.append(
                RawBalance(
                    account=row['Name'],
                    date=date,
                    amount=Amount(D(row['Balance']), row['Currency']),
                    filename=filename,
                    line=line_i + 1))
        return balances


def _get_key_from_posting(entry: Transaction, posting: Posting,
                          source_postings: List[Posting], source_desc: str,
                          posting_date: datetime.date):
    del entry
    del source_postings
    return (posting.account, posting_date, posting.units, source_desc)


def _get_key_from_csv_entry(x: ICScardsEntry):
    return (x.account, x.date, x.amount, x.source_desc)


def _make_import_result(icscards_entry: ICScardsEntry) -> ImportResult:
    transaction = Transaction(
        meta=None,
        date=icscards_entry.date,
        flag=FLAG_OKAY,
        payee=None,
        narration=icscards_entry.source_desc,
        tags=EMPTY_SET,
        links=EMPTY_SET,
        postings=[
            Posting(
                account=icscards_entry.account,
                units=icscards_entry.amount,
                cost=None,
                price=None,
                flag=None,
                meta=collections.OrderedDict(
                    source_desc=icscards_entry.source_desc,
                    date=icscards_entry.date,
                )),
            Posting(
                account=FIXME_ACCOUNT,
                units=-icscards_entry.amount,
                cost=None,
                price=None,
                flag=None,
                meta=None,
            ),
        ])
    return ImportResult(
        date=icscards_entry.date, info=get_info(icscards_entry), entries=[transaction])

class ICScardsSource(description_based_source.DescriptionBasedSource):
    def __init__(self,
                 filename: str,
                 balances_directory: Optional[str] = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.filename = filename
        self.balances_directory = balances_directory

        # In these entries, account refers to the icscards_id, not the journal account.
        self.log_status('icscards: loading %s' % filename)
        self.icscards_entries = load_transactions(filename)

        # Balances are in the same file
        self.log_status('icscards: loading %s' % filename)
        self.balances = load_balances(filename)

    def prepare(self, journal: JournalEditor, results: SourceResults) -> None:
        account_to_icscards_id, icscards_id_to_account = description_based_source.get_account_mapping(
            journal.accounts, 'icscards_id')
        missing_accounts = set()  # type: Set[str]

        def get_converted_icscards_entries(entries):
            for raw_icscards_entry in entries:
                account = icscards_id_to_account.get(raw_icscards_entry.account)
                if not account:
                    missing_accounts.add(raw_icscards_entry.account)
                    continue
                match_entry = raw_icscards_entry._replace(account=account)
                yield match_entry

        description_based_source.get_pending_and_invalid_entries(
            raw_entries=get_converted_icscards_entries(self.icscards_entries),
            journal_entries=journal.all_entries,
            account_set=account_to_icscards_id.keys(),
            get_key_from_posting=_get_key_from_posting,
            get_key_from_raw_entry=_get_key_from_csv_entry,
            make_import_result=_make_import_result,
            results=results)

        for icscards_account in missing_accounts:
            results.add_warning(
                'No Beancount account associated with ICScards account %r.' %
                (icscards_account, ))

        for raw_balance in get_converted_icscards_entries(self.balances):
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
        return 'icscards'

def load(spec, log_status):
    return ICScardsSource(log_status=log_status, **spec)

def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('path')

    args = ap.parse_args()

    f_in = csv.reader(open(args.path), quotechar='"', newline='')
    for line in f_in:
        print(line)

if __name__ == '__main__':
    main()
