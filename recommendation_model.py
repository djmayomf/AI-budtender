import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle

# Load and prepare data
data = pd.read_csv('data.csv')
user_product_ratings = data.pivot(index='user_id', columns='product_id', values='rating').fillna(0)

# Train a KNN model
model = NearestNeighbors(n_neighbors=5, algorithm='auto')
model.fit(user_product_ratings)

# Save the model
with open('recommendation_model.pkl', 'wb') as f:
    pickle.dump(model, f)
