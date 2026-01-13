from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class DelhiveryWarehouseCreateRequest(BaseModel):
    name: str = Field(..., description="Warehouse name")
    registered_name: str = Field(..., description="Registered business name")

    address: str = Field(..., description="Primary address")
    city: str = Field(..., description="City")
    pin: str = Field(..., min_length=6, max_length=6, description="Pincode")

    phone: str = Field(
        ..., min_length=10, max_length=10, description="Contact phone number"
    )
    email: EmailStr

    country: str = Field(default="India", description="Country")

    # Return address details
    return_address: str = Field(..., description="Return address")
    return_city: str = Field(..., description="Return city")
    return_state: str = Field(..., description="Return state")
    return_pin: str = Field(
        ..., min_length=6, max_length=6, description="Return pincode"
    )
    return_country: str = Field(default="India", description="Return country")


class DelhiveryWarehouseUpdateRequest(BaseModel):
    name: str = Field(..., description="Registered warehouse name")
    phone: str = Field(..., description="Contact phone number")
    address: str = Field(..., description="Full warehouse address")
