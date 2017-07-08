"""
Usage:
  book_flight.py --date DATE --from IATA --to IATA [--one-way | --return DAYS]
                                                   [--cheapest | --shortest]
  book_flight.py (-h | --help)
  book_flight.py --version

Options:
  -h --help      Show this screen.
  --return DAYS  Book 2 flights there and back again with a gap in 5 nights.
  --one-way      One way flight [default].
  --cheapest     Book cheapest flight [default].
  --shortest     Book shortest flight.
  --date DATE    Format: YYYY-MM-DD
  --from IATA    IATA code.
  --to IATA      IATA code.
  --version      Version of the application
"""
from docopt import docopt
from schema import Schema, And, Or, Use, SchemaError

from datetime import datetime

import requests


API_HOST = {
    'search': 'https://api.skypicker.com',
    'booking': 'http://37.139.6.125:8080'
}


def find_flight(date, from_, to, return_, shortest):
    payload = {
        'v': 3,
        'dateFrom': date,
        'dateTo': date,
        'flyFrom': from_,
        'to': to,
        'affilid': 'picky'
    }

    if return_:
        payload['daysInDestinationTo'] = return_
        payload['daysInDestinationFrom'] = return_
        payload['typeFlight'] = 'return'
    else:
        payload['typeFlight'] = 'oneway'  # Default option

    if shortest:
        payload['sort'] = 'duration'
    else:
        payload['sort'] = 'price'  # Default option

    service_url = '{}/flights'.format(API_HOST['search'])
    resp = requests.get(service_url, params=payload)

    # data = error_handling(resp)
    data = resp.json()

    if data['_results'] == 0:
        raise Exception(
            'Flights not found'
        )
    return data['data'][0]['booking_token']


def book_flight(date, from_, to, return_, shortest):
    save_book_payload = {
        "passengers": [
            {
                'firstName': 'Name',
                'lastName': 'Surname',
                'title': 'Mr',
                'birthday': '1991-01-01',
                'documentID': 'TEST5121905',
                'email': 'test@test.com'
            }
        ],
        "currency": "EUR",
        "booking_token": find_flight(date, from_, to, return_, shortest)
    }

    service_url = '{}/booking'.format(API_HOST['booking'])
    resp = requests.post(service_url, json=save_book_payload)

    # data = error_handling(resp)
    data = resp.json()

    if data['status'] == 'confirmed':
        return data['pnr']
    else:
        raise Exception(
            'Status: not confirmed'
        )


# def error_handling(resp):
#     if resp.status_code == 200:
#         return resp.json()
#     else:
#         raise Exception(
#             'ERROR! Status code: {}, '
#             'Content: {}'.format(resp.status_code, resp.content)
#         )


def main():
    arguments = docopt(__doc__, version='1.0.0')

    schema = Schema({
        '--date': And(str, lambda s: datetime.strptime(s, '%Y-%m-%d')),
        '--from': And(str, lambda s: len(s) == 3 and s.isalpha()),
        '--to': And(str, lambda s: len(s) == 3 and s.isalpha()),
        '--return': Or(None, Use(int)),
        '--cheapest': bool,
        '--one-way': bool,
        '--shortest': bool,
        '--help': bool,
        '--version': bool
    })
    try:
        arguments = schema.validate(arguments)
    except SchemaError as e:
        exit('{0}\n\n'
             'book_flight.py -h or --help for help message'.format(e))

    dt = datetime.strptime(arguments['--date'], '%Y-%m-%d').strftime('%d/%m/%Y')

    pnr = book_flight(date=dt,
                      from_=arguments['--from'],
                      to=arguments['--to'],
                      return_=arguments['--return'],
                      shortest=arguments['--shortest'])
    return pnr

if __name__ == '__main__':
    print('Your PNR number is:', main())
