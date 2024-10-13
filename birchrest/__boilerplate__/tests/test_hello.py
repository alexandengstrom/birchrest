import unittest

from birchrest.unittest import TestAdapter, BirchRestTestCase
from birchrest import BirchRest


class TestHello(BirchRestTestCase):
    
    def setUp(self) -> None:
        app = BirchRest()
        self.runner = TestAdapter(app)
        
    async def test_hello(self) -> None:
        response = await self.runner.get("/hello")
        self.assertOk(response)
        
    async def test_incorrect_route(self) -> None:
        response = await self.runner.get("/notexist")
        self.assertStatus(response, 404)
        
if __name__ == "__main__":
    unittest.main()
