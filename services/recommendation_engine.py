import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from typing import List, Dict
import joblib
import os

class RecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.strain_vectors = None
        self.strain_data = None
        self.user_preferences_model = None
        self.load_models()

    def load_models(self):
        """Load or train recommendation models"""
        try:
            # Load pre-trained models if they exist
            self.user_preferences_model = joblib.load('models/user_preferences.joblib')
            self.strain_vectors = joblib.load('models/strain_vectors.joblib')
            self.strain_data = joblib.load('models/strain_data.joblib')
        except FileNotFoundError:
            # Train new models if they don't exist
            self.train_models()

    def train_models(self):
        """Train recommendation models"""
        # Load strain data
        strains_df = pd.read_json('data/strains.json')
        
        # Create strain vectors based on descriptions and effects
        strain_texts = strains_df.apply(
            lambda x: f"{x['description']} {' '.join(x['effects'])} {' '.join(x['flavors'])}",
            axis=1
        )
        self.strain_vectors = self.vectorizer.fit_transform(strain_texts)
        self.strain_data = strains_df

        # Train user preferences model
        self.user_preferences_model = RandomForestClassifier(n_estimators=100)
        # Train with historical user preference data if available
        
        # Save models
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.user_preferences_model, 'models/user_preferences.joblib')
        joblib.dump(self.strain_vectors, 'models/strain_vectors.joblib')
        joblib.dump(self.strain_data, 'models/strain_data.joblib')

    def get_personalized_recommendations(
        self, 
        user_id: int, 
        mood: str, 
        time_of_day: str, 
        previous_likes: List[str]
    ) -> List[Dict]:
        """Get personalized strain recommendations"""
        # Get user preferences
        user_vector = self._get_user_vector(user_id, mood, time_of_day, previous_likes)
        
        # Calculate similarity scores
        similarities = cosine_similarity(user_vector, self.strain_vectors)
        
        # Get top recommendations
        top_indices = similarities[0].argsort()[-5:][::-1]
        recommendations = self.strain_data.iloc[top_indices]
        
        return recommendations.to_dict('records')

    def _get_user_vector(
        self, 
        user_id: int, 
        mood: str, 
        time_of_day: str, 
        previous_likes: List[str]
    ):
        """Create a user preference vector"""
        # Combine user preferences into a single text
        user_prefs = f"{mood} {time_of_day} {' '.join(previous_likes)}"
        return self.vectorizer.transform([user_prefs])

    def update_user_preferences(self, user_id: int, strain_id: int, rating: int):
        """Update user preferences based on ratings"""
        # Update user preference model with new rating
        strain = self.strain_data.loc[strain_id]
        features = self.vectorizer.transform([strain['description']])
        self.user_preferences_model.partial_fit(features, [rating])

    def get_mood_based_recommendations(self, mood: str) -> List[Dict]:
        """Get recommendations based on user's current mood"""
        mood_effects = {
            'energetic': ['energetic', 'uplifted', 'focused'],
            'relaxed': ['relaxed', 'calm', 'sleepy'],
            'creative': ['creative', 'euphoric', 'focused'],
            'social': ['talkative', 'uplifted', 'giggly'],
            'stressed': ['relaxed', 'stress-relief', 'calm']
        }
        
        effects = mood_effects.get(mood.lower(), ['relaxed'])
        effects_text = ' '.join(effects)
        effects_vector = self.vectorizer.transform([effects_text])
        
        similarities = cosine_similarity(effects_vector, self.strain_vectors)
        top_indices = similarities[0].argsort()[-5:][::-1]
        
        return self.strain_data.iloc[top_indices].to_dict('records')

    def get_time_based_recommendations(self, time_of_day: str) -> List[Dict]:
        """Get recommendations based on time of day"""
        time_preferences = {
            'morning': ['energetic', 'focused', 'clear'],
            'afternoon': ['balanced', 'creative', 'uplifted'],
            'evening': ['relaxed', 'calm', 'sleepy']
        }
        
        effects = time_preferences.get(time_of_day.lower(), ['balanced'])
        effects_vector = self.vectorizer.transform([' '.join(effects)])
        
        similarities = cosine_similarity(effects_vector, self.strain_vectors)
        top_indices = similarities[0].argsort()[-5:][::-1]
        
        return self.strain_data.iloc[top_indices].to_dict('records') 