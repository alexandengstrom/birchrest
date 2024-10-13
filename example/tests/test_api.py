import unittest

from birchrest import BirchRest
from birchrest.unittest import TestAdapter, BirchRestTestCase

class ApiTest(BirchRestTestCase):
    
    def setUp(self) -> None:
        app = BirchRest(log_level="test")
        self.runner = TestAdapter(app)
        
    async def test_user_route(self) -> None:
        response = await self.runner.get("/user")
        self.assertOk(response)
        
    async def test_invalid_id(self) -> None:
        response = await self.runner.get("/user/0")
        self.assertNotOk(response)
        self.assertStatus(response, 400)
        
        
if __name__ == "__main__":
    unittest.main()
