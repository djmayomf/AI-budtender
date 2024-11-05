from flask import Flask, request, jsonify
import requests

def convert_currency(amount, from_currency, to_currency):
    url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
    response = requests.get(url)
    data = response.json()
    rate = data['rates'].get(to_currency, 1)
    return amount * rate

@app.route('/convert_currency', methods=['POST'])
def convert_currency_route():
    data = request.json
    amount = data['amount']
    from_currency = data['from_currency']
    to_currency = data['to_currency']
    converted_amount = convert_currency(amount, from_currency, to_currency)
    return jsonify({'converted_amount': converted_amount})

if __name__ == '__main__':
    app.run(debug=True)