class HindsightException(Exception):
    """Base exception for Hindsight Cloud memory service errors."""
    pass


class HindsightNotConfiguredError(HindsightException):
    """Raised when Hindsight API key or URL is not configured."""
    pass


class HindsightConnectionError(HindsightException):
    """Raised when connection to Hindsight Cloud fails."""
    pass


class HindsightAPIError(HindsightException):
    """Raised when Hindsight API returns an error status."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Hindsight Cloud Error ({status_code}): {detail}")
