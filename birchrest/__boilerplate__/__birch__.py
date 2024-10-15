"""
This file must import all controllers in your project!    
"""

from src.controllers.hello_controller import HelloController

"""
Change this to your own information if you want to create openapi specs
"""
__openapi__ = {
    "info": {
        "title": "My API",  # The name of the API.
        "description": "API Description",  # A short description of your API.
        "termsOfService": "http://example.com/terms/",  # URL to the API's terms of service.
        "contact": {  # Contact information for the API.
            "name": "API Support",
            "url": "http://www.example.com/support",
            "email": "support@example.com",
        },
        "license": {  # License information.
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        "version": "1.0.0",  # Version of your API.
    }
}
