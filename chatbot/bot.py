from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import torch
from typing import Dict, List
import json
import os
from services.recommendation_engine import RecommendationEngine
from datetime import datetime
import pytz

class BudBot:
    def __init__(self):
        self.model = GPTNeoForCausalLM.from_pretrained('EleutherAI/gpt-neo-1.3B')
        self.tokenizer = GPT2Tokenizer.from_pretrained('EleutherAI/gpt-neo-1.3B')
        self.strain_data = self._load_strain_data()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.recommendation_engine = RecommendationEngine()
        self.user_sessions = {}
        
    def _load_strain_data(self) -> Dict:
        """Load strain data from JSON file"""
        try:
            with open('data/strains.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def generate_response(self, user_input: str) -> str:
        """Generate response using GPT-Neo"""
        # Add context about cannabis
        prompt = f"""
        As a knowledgeable cannabis assistant, help with this question:
        {user_input}
        
        Response:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=150,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Response:")[-1].strip()

    def get_strain_info(self, strain_name: str) -> Dict:
        """Get specific strain information"""
        return self.strain_data.get(strain_name.lower(), {})

    def get_strain_recommendations(self, effects: List[str]) -> List[Dict]:
        """Get strain recommendations based on desired effects"""
        recommendations = []
        for strain, info in self.strain_data.items():
            if any(effect.lower() in info['effects'] for effect in effects):
                recommendations.append({
                    'name': strain,
                    'info': info
                })
        return recommendations[:5]  # Return top 5 matches 

    def get_time_based_greeting(self) -> str:
        """Get time-appropriate greeting"""
        hour = datetime.now(pytz.UTC).hour
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        else:
            return "Good evening"

    def start_conversation(self, user_id: str) -> str:
        """Start personalized conversation"""
        greeting = self.get_time_based_greeting()
        self.user_sessions[user_id] = {
            'stage': 'initial',
            'preferences': {}
        }
        
        return f"{greeting}! I'm your personal cannabis guide. To help you find the perfect product, could you tell me how you're feeling today?"

    def process_mood(self, user_id: str, mood: str) -> str:
        """Process user's mood and get recommendations"""
        session = self.user_sessions.get(user_id, {})
        session['preferences']['mood'] = mood.lower()
        
        recommendations = self.recommendation_engine.get_mood_based_recommendations(mood)
        
        response = f"Based on your {mood} mood, I think you might enjoy these strains:\n\n"
        for strain in recommendations:
            response += f"🌿 {strain['name']}: {strain['effects'][0]}, {strain['effects'][1]}\n"
        
        return response

    def get_personalized_recommendations(self, user_id: str) -> List[Dict]:
        """Get personalized recommendations based on user history"""
        session = self.user_sessions.get(user_id, {})
        preferences = session.get('preferences', {})
        
        return self.recommendation_engine.get_personalized_recommendations(
            user_id=user_id,
            mood=preferences.get('mood', 'relaxed'),
            time_of_day=self.get_current_time_period(),
            previous_likes=preferences.get('liked_strains', [])
        )

    def get_current_time_period(self) -> str:
        """Get current time period for recommendations"""
        hour = datetime.now(pytz.UTC).hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        else:
            return 'evening'

    def handle_strain_rating(self, user_id: str, strain_id: int, rating: int):
        """Handle user's strain rating"""
        self.recommendation_engine.update_user_preferences(user_id, strain_id, rating)
        session = self.user_sessions.get(user_id, {})
        preferences = session.get('preferences', {})
        
        if rating >= 4:  # If user liked the strain
            liked_strains = preferences.get('liked_strains', [])
            strain = self.strain_data.get(strain_id, {})
            if strain:
                liked_strains.append(strain['name'])
                preferences['liked_strains'] = liked_strains