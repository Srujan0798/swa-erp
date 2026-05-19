from fastapi import HTTPException, status


class ClientError(HTTPException):
    def __init__(self, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


class ServerError(HTTPException):
    def __init__(self, detail: str = "Internal server error") -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class IntegrationError(HTTPException):
    def __init__(self, detail: str = "External service error") -> None:
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
