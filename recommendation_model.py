import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

def load_data(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        data = pd.read_csv(file_path)
        logging.info(f"Data loaded successfully from {file_path}")
        
        # Validate data
        if 'user_id' not in data.columns or 'product_id' not in data.columns or 'rating' not in data.columns:
            raise ValueError("Data must contain 'user_id', 'product_id', and 'rating' columns")
        
        return data
    except FileNotFoundError as e:
        logging.error(e)
        raise
    except pd.errors.EmptyDataError:
        logging.error(f"No data: {file_path}")
        raise
    except pd.errors.ParserError as e:
        logging.error(f"Error parsing data: {e}")
        raise
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise

def train_knn_model(data):
    try:
        user_product_ratings = data.pivot(index='user_id', columns='product_id', values='rating').fillna(0)
        model = NearestNeighbors(n_neighbors=5, algorithm='auto')
        model.fit(user_product_ratings)
        logging.info("KNN model trained successfully")
        return model
    except Exception as e:
        logging.error(f"Error training model: {e}")
        raise

def save_model(model, file_path):
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(model, f)
        logging.info(f"Model saved successfully to {file_path}")
    except Exception as e:
        logging.error(f"Error saving model: {e}")
        raise

if __name__ == "__main__":
    data_file_path = 'data.csv'
    model_file_path = 'recommendation_model.pkl'

    try:
        data = load_data(data_file_path)
        model = train_knn_model(data)
        save_model(model, model_file_path)
    except Exception as e:
        logging.error(f"An error occurred: {e}")