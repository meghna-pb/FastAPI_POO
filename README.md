# FastAPIDecorator
FastAPIDecorator allows to transform any function into an API, generating a new route for each new function. There is a layer of basic authentication that can be used to access protected routes.
We have added some unit testing to the project as well.
For more information on FastAPI, you can look at the link [here](https://fastapi.tiangolo.com/).

## Prerequisites
### Create a virtual environment
```bash
python3 -m venv venv
source venv/Scripts/activate # sur Windows
source venv/bin/activate #sur Mac
```

### Install the requirements
```bash
pip install -r requirements.txt
```

## Usage
1. Basic Configuration
```python
from FastApiDecorator import FastApiDecoratorBuilder
# run this line to initialise the FastApi Decorator Builder
builder = FastApiDecoratorBuilder()
```

2. Defining Routes
To define a new route, you can just add 
Define routes using the `api_route` decorator:
```python
@builder.api_route(path="example", methods=["GET"], run_server=True)
def example_route(username: str):
    return f"Hello, {username}!"
```
The function should be a classic function which takes parameters as arguments but returns a string.

When the path is not given any argument, it automatically takes the function name as the route name for the API. See for an example below:
```python
@builder.api_route()
def addition(a: int, b: int):
    return a+b
```
The route name in the API for this function will automatically be set to "addition".

3. Running the server

To start the FastAPI application server, you have two ways of doing this:
```python
builder.run(host="0.0.0.0", port=8000)
```

Alternatively, we have made an argument in the `api_route` decorator where you can choose whether you want to run the server. In this case you have no need to use the previous command, simply set `run_server = True` when you configure the api_route decorator.

```python
@builder.api_route("diff", run_server=True)
def difference(a: int=0, b: int=4):
    """
    Endpoint pour soustraire deux nombres.
    """
    return a-b
```

4. Authentification

There is an authentification method in the `api_route` module, whereby we can generate some protected routes, safeguarded behind a username and password.
We have chosen to use a basic authentication method, using the functions already available in FastAPI. The `HTTPBasic` instance is created to set up the basic authentication security scheme. 

```python
security = HTTPBasic()
```

In the `Auth.py` file, the `get_current_user` function is defined to perform user authentication. It takes `HTTPBasicCredentials` as a dependency, which is automatically provided by FastAPI when using the `Depends` function with the `security` instance. 
It checks against the credentials stored in the `user_credentials.json` file, which has the couple {username : hashed password} stored. We use the `bcrypt` package to hash the password and check if the provided password corresponds to the one stored in the json file.

If the credentials are incorrect, it raises an `HTTPException` with a 401 Unauthorized status and the "Incorrect username and/or password" message.
To add new users to the credentials database, you can run the following command at the end of the Auth.py file. You can also remove users, with the `delete_user` method.

```python
user_db.add_user("new_user", "new_password")
```

If you want to protect a route, you have to set the parameter `auth_required` to True, and put `Depends(get_current_user)` as an argument of the function. 
.
```python
@builder.api_route("function", auth_required=True)
def function(args,username: str = Depends(get_current_user))
```

5. Configuration
This allows to set the default methods in the API.

```python
config = {
    "methodsAutomatic": True,
    "title": "Fast API Decorator",
    "methodsDefault": ["GET"]
}
builder.configure_api(config)
```

6. Rate-limiting

The rate-limiting is implemented using the `slowapi` library, specifically leverageing the `limits` package, and it provides a simple yet effective way to control the number of requests a client can make to an endpoint within a specified time frame. <br>
The rate limit can be specified for each route using the custom decorator provided by teh FastApiDecoratorBuilder. The client's IP address is used as the default key for tracking the request count. <br> 
In order to apply a rate limit to an API route, use the `api_route` decorator from the `FastApiDecoratorBuilder` class and specify the `rate_limit` parameter, using the following syntax "number/time unit", the available units second, minute, hour or day. For example:

```python
@builder.api_route("rate", rate_limit="5/minute")
def rate_limitation(request: Request):
    return {"message": "This is an example route with rate limiting."}
```
We decided against using a dictionary for rate-limiting due to potential scalability challenges. Moreover, the extensive features offered by the `slowapi` and `fastapi` libraries have opened up opportunities for us to delve into the diverse packages they encompass.

## Testing 
You can run the unit tests for FastApiDecorator using the provided `unittest` module

#### Cases 
**Root Route**
```python
def test_root_route(self):
    response = self.client.get("/")
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), {"Hello": "Welcome to the FastAPI Decorator Builder API!"})
```
Verify that the root route returns a status code of 200 (which means the request has succeeded) and the expected JSON response.

**Addition Route**
```python
def test_addition_route(self):
    response = self.client.get("/addition?a=2&b=3")
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), 5)
```
This tests the addition route by checking if the correct result is returned for the provided parameters. <br> The same test is also run for the difference function. 

**API Configuration**
```python
def test_api_configuration(self):
    self.assertTrue(builder.methodsAutomatic)
    self.assertEqual(builder.title, "FastAPI Decorator Builder")
    self.assertEqual(builder.methodsDefault, ["GET"])
```
Check that the API configuration matches the expected values.

** Rate Limit**
```python
 def test_rate_limited_route(self):
        response = self.client.get("/rate")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/rate")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/rate")
        self.assertEqual(response.status_code, 429)
```
This tests whether for the 2 requests per hour limit endpoint, we get the 429 error which means rate limit reached.


The final output consists in how many tests have passed/failed, and the execution time for these tests.

## Examples
Check out the `main.py` directory for usage examples.

## How to access the API
We have chosen to use the software Insomnia in order to view the output of the API, since it is intuitive to use. <br> For more information, you can look at the [Insomnia webite](https://docs.insomnia.rest/)
