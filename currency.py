from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def convert_currency(amount, from_currency, to_currency):
    url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Check if the to_currency exists in the rates
        if to_currency not in data['rates']:
            return None
        
        rate = data['rates'][to_currency]
        return amount * rate
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except ValueError:
        print("Error parsing JSON response")
        return None

@app.route('/convert_currency', methods=['POST'])
def convert_currency_route():
    data = request.json
    
    # Input validation
    if 'amount' not in data or 'from_currency' not in data or 'to_currency' not in data:
        return jsonify({'error': 'Missing required fields: amount, from_currency, to_currency'}), 400
    
    try:
        amount = float(data['amount'])
        from_currency = data['from_currency'].upper()
        to_currency = data['to_currency'].upper()
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid input types'}), 400

    converted_amount = convert_currency(amount, from_currency, to_currency)
    
    if converted_amount is None:
        return jsonify({'error': 'Invalid currency code or conversion failed'}), 400
    
    return jsonify({'converted_amount': converted_amount})

if __name__ == '__main__':
    app.run(debug=True)