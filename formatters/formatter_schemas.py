#!/usr/bin/env python3

schema = {
    "api/dockers/create": {
        "post": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "userId": {"type": "string"},
                "modelName": {"type": "string"}
            },
            "required": ["id", "userId", "modelName"]
        }
    }
}
