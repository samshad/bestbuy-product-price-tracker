from flask import Response, jsonify
from typing import Dict, Any


class APIResponse:
    """API response builder."""

    @staticmethod
    def build(status_code: int, body: Dict[str, Any]) -> Response:
        """
        Build a standardized API response.

        Parameters:
            status_code (int): HTTP status code.
            body (Dict[str, Any]): JSON-serializable dictionary to include in the response body.

        Returns:
            Response: A Flask Response object with JSON content.
        """
        # Use Flask's jsonify for correct content-type and formatting
        response = jsonify(body)
        response.status_code = status_code
        return response
