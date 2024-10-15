from example.controllers import UserController
from example.controllers import MessageController
from example.controllers import HealthController

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
