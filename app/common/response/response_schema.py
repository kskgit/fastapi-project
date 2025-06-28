from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from app.common.response.response_code import CustomResponseCode

SchemaT = TypeVar("SchemaT")


class ResponseModel(BaseModel):
    """
    Generic unified return model without a return data schema
    """

    code: int = Field(
        CustomResponseCode.HTTP_200.code, description="Return status code"
    )
    msg: str = Field(
        CustomResponseCode.HTTP_200.message, description="Return information"
    )
    data: Any | None = Field(None, description="Return data")


class ResponseSchemaModel(ResponseModel, Generic[SchemaT]):
    """
    Generic unified return model containing a return data schema
    """

    data: SchemaT


class ResponseBase:
    """Unified return method"""

    def success_empty(
        self,
        *,
        res: CustomResponseCode = CustomResponseCode.HTTP_200,
    ) -> ResponseModel:
        """
        Successful response

        :param res: Return information
        :param data: Return data
        :param schema: Return data model
        :return:
        """
        return ResponseModel(code=res.code, msg=res.message, data=None)

    def success_schema(
        self,
        *,
        res: CustomResponseCode = CustomResponseCode.HTTP_200,
        data: Any | None = None,
        schema: Any,
    ) -> ResponseSchemaModel:
        """
        Successful response

        :param res: Return information
        :param data: Return data
        :param schema: Return data model
        :return:
        """
        return ResponseSchemaModel[schema](code=res.code, msg=res.message, data=data)

    def fail(
        self,
        *,
        res: CustomResponseCode,
        data: Any = None,
    ) -> ResponseModel | ResponseSchemaModel:
        """
        Failed response

        :param res: Return information
        :param data: Return data
        :return:
        """
        return ResponseModel(code=res.code, msg=res.message, data=data)


response_base: ResponseBase = ResponseBase()
