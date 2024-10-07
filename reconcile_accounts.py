import csv
from pathlib import Path
from pprint import pprint
from collections import defaultdict
from datetime import date, timedelta


def reconcile_accounts(transactions1: list[list[str]], transactions2: list[list[str]]) -> tuple[list[list[str]], list[list[str]]]:
    '''
    Given 2 lists of lists of transactions, compare the transactions on each list
    to find the corresponding matching transaction.
    Returns a copy of the original lists identifying if the transaction has been found
    on the other list.

    If the transaction has been the same but made within one on the second list,
    we match with the most recent date.

    If there are any transaction duplicates in one list, we only match one of them
    and the remaining ones are missing.

    Ex:
    transactions1: [
        ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket'],
        ['2020-12-06', 'Tecnologia', '16.00', 'Bitbucket'],
    ]
    transactions2: [
        ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket'],
        ['2020-12-06', 'Tecnologia', '16.00', 'Bitbucket'],
    ]

    Returns:
    (
        [
            ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket', 'FOUND'],
            ['2020-12-06', 'Tecnologia', '16.00', 'Bitbucket', 'MISSING'],
        ],
        [
            ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket', 'FOUND'],
        ]
    )
    '''
    transactions1_map = _create_transaction_identifier_date_map(transactions1)
    transactions2_map = _create_transaction_identifier_date_map(transactions2)
    
    
    transactions1_copy = [[v for v in transaction] for transaction in transactions1]
    transactions1_result = _match_transactions(transactions1_copy, transactions2_map)

    
    transactions2_copy = [[v for v in transaction] for transaction in transactions2]
    transactions2_result = _match_transactions(transactions2_copy, transactions1_map)

    return transactions1_result, transactions2_result


def _match_transactions(transactions_origin: list[list[str]], transactions_map: dict) -> list[list[str]]:
    '''
    Given a list of transactions and a map, identifies if transactions from the transactions_origin
    are in the transactions_map and mutates the original list with FOUND or MISSING depending if there
    was a match.

    Ex:
    transactions_origin: [
        ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket'],
        ['2020-12-06', 'Tecnologia', '16.00', 'Bitbucket'],
    ]
    transactions_map: {
        "Tecnologia,16.00,Bitbucket": {"2020-12-04": False}
    }

    Returns: [
        ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket', 'FOUND'],
        ['2020-12-06', 'Tecnologia', '16.00', 'Bitbucket', 'MISSING'],
    ]
    '''
    found_matches = set()
    for i, transaction in enumerate(transactions_origin):
        
        dateless_transaction_identifier = ','.join(transaction[1:])
        transaction_date_str = transaction[0]
        transaction_str = f'{transaction_date_str},{dateless_transaction_identifier}'
        

        if not transaction_date_str:
            continue
        elif transaction_str in found_matches:
            transactions_origin[i].append("MISSING")
            continue

        transaction_in_map = _is_transaction_in_map(dateless_transaction_identifier, transaction_date_str, transactions_map)
        if transaction_in_map:
            found_matches.add(transaction_str)
            transactions_origin[i].append("FOUND")
        else:
            transactions_origin[i].append("MISSING")
    
    return transactions_origin


def _is_transaction_in_map(transaction_id: str, transaction_date_str: str, transactions_map: dict) -> bool:
    '''
    Verify if given transaction_id and transaction_date_str matches a transaction map
    given it hasn't been found yet. 
    
    If the transaction_id matches a transaction on the map, we give priority to the transactions
    that occurred the day before.

    Ex:
    transactions_id: 'Tecnologia,16.00,Bitbucket'
    transaction_date_str: '2020-12-04'

    transactions_map: {
        "Tecnologia,16.00,Bitbucket": {"2020-12-03": False}
    }

    Returns:
    True
    '''
    transaction_date = date.fromisoformat(transaction_date_str)
    day_before_transaction = (transaction_date - timedelta(days=1)).strftime("%Y-%m-%d")
    day_after_transaction = (transaction_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    found = False
    
    if transactions_map.get(transaction_id, {}) and transactions_map[transaction_id].get(transaction_date_str) == False:
        if transactions_map[transaction_id].get(day_before_transaction) == False:
            # give priority to the first transaction made the day before
            transactions_map[transaction_id][day_before_transaction] = True
        else:
            transactions_map[transaction_id][transaction_date_str] = True
        found = True
    elif transactions_map.get(transaction_id, {}):
        if transactions_map[transaction_id].get(day_before_transaction) == False:
            transactions_map[transaction_id][day_before_transaction] = True
            found = True
        elif transactions_map[transaction_id].get(day_after_transaction) == False:
            transactions_map[transaction_id][day_after_transaction] = True
            found = True
    
    return found



def _create_transaction_identifier_date_map(transactions_list: list[list]) -> dict:
    '''
    Creates a map of the transactions and it's dates, mapped by a boolean value
    if it has been found.

    Ex:
    [
        ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket'],
        ['2020-12-06', 'Tecnologia', '16.00', 'Bitbucket'],
    ] 
    Returns:
    {
        "Tecnologia,16.00,Bitbucket": {"2020-12-04": False, "2020-12-06": False}
    } 
    '''
    transactions_map = defaultdict(dict)
    for transaction in transactions_list:
        dateless_transaction_identifier = ','.join(transaction[1:])
        transactions_map[dateless_transaction_identifier].update({transaction[0]: False})
    
    return transactions_map
