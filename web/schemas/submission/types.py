from typing import Annotated

from pydantic import AfterValidator, Field

from web.schemas.submission.validator import validate_code

Code = Annotated[str, Field(), AfterValidator(validate_code)]
