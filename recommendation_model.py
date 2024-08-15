import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle
import os

def load_data(file_path):
    """Load data from a CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    data = pd.read_csv(file_path)
    
    # Check if required columns are present
    required_columns = {'user_id', 'product_id', 'rating'}
    if not required_columns.issubset(data.columns):
        raise ValueError(f"Data must contain the following columns: {required_columns}")
    
    return data

def prepare_user_product_ratings(data):
    """Pivot the data to create a user-product ratings matrix."""
    return data.pivot(index='user_id', columns='product_id', values='rating').fillna(0)

def train_knn_model(user_product_ratings, n_neighbors=5):
    """Train a KNN model on the user-product ratings matrix."""
    model = NearestNeighbors(n_neighbors=n_neighbors, algorithm='auto')
    model.fit(user_product_ratings)
    return model

def save_model(model, file_path):
    """Save the trained model to a file."""
    with open(file_path, 'wb') as f:
        pickle.dump(model, f)

def main():
    try:
        # Load and prepare data
        data = load_data('data.csv')
        user_product_ratings = prepare_user_product_ratings(data)

        # Train a KNN model
        model = train_knn_model(user_product_ratings)

        # Save the model
        save_model(model, 'recommendation_model.pkl')
        print("Model trained and saved successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()