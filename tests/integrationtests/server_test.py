# type: ignore

import unittest
import requests
import json

class TestServer(unittest.TestCase):

    def test_get_user_by_id(self):
        user_id = 1
        response = requests.get(f"http://127.0.0.1:13337/user/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        self.assertEqual(response.json()["id"], user_id)
        self.assertEqual(response.json()["name"], "John Doe")
        
    def test_get_user_by_id_that_doesnt_exist(self):
        response = requests.get(f"http://127.0.0.1:13337/user/99")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "Not Found")
        self.assertEqual(response.json()["error"]["message"], "No user with id 99 exists")
        
    def test_incorrect_params(self):
        response = requests.get(f"http://127.0.0.1:13337/user/invalid")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "Bad Request")
        
        response = requests.get(f"http://127.0.0.1:13337/user/-1")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "Bad Request")
        
        response = requests.get(f"http://127.0.0.1:13337/user/1.2")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "Bad Request")
        
    def test_incorrect_method(self):
        response = requests.patch(f"http://127.0.0.1:13337/user/1")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["error"]["code"], "Method Not Allowed")
        
        response = requests.options(f"http://127.0.0.1:13337/user/1")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["error"]["code"], "Method Not Allowed")  
    
        
    def test_get_users(self):
        response = requests.get("http://127.0.0.1:13337/user")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        
    def test_get_users_with_queries_which_is_not_allowed(self):
        response = requests.get("http://127.0.0.1:13337/user?name=john")
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.json(), dict)
        
    def test_create_user(self):
        response = requests.post("http://127.0.0.1:13337/user", json={
            "name": "Johan Doe",
            "age": 31
        })
        self.assertEqual(response.status_code, 201)
        
    def test_get_user_messages(self):
        response = requests.get("http://127.0.0.1:13337/user/1/messages")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 2)
        

if __name__ == "__main__":
    unittest.main()
