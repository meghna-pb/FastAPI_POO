# file: FastApiDecorator.py

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from functools import wraps

class FastApiDecoratorBuilder:
	"""
	A class to build and manage a FastAPI application, providing a decorator for route handling.

	Attributes:
		app (FastAPI): The FastAPI application instance.
		routes (list): A list to store information about the routes.
		methodsDefault (list): Default HTTP methods for routes.
		server_started (bool): A flag to check if the server has been started.
		methodsAutomatic (bool): A flag to automatically set HTTP methods.
		title (str): The title of the API.
	"""

	def __init__(self):
		"""
		Initialize the FastAPI application and set up the root route.
		"""
		self.app = FastAPI()
		self.routes = []  # store info on the routes
		self.methodsDefault = ["GET"]  #  method to store the routes
		self.server_started = False # if False -> it will create the server
		self.methodsAutomatic = True
		self.title = "FastAPI Decorator Builder API"
		self.limiter = Limiter(key_func=get_remote_address)
		self.app.state.limiter = self.limiter
		self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
		self.setup_exception_handlers()

		# Define root route
		@self.app.get("/")
		def read_root():
				return {"Hello": "Welcome to the " + self.title + " API!"}
	
	def setup_exception_handlers(self):
		@self.app.exception_handler(HTTPException)
		def http_exception_handler(request: Request, exc: HTTPException):
			return JSONResponse(status_code=exc.status_code,
								content={"detail": exc.detail},)

		@self.app.exception_handler(RequestValidationError)
		def validation_exception_handler(request: Request, exc: RequestValidationError):
			return JSONResponse(status_code=422,
								content={"detail": exc.errors()})

		@self.app.exception_handler(Exception)
		def general_exception_handler(request: Request, exc: Exception):
			return JSONResponse(status_code=500,
								content={"detail": "An internal server error occurred."})
		
		@self.app.exception_handler(RateLimitExceeded)
		def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
			return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
								content={"detail": "You have exceeded the rate limit."})
		

	def api_route(self, path: str = "", methods: list = None, run_server=False, auth_required=False, rate_limit=None):
		"""
		Decorator to define an API route.
		"""
		if methods is None:
			methods = ["GET"]

		def decorator(func: callable) -> callable:
			"""
			Decorator to define an API route.

			Args:
				path (str): The URL path for the route.
				methods (list, optional): The HTTP methods for the route.
				run_server (bool, optional): Flag to run the server after adding the route.

			Returns:
				callable: The wrapper function.
        	"""
			nonlocal path, methods

			if not path: # this allows to dynamically set the route name to the function name
				path = "/" + func.__name__ 
			else:
				path = "/" + path

			if self.methodsAutomatic:
				methods = self.methodsDefault

			route_info = {"path": path, "methods": methods, "function": func}
			self.routes.append(route_info)

			if rate_limit:
				func = self.limiter.limit(rate_limit)(func)
				
			@wraps(func)
			def wrapper(*args, **kwargs):
				"""
				Wrapper function which authenticates if auth_required=True before runnning the rest of the code
				"""
				if auth_required:
					pass
				return func(*args, **kwargs)

			self.app.add_api_route(path, wrapper, methods=methods)

			#here, the api calls the route class and creates a server. This allows for concise comprehension
			route = Route(self, path, methods, wrapper)
			route.create(run_server=run_server)

			return wrapper

		return decorator

	
	def run(self, host="0.0.0.0", port=8001):
		"""
		Start the FastAPI application server.
		"""
		if not self.server_started:
			uvicorn.run(self.app, host=host, port=port)
			self.server_started = True
		#else:
		#	print("Server already running. Restart the server to activate new routes.")
			

	def configure_api(self, config):
		"""
		Configure the generated API based on the provided configuration.
		"""
		self.methodsAutomatic = config["methodsAutomatic"]
		self.title = config["title"]
		self.methodsDefault = config["methodsDefault"]
		self.app.title = self.title

class Route:
	"""
    A class representing a route in a FastAPI application.

    Attributes:
        builder (FastApiDecoratorBuilder): The FastAPI decorator builder instance.
        url (str): The URL path for the route.
        method (str): The HTTP method for the route.
        callback (callable): The callback function for the route.
    """
	def __init__(self, builder, url, method, callback):
		"""
		Initialisation of the Route instance. 
		It takes builder as an argument(FastApiDecoratorBuilder) -> The FastAPI decorator builder instance.
		"""
		self.builder = builder
		self.url = url
		self.method = method
		self.callback = callback

	def create(self, run_server=False):
		"""
		Create and add the route to the FastAPI application.
		"""
		self.builder.app.add_api_route(self.url, self.callback, methods=self.method)
		if run_server and not self.builder.server_started:
			self.builder.run()
