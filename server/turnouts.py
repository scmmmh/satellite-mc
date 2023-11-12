"""Turnout control API endpoints."""
from machine import Pin
from microdot import Request
from time import sleep

from .base import server


API_SCHEMA = {
    "schemas": {
        "CreateTurnout": {
            "type": "object",
            "properties": {
                "type": {"type": "String"},
                "params": {
                    "type": "object",
                    "id": {"type": "string"},
                    "properties": {"^S_": {"type": "string"}},
                },
            },
        },
        "Turnout": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "type": {"type": "string"},
                "params": {"type": "object", "properties": {"^S_": {"type": "string"}}},
                "state": {"type": "string"},
            },
        },
    },
    "paths": {
        "/api/turnouts": {
            "get": {
                "summary": "Turnouts: List all",
                "description": "List all configured turnouts.",
                "responses": {
                    "200": {
                        "description": "A list of all available turnouts.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Turnout"},
                                }
                            }
                        },
                    }
                },
            },
            "post": {
                "summary": "Turnouts: Create",
                "description": "Create a new turnout.",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateTurnout"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "The newly created turnout.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Turnout"}
                            }
                        },
                    }
                },
            },
        },
        "/api/turnouts/{tid}": {
            "summary": "Single turnout API endpoints",
            "parameters": [
                {
                    "name": "tid",
                    "in": "path",
                    "description": "The identifier of the turnout to set",
                    "required": True,
                    "schema": {"type": "string"},
                    "style": "simple",
                }
            ],
            "get": {
                "summary": "Turnouts: Get state",
                "description": "Get the turnout identified by the identifier",
                "responses": {
                    "200": {
                        "description": "The requested turnout object",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Turnout"}
                            }
                        },
                    },
                    "404": {
                        "description": "No turnout exists for the given identifier",
                    },
                },
            },
            "patch": {
                "summary": "Turnouts: Set state",
                "description": "Set the turnout to the required state.",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "state": {
                                        "description": "The turnout state to set",
                                        "type": "string",
                                    }
                                },
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Returns the updated turnout state.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Turnout"}
                            }
                        },
                    },
                    "400": {"description": "The requested state is not valid"},
                    "404": {
                        "description": "The id does not identify an existing turnout"
                    },
                },
            },
            "delete": {
                "summary": "Turnouts: Delete",
                "description": "Delete the specified turnout.",
                "responses": {
                    "200": {"description": "The turnout has been deleted."},
                    "404": {
                        "description": "The id does not identify an existing turnout"
                    },
                },
            },
        },
    },
}


class TwoPinSolenoidTurnout:
    """A Two-Pin Solenoid Turnout.

    The two pins are:

    * **enable_pin** - The pin to turn on power to the solenoid
    * **direction_pin** - The pin to control the electricity flow direction

    Additionally the parameter **turnout_high** Determines whether the
    "turn" position is achieved by driving the **direction_pin** high or
    low.

    Supports the following states:

    * **off**: Undetermined state
    * **straight**: Turnout set to straight ahead
    * **turn**: Turnout set to turn
    """

    def __init__(self: "TwoPinSolenoidTurnout", config: dict) -> None:
        """Initialise and set the turnout to 'off'."""
        self._config = config
        self._enable = Pin(self._config["params"]["enable_pin"], Pin.OUT)
        self._direction = Pin(self._config["params"]["direction_pin"], Pin.OUT)
        self._turnout_high = self._config["params"]["turnout_high"]
        self._state = ""
        self.set_turnout({"state": "straight"})
        sleep(0.5)
        self.set_turnout({"state": "turn"})
        sleep(0.5)
        self.set_turnout({"state": "straight"})

    @classmethod
    def validate_create(cls, body: dict) -> bool:  # noqa: ANN001, ANN102
        """Validate that the body is a valid config for this turnout."""
        if body is not None and isinstance(body, dict):
            if "type" in body and body["type"] == "TwoPinSolenoidTurnout":
                if "params" in body and isinstance(body["params"], dict):
                    if (
                        "enable_pin" in body["params"]
                        and "direction_pin" in body["params"]
                        and "turnout_high" in body["params"]
                    ):  # noqa: E501
                        return True
        return False

    def validate_update(self: "TwoPinSolenoidTurnout", body) -> bool:  # noqa: ANN001
        """Validate that the body is a valid instruction for this turnout."""
        if body is not None and isinstance(body, dict):
            if "state" in body and isinstance(body["state"], str):
                if body["state"] in ["off", "straight", "turn"]:
                    return True
        return False

    def set_turnout(self: "TwoPinSolenoidTurnout", body: dict) -> None:
        """Set the turnout to the state specified in the body."""
        if body["state"] == "off":
            self._state = "off"
            self._direction.off()
            self._enable.off()
        elif body["state"] == "straight":
            self._state = "straight"
            self._enable.on()
            sleep(0.01)
            if self._turnout_high:
                self._direction.off()
            else:
                self._direction.on()
            sleep(0.1)
            self._enable.off()
        elif body["state"] == "turn":
            self._state = "turn"
            self._enable.on()
            sleep(0.01)
            if self._turnout_high:
                self._direction.on()
            else:
                self._direction.off()
            sleep(0.1)
            self._enable.off()

    def as_json(self: "TwoPinSolenoidTurnout") -> dict:
        """Return this TwoPinSolenoidTurnout in its JSON representation."""
        return {
            "id": self._config["id"],
            "type": "TwoPinSolenoidTurnout",
            "params": self._config["params"],
            "state": self._state,
        }


turnouts = {}


@server.get("/api/turnouts")
async def get_all_turnouts(request: Request) -> list:
    """Return all configured turnouts."""
    return [turnout.as_json() for turnout in turnouts.values()]


@server.post("/api/turnouts")
async def create_turnout(request: Request):  # noqa: ANN201
    """Create a new turnout."""
    config = request.json
    if config is not None and "type" in config and "id" in config:
        if config["id"] not in turnouts:
            if config["type"] == "TwoPinSolenoidTurnout":
                if TwoPinSolenoidTurnout.validate_create(config):
                    turnouts[config["id"]] = TwoPinSolenoidTurnout(config)
                    return turnouts[config["id"]].as_json()
    return None, 400


@server.get("/api/turnouts/<tid>")
async def get_turnout(request: Request, tid: str):  # noqa: ANN201
    """Get a single turnout."""
    if tid in turnouts:
        return turnouts[tid].as_json()
    return None, 404


@server.patch("/api/turnouts/<tid>")
async def patch_turnout(request: Request, tid: str):  # noqa: ANN201
    """Set a turnout to the given state."""
    if tid in turnouts:
        turnout = turnouts[tid]
        if turnout.validate_update(request.json):
            turnout.set_turnout(request.json)
            return turnout.as_json()
        return None, 400
    return None, 404


@server.delete("/api/turnouts/<tid>")
async def delete_turnout(request: Request, tid: str):  # noqa: ANN201
    """Delete the turnout."""
    if tid in turnouts:
        turnouts[tid].set_turnout({"state": "off"})
        del turnouts[tid]
        return None, 200
    return None, 404


def shutdown() -> None:
    """Shut down all turnouts."""
    for turnout in turnouts.values():
        turnout.set_turnout({"state": "off"})
