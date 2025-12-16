import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

class LocalVectorSearch:
    """FREE local vector search using sentence-transformers"""
    
    def __init__(self, product_catalog_path="data/product_catalog.json"):
        # Load FREE embedding model (runs locally, no API calls)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 90MB, good for prototype
        
        # Load product catalog
        with open(product_catalog_path, 'r') as f:
            data = json.load(f)
        
        self.products = data["products"]
        self.index = None
        self.product_texts = []
        
        self._build_index()
    
    def _build_index(self):
        """Build FAISS index for similarity search"""
        # Create text representations of products
        for product in self.products:
            text = f"{product['name']} {product['description']} "
            text += " ".join(product['technical_keywords'])
            for key, value in product['specs'].items():
                text += f" {key}: {value}"
            self.product_texts.append(text)
        
        # Generate embeddings
        embeddings = self.model.encode(self.product_texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        print(f"Built index for {len(self.products)} products")
    
    def find_similar_products(self, query_text, k=3):
        """Find similar products using vector similarity"""
        query_embedding = self.model.encode([query_text])
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.products):
                product = self.products[idx].copy()
                product['similarity_score'] = float(1 / (1 + distance))  # Convert to similarity
                results.append(product)
        
        return results

# Test the vector search
if __name__ == "__main__":
    vs = LocalVectorSearch()
    results = vs.find_similar_products("cloud platform with high availability")
    print("Test Results:", results[:2])