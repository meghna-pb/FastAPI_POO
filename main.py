from FastApiDecorator import FastApiDecoratorBuilder
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


@builder.api_route("protected", auth_required=True, run_server=True)
def protected_data(username: str = Depends(get_current_user)) -> str:
    """
    Provides access to authenticated users only
    """
    return f"Hello, {username}"


# LANCEMENT MANUEL de l'API avec uvicorn
#if __name__ == "__main__":
#     uvicorn.run(builder.app, host="0.0.0.0", port=8000)


