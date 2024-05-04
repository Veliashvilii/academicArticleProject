import pymongo
import fasttext
import numpy as np

class MongoDBManager:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["vectors"]
    
    def connect_to_collection(self, collection_name):
        return self.db[collection_name]
    
    def save_user_vector(self, collection, email, vector):
        user_data = {
            "_id": email,
            "vector": vector.tolist()
        }
        collection.insert_one(user_data)
        print("Kullanıcı vektörü başarıyla MongoDB'ye kaydedildi.")
    
class VectorProcessor:
    def __init__(self):
        self.model = fasttext.load_model("cc.en.300.bin")
    
    def get_vector_for_person(self, person):
        person_vector = np.mean([self.model.get_word_vector(word) for word in person], axis=0)
        return person_vector
    
    def process_user_vector(self, email, interests, collection):
        vector = self.get_vector_for_person(interests)
        manager = MongoDBManager()
        manager.save_user_vector(collection, email, vector)
