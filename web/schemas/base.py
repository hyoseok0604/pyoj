from pydantic import BaseModel as Schema
from pydantic import ConfigDict


class BaseSchema(Schema):
    model_config = ConfigDict(arbitrary_types_allowed=True)
