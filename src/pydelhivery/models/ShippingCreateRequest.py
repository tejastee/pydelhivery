import json
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from pydelhivery import logger

from pydantic import BaseModel, Field
from typing import List, Literal
import requests
from requests import Response


class AddressData(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    streetAddress: str = Field(..., alias="add")  # Maps 'add' from API if needed
    pincode: int | str
    city: str
    state: str
    phone: str

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v):
        # Ensures pincode is sent as a string to Delhivery but accepts int input
        return str(v)

    @property
    def full_name(self) -> str:
        return f"{self.firstName} {self.lastName}"


class DelhiveryCMUPackage(BaseModel):
    status: Literal["Success", "Fail"]
    client: str
    sort_code: str
    remarks: List[str] = Field(default_factory=list)
    waybill: str
    cod_amount: float
    payment: Literal["Pre-paid", "COD"]
    serviceable: bool
    refnum: str
    sort_code: Optional[str] = None


class DelhiveryCMUCreateResponse(BaseModel):
    success: bool

    upload_wbn: str

    package_count: int
    packages: List[DelhiveryCMUPackage]

    prepaid_count: int
    cod_count: int
    cash_pickups_count: float
    pickups_count: int
    replacement_count: int
    rmk: Optional[str] = None

    cod_amount: float
    cash_pickups: float

    # -----------------------
    # Helpers
    # -----------------------

    @property
    def waybills(self) -> list[str]:
        return [p.waybill for p in self.packages if p.status == "Success"]

    @property
    def failed_packages(self) -> list[DelhiveryCMUPackage]:
        return [p for p in self.packages if p.status != "Success"]

    @property
    def error_messages(self) -> list[str]:
        errors: list[str] = []
        for pkg in self.failed_packages:
            errors.extend(r for r in pkg.remarks if r)
        return errors

    # -----------------------
    # HARD FAILURE HANDLER
    # -----------------------

    def raise_for_failure(self, response: Response) -> None:
        """
        Raise requests.exceptions.HTTPError if CMU creation failed
        or partially failed.
        """

        if self.success and not self.failed_packages:
            return  # fully successful

        error_message = (
            "Delhivery CMU order creation failed | "
            f"upload_wbn={self.upload_wbn} | "
            f"errors={self.error_messages or 'Unknown error'}"
        )

        http_error = requests.exceptions.HTTPError(
            error_message,
            response=response,
        )
        raise http_error


class DelhiveryShipment(BaseModel):
    name: str
    add: str
    pin: str
    city: str
    state: str
    country: str = "India"
    phone: str

    order: str = Field(..., description="Should be equal to order ID that is placed")
    payment_mode: Literal["Prepaid", "COD"]

    return_pin: Optional[str] = ""
    return_city: Optional[str] = ""
    return_phone: Optional[str] = ""
    return_add: Optional[str] = ""
    return_state: Optional[str] = ""
    return_country: Optional[str] = ""

    products_desc: Optional[str] = ""
    hsn_code: Optional[str] = ""
    cod_amount: Optional[str] = ""
    order_date: Optional[str] = None
    total_amount: Optional[str] = ""

    seller_add: Optional[str] = ""
    seller_name: Optional[str] = ""
    seller_inv: Optional[str] = ""
    quantity: Optional[str] = ""

    waybill: Optional[str] = ""

    shipment_width: Optional[str] = ""
    shipment_height: Optional[str] = ""
    weight: Optional[str] = ""

    shipping_mode: Literal["Surface", "Express"]
    address_type: Optional[str] = ""


class DelhiveryPickupLocation(BaseModel):
    name: str


class DelhiveryCMUCreateRequest(BaseModel):
    shipments: List[DelhiveryShipment]
    pickup_location: DelhiveryPickupLocation

    def build_payload(self) -> dict:
        """
        Delhivery CMU requires:
        format=json&data=<json string>
        """
        data = {
            "shipments": [s.model_dump(exclude_none=True) for s in self.shipments],
            "pickup_location": self.pickup_location.model_dump(exclude_none=True),
        }

        data = {
            "format": "json",
            "data": json.dumps(data),
        }
        logger.debug("Delhivery CMU payload: %s", data)
        return data
