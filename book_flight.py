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
import requests

from datetime import datetime


API_HOST = {
    'search': 'https://api.skypicker.com',
    'booking': 'http://37.139.6.125:8080'
}


def find_flight(date, from_, to, return_, shortest):
    """
    Generate and send request based on arguments for flight search
    :return: booking token of flight
    """
    payload = {
        'v': 3,
        'dateFrom': date,
        'dateTo': date,
        'flyFrom': from_,
        'to': to,
        'affilid': 'picky',
        'typeFlight': 'return' if return_ else 'oneway',
        'sort': 'duration' if shortest else 'price'
    }
    if return_:
        payload['daysInDestinationTo'] = return_
        payload['daysInDestinationFrom'] = return_

    service_url = '{}/flights'.format(API_HOST['search'])
    resp = requests.get(service_url, params=payload)

    try:
        resp.raise_for_status()
        data = resp.json()
        if data['_results'] == 0:
            raise Exception('Flights not found')
        return data['data'][0]['booking_token']
    except Exception as e:
        exit(e)


def book_flight(date, from_, to, return_, shortest):
    """
    Book flight
    :return: PNR number
    """
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

    try:
        resp.raise_for_status()
        data = resp.json()
        if data['status'] == 'confirmed':
            return data['pnr']
        else:
            raise Exception('Status: not confirmed')
    except Exception as e:
        exit(e)


def main():
    arguments = docopt(__doc__, version='1.0.0')

    #  Argument validation
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
        exit('{0}\n'
             'book_flight.py --help or -h for help message'.format(e))

    dt = datetime.strptime(arguments['--date'], '%Y-%m-%d').strftime('%d/%m/%Y')

    return book_flight(date=dt,
                       from_=arguments['--from'],
                       to=arguments['--to'],
                       return_=arguments['--return'],
                       shortest=arguments['--shortest'])

if __name__ == '__main__':
    print('Your PNR number is:', main())
