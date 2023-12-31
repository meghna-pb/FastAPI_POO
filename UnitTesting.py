import unittest
from fastapi.testclient import TestClient
from FastApiDecorator import FastApiDecoratorBuilder
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from Auth import security

class TestFastApiDecoratorBuilder(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(builder.app)

    def test_root_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"Hello": "Welcome to the FastAPI Decorator Builder API!"})

    def test_addition_route(self):
        response = self.client.get("/addition?a=2&b=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 5)

    def test_difference_route(self):
        response = self.client.get("/diff?a=5&b=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 3)
    
    def test_rate_limited_route(self):
        response = self.client.get("/rate")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/rate")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/rate")
        self.assertEqual(response.status_code, 429)

    def test_api_configuration(self):
        self.assertTrue(builder.methodsAutomatic)
        self.assertEqual(builder.title, "FastAPI Decorator Builder")
        self.assertEqual(builder.methodsDefault, ["GET"])

if __name__ == '__main__':
    from fastapi import Depends, Request
    from Auth import get_current_user

    # utilisation du décorateur
    builder = FastApiDecoratorBuilder()

    # Configuration additionnelle de l'API
    builder.configure_api({
    "title": "FastAPI Decorator Builder",
    "methodsAutomatic": True,
    "methodsDefault": ["GET"]
    })

    ################# IMPLEMENTATION EXAMPLES  #################

    @builder.api_route("diff", run_server=False)
    def difference(a: int, b: int) -> int:
        """
        Endpoint to subtract two integers.
        """
        return a-b

    @builder.api_route(run_server=False)
    def addition(a: int, b: int)->int:
        """
        Endpoint to add two integers.
        """
        return a+b

    @builder.api_route("rate", rate_limit="2/hour")
    def example_route(request: Request)->str:
        """
        Demonstrates a rate-limited endpoint, allowing only 2 requests per hour from the same client. 
        """
        return "Rate-limited route."


    @builder.api_route("protected", auth_required=True, run_server=False)
    def protected_data(username: str = Depends(get_current_user)) -> str:
        """
        Provides access to authenticated users only
        """
        return f"Hello, {username}"

    unittest.main()
