from enum import Enum


class CustomResponseCode(Enum):
    HTTP_200 = (200, "OK")
    HTTP_201 = (201, "Created")
    HTTP_400 = (400, "Bad Request")
    HTTP_401 = (401, "Unauthorized")
    HTTP_403 = (403, "Forbidden")
    HTTP_404 = (404, "Not Found")
    HTTP_500 = (500, "Internal Server Error")
    HTTP_502 = (502, "Bad Gateway")
    HTTP_503 = (503, "Service Unavailable")
    HTTP_504 = (504, "Gateway Timeout")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]
