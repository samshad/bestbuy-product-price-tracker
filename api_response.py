import json
from typing import Dict, Any


class APIResponse:
    """API response builder."""

    @staticmethod
    def build(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
        """Build standardized API response."""
        return {
            'statusCode': status_code,
            'body': json.dumps(body)
        }
