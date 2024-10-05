import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def convert_currency(amount, from_currency, to_currency):
    url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        rate = data['rates'].get(to_currency)
        if rate is None:
            raise ValueError(f"Invalid target currency: {to_currency}")
        return amount * rate
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching exchange rate: {e}")
    except ValueError as e:
        raise RuntimeError(f"Error processing exchange rate data: {e}")

@app.route('/convert_currency', methods=['POST'])
def convert_currency_route():
    data = request.json
    if not all(k in data for k in ('amount', 'from_currency', 'to_currency')):
        return jsonify({'error': 'Invalid input. Must include amount, from_currency, and to_currency.'}), 400
    try:
        amount = float(data['amount'])
        from_currency = data['from_currency']
        to_currency = data['to_currency']
        converted_amount = convert_currency(amount, from_currency, to_currency)
        return jsonify({'converted_amount': converted_amount})
    except ValueError:
        return jsonify({'error': 'Invalid amount. Must be a number.'}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)