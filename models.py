from pydantic import BaseModel, HttpUrl,field_validator
from typing import Optional
import re

class Urls(BaseModel):
    city_name:str
    url:str

class Outlet(BaseModel):
    OutletName: str
    area:str
    address:   str
    city: Optional[str]=None
    DeliveryTime:str
    Cost:str
    Status:str
    goodFor:str
    phone: str
    timing:  str
    pincode: Optional[int]=None
    StoreUrl :str
    menuUrl:   str

    @field_validator("pincode", mode="before")
    @classmethod
    def parse_pincode(cls, v):
        if not v:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    @field_validator("StoreUrl", "menuUrl", mode="before")
    @classmethod
    def check_urls(cls, v):
        if not v or not str(v).startswith("http"):
            return None
        return v