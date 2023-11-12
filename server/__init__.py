"""Setup the Microdot server in asyncio mode."""
from microdot import Request

from .base import server
from .signals import API_SCHEMA as SIGNALS_API_SCHEMA, shutdown as signals_shutdown
from .system import API_SCHEMA as SYSTEM_API_SCHEMA
from .turnouts import API_SCHEMA as TURNOUTS_API_SCHEMA, shutdown as turnouts_shutdown


@server.get('/')
async def get_openapi_explorer(request: Request):  # noqa: ANN201
    """Return the OpenAPI Explorer UI."""
    return """<!doctype html>
<html>
  <head>
    <meta charset="UTF-8"/>
    <title>Model Railway Thin Controller API Documentation</title>
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
            'title': 'Model Railway Thin Controller',
            'version': '0.2.0'
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
    schema['components']['schemas'].update(TURNOUTS_API_SCHEMA['schemas'])
    schema['paths'].update(SIGNALS_API_SCHEMA['paths'])
    schema['paths'].update(SYSTEM_API_SCHEMA['paths'])
    schema['paths'].update(TURNOUTS_API_SCHEMA['paths'])
    return schema


def start_server() -> None:
    """Run the server."""
    server.run(port=80)


def shutdown_server() -> None:
    """Shut down the server."""
    signals_shutdown()
    turnouts_shutdown()
