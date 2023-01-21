"""Setup the Microdot server in asyncio mode."""
from microdot import Request

from .base import server
from .signals import API_SCHEMA as SIGNALS_API_SCHEMA, add_signal
from .system import API_SCHEMA as SYSTEM_API_SCHEMA


@server.get('/')
async def get_openapi_explorer(request: Request):  # noqa: ANN201
    """Return the OpenAPI Explorer UI."""
    return """<!doctype html>
<html>
  <head>
    <meta charset="UTF-8"/>
    <title>Satellite Microcontroller API Documentation</title>
    <script type="module" src="https://unpkg.com/openapi-explorer@0/dist/browser/openapi-explorer.min.js"></script>
  </head>
  <body>
    <openapi-explorer spec-url="/api/schema"> </openapi-explorer>
  </body>
</html>
""", 200, {'Content-Type': 'text/html; charset=UTF-8'}


@server.get('/api/schema')
async def get_schema(request: Request) -> dict:
    """Return the OpenAPI schema document."""
    schema = {
        'version': '3.1',
        'info': {
            'title': 'Satellite MC',
            'version': '0.1.0'
        },
        'components': {
            'schemas': {}
        },
        'paths': {
            '/': {
                'get': {
                    'summary': 'User: API Documentation',
                    'description': 'Access this API console'
                }
            },
            '/api/schema': {
                'get': {
                    'summary': 'Schema: Definition',
                    'description': 'Fetch the OpenAPI schema document for this API'
                }
            }
        }
    }
    schema['components']['schemas'].update(SIGNALS_API_SCHEMA['schemas'])
    schema['paths'].update(SIGNALS_API_SCHEMA['paths'])
    schema['paths'].update(SYSTEM_API_SCHEMA['paths'])
    return schema


def start_server() -> None:
    """Run the server, initialising the signals."""
    add_signal({
        'type': 'GermanHauptsignal',
        'id': '1',
        'params': {
            'red_pin': 0,
            'green_pin': 1,
        }
    })
    server.run(port=80)
