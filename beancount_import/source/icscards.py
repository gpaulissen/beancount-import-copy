# -*-coding: utf-8-*-
# coding=utf-8

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
Excel XLSX) from https://wps.com and later use Python module openpyxl to read it.

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

The associated account is specified in row 3, column 2 below haeding ICS-klantnummer (ICS client number).

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

"""

from typing import List, Union, Optional, Set
from openpyxl import load_workbook
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

def convert_str_to_list(str, max_items, sep=r'\s\s+|\t|\n'):
    return [x for x in re.split(sep, str)[0:max_items]]

def convert_str_to_id_list(str, max_items, sep=r'\s\s+|\t|\n'):
    return [x.replace(' ', '_') for x in re.split(sep, str)[0:max_items]]

# account may be either the icscards_id or the journal account name
ICScardsEntry = collections.namedtuple(
    'ICScardsEntry',
    ['account', 'date', 'amount', 'price', 'source_desc', 'filename', 'line'])
RawBalance = collections.namedtuple(
    'RawBalance', ['account', 'date', 'amount', 'filename', 'line'])

def get_info(raw_entry: Union[ICScardsEntry, RawBalance]) -> dict:
    return dict(
        # type='text/csv',
        type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=raw_entry.filename,
        line=raw_entry.line,
    )

def load_transactions(filename: str, currency: str = 'USD') -> [List[ICScardsEntry], List[RawBalance]]:
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
        d = datetime.datetime.strptime(s, '%d %b').date()
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
    balance_names = [
        "Vorig openstaand saldo",
        "Totaal ontvangen betalingen",
        "Totaal nieuwe uitgaven",
        "Nieuw openstaand saldo"
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
    new_page_names = [
        'Datum',
        'ICS-klantnummer',
        'Volgnummer',
        'Bladnummer'
    ]
    page_date = None

    locale.setlocale(category=locale.LC_ALL, locale="Dutch") # Need to parse "05 mei" i.e. "05 may"

    try:
        entries = []
        balances = []
        account = None
        new_page = False
        filename = os.path.abspath(filename)
        wb = load_workbook(filename, read_only=True)
        for sheet_i, sheet_name in enumerate(wb.sheetnames, start=1):
            sheet = wb[sheet_name]
            for line_i, row in enumerate(sheet.rows, start=1):
                # Handle the two new page rows
                if (sheet_i == 1 and line_i == 2):
                    assert convert_str_to_list(row[0].value, 4) == new_page_names
                    new_page = True
                elif (sheet_i > 1 and line_i == 1):
                    assert [col.value for col in row[0:4]] == new_page_names
                    new_page = True
                elif new_page:
                    new_page = False
                    if page_date == None:
                        page_date, account = convert_str_to_list(row[0].value, 2)
                        page_date = datetime.datetime.strptime(page_date, '%d %B %Y').date()
                # Handle the balance row
                elif (sheet_i == 1 and line_i == 4) or (sheet_i > 1 and line_i == 3):
                    balance_names_actual, number, transaction_type = None, None, None
                    if sheet_i == 1:
                        cols = convert_str_to_list(row[0].value, 12)
                        balance_names_actual = cols[0:4]
                        number, transaction_type = cols[-2:]
                    else:
                        cols0 = convert_str_to_list(row[0].value, 3)
                        cols1 = convert_str_to_list(row[1].value, 1)
                        cols2 = convert_str_to_list(row[2].value, 1)
                        cols3 = convert_str_to_list(row[3].value, 1)
                        balance_names_actual = [cols0[0], cols1[0], cols2[0], cols3[0]]                                        
                        number, transaction_type = cols0[1:]  # Skip euro sign
                    assert balance_names_actual == balance_names, print("Actual: {0}; Expected: {1}".format(balance_names_actual, balance_names))
                        
                    # number something like € 1.827,97
                    number = D(number[2:].replace('.', '').replace(',', '.'))  # Skip euro sign and take care of comma's and points

                    if transaction_type == 'Af':
                        number = -number
                    elif transaction_type != 'Bij':
                        raise RuntimeError('Unknown transaction type "{0}" in row {1}'.format(transaction_type, line_i))
                    balances.append(
                        RawBalance(
                            account=account,
                            date=page_date,
                            amount=Amount(number=number, currency='EUR'),
                            filename=filename,
                            line=line_i))
                # Handle the rest
                else:
                    # Only keep the non null columns
                    row = [col for col in row if col.value != None]
                    if len(row) == 5 or len(row) == 7 or len(row) == 8:
                        # Use transaction date, index 0
                        breakpoint()
                        try:
                            date = get_date(row[0].value)
                        except Exception as e:
                            raise RuntimeError('Invalid date: {0}'.format(row[0].value)) from e

                        # Skip booking date, index 1
                        
                        # Description (2)
                        source_desc = row[2].value

                        # Add place and country
                        if len(row) >= 7:
                            source_desc += ", {0} ({1})".format(row[3].value, row[4].value)

                        # Is there a price?
                        price = None
                        price_currency = None
                        if len(row) == 8:
                            price = D(str(row[-3].value))
                            price_currency = row[-3].number_format[-4:-1]
                            
                        # Skip amount in foreign currency
                        number = D(str(row[-2].value))
                        if number == ZERO:
                            # Skip zero-dollar transactions.
                            # Some banks produce these, e.g. for an annual fee that is waived.
                            continue
                        
                        transaction_type = row[-1].value
                        if transaction_type == 'Af':
                            number = -number
                            price = -price if price != None else None
                        elif transaction_type != 'Bij':
                            raise RuntimeError('Unknown transaction type "{0}" in row {1}'.format(transaction_type, row))
                        
                        entry = ICScardsEntry(account=account,
                                              date=date,
                                              source_desc=source_desc,
                                              amount=Amount(number=number, currency='EUR'),
                                              price=Amount(number=price, currency=price_currency) if price != None else None,
                                              filename=filename,
                                              line=line_i)
                        if DEBUG:
                            print(entry)
                        entries.append(entry)

        # No need to sort balances: there is just one
        entries.reverse()
        entries.sort(key=lambda x: x.line)  # sort by date first, line next
        if DEBUG:
            print(entries)
            print(balances)
        return entries, balances

    except Exception as e:
        raise RuntimeError('XLSX file has incorrect format', filename) from e

def _get_key_from_posting(entry: Transaction, posting: Posting,
                          source_postings: List[Posting], source_desc: str,
                          posting_date: datetime.date):
    del entry
    del source_postings
    return (posting.account, posting_date, posting.units, source_desc)


def _get_key_from_entry(x: ICScardsEntry):
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
                price=icscards_entry.price,
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
        # Balances are in the same file
        self.icscards_entries, self.balances = load_transactions(filename)

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
            get_key_from_raw_entry=_get_key_from_entry,
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