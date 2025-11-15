import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from config import Config
import spacy

class MarketingScriptRecommender:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.products = self._load_products()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️  SpaCy model not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def _load_products(self):
        """Load all products from database"""
        try:
            products = list(self.db.products.find())
            print(f"✅ Loaded {len(products)} products from database")
            return products
        except Exception as e:
            print(f"❌ Error loading products: {e}")
            return []
    
    def extract_features_from_text(self, text):
        """Extract features from any product description"""
        if not text or not self.nlp:
            return []
        
        doc = self.nlp(text)
        features = []
        for token in doc:
            if token.pos_ in ["NOUN", "ADJ"] and not token.is_stop and len(token.text) > 2:
                features.append(token.lemma_.lower())
        
        return list(set(features))
    
    def calculate_similarity(self, features1, features2):
        """Calculate Jaccard similarity between feature sets"""
        if not features1 or not features2:
            return 0.0
        
        set1 = set(features1)
        set2 = set(features2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def find_similar_products(self, input_product, top_n=5):
        """Find similar products for ANY input product"""
        input_features = self.extract_features_from_text(input_product.get('description', ''))
        
        if input_product.get('category'):
            input_features.extend(input_product['category'].lower().split())
        
        similarities = []
        for db_product in self.products:
            db_features = db_product.get('features', [])
            similarity = self.calculate_similarity(input_features, db_features)
            
            category_bonus = 0.0
            if (input_product.get('category') and 
                db_product.get('category') and 
                input_product['category'].lower() == db_product['category'].lower()):
                category_bonus = 0.1
            
            total_similarity = similarity + category_bonus
            
            if total_similarity > 0:
                similarities.append({
                    'product': db_product,
                    'similarity': total_similarity,
                    'features': db_features
                })
        
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_n]
    
    def generate_marketing_script(self, input_product, similar_products):
        """Generate a professional marketing script"""
        if not similar_products:
            return "No similar products found to generate marketing script."
        
        input_name = input_product.get('name', 'This product')
        input_category = input_product.get('category', 'product')
        input_price = input_product.get('price', '')
        input_features = self.extract_features_from_text(input_product.get('description', ''))
        
        script_parts = []
        script_parts.append(f"🎬 **VIDEO SCRIPT**")
        script_parts.append(f"Introducing {input_name} - the ultimate {input_category} solution!")
        
        if input_features:
            script_parts.append(f"\n🔥 **KEY FEATURES:**")
            key_features = input_features[:4]
            for i, feature in enumerate(key_features, 1):
                script_parts.append(f"{i}. {feature.upper()} - Designed for maximum performance")
        
        script_parts.append(f"\n⭐ **WHY YOU'LL LOVE IT:**")
        script_parts.append(f"Join thousands of satisfied customers who trust our {input_category} solutions!")
        
        script_parts.append(f"\n🚀 **CALL TO ACTION:**")
        if input_price:
            script_parts.append(f"Get your {input_name} for just ${input_price} today!")
        else:
            script_parts.append(f"Get your {input_name} today and experience the difference!")
        script_parts.append("👉 Order now and transform your experience!")
        
        return "\n".join(script_parts)
    
    def generate_social_media_post(self, input_product):
        """Generate social media content"""
        name = input_product.get('name', 'This amazing product')
        category = input_product.get('category', 'product')
        price = input_product.get('price', '')
        
        posts = []
        posts.append("📱 **INSTAGRAM POST**")
        posts.append(f"Meet your new favorite {category}! ✨")
        posts.append(f"Say hello to {name} - designed to make your life better! 🌟")
        if price:
            posts.append(f"Only ${price}!")
        posts.append(f"#{(category.replace(' ', '')).lower()} #innovation")
        
        posts.append("\n🐦 **TWITTER POST**")
        posts.append(f"Just launched: {name}! 🚀")
        posts.append(f"The {category} you've been waiting for is here.")
        if price:
            posts.append(f"Get it for ${price}!")
        posts.append("#Tech #Innovation")
        
        return "\n".join(posts)