from typing import Optional
from pydantic import BaseModel, model_validator

from models import RoleLevel


class BaseModelHideable(BaseModel):
    hidden: bool = False
    hidden_by_parent: bool = False
    access_level: RoleLevel = RoleLevel.user

    @model_validator(mode="after")
    def set_fields_to_null_if_hidden(self):
        hidden = self.hidden or self.hidden_by_parent
        
        if not self.access_level :
            self.access_level = RoleLevel.user
        
        if not hidden or (self.access_level != None and self.access_level.value > RoleLevel.user.value):
            return self

        for field in self.model_fields_set:
            if field in ("hidden", "access_level", "id", "hidden_by_parent") or "_id" in field:
                continue
            self.__dict__[field] = None

        return self
