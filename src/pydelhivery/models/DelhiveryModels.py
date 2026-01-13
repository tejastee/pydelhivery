from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)
from typing import Any, List, Literal, Optional


class DelhiveryShippingCostRequest(BaseModel):
    md: Literal["E", "S"] = Field(
        ..., description="Billing mode: E = Express, S = Surface"
    )
    cgm: int = Field(..., ge=0, description="Chargeable weight in grams")
    o_pin: int = Field(..., description="Origin pincode (6-digit)")
    d_pin: int = Field(..., description="Destination pincode (6-digit)")
    ss: Literal["Delivered", "RTO", "DTO"] = Field(..., description="Shipment status")
    pt: Literal["Pre-paid", "COD"] = Field(..., description="Payment type")

    @field_validator("o_pin", "d_pin")
    @classmethod
    def validate_pin(cls, v: int):
        if not (100000 <= v <= 999999):
            raise ValueError("Pincode must be a valid 6-digit number")
        return v


class DelhiveryOrderItem(BaseModel):
    name: str
    sku: str
    units: int
    selling_price: float


class DelhiveryOrderUpdateRequest(BaseModel):
    order: str = Field(..., description="Merchant order ID to update")
    waybill: Optional[str] = None

    # Optional fields you might want to update
    total_amount: Optional[float] = None
    shipping_mode: Optional[Literal["Surface", "Express"]] = None
    payment_mode: Optional[Literal["Prepaid", "COD"]] = None

    # Delivery address updates
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pin: Optional[str] = None

    # Return address updates
    return_pin: Optional[str] = None
    return_city: Optional[str] = None
    return_phone: Optional[str] = None
    return_address: Optional[str] = None
    return_state: Optional[str] = None
    return_country: Optional[str] = None

    # Items might be updateable partially (if supported)
    order_items: Optional[List[DelhiveryOrderItem]] = None


class DelhiveryPickupRequest(BaseModel):
    pickup_time: str = Field(
        ...,
        pattern=r"^\d{2}:\d{2}:\d{2}$",
        description="Pickup time (HH:MM:SS)",
        examples=["11:00:00"],
    )
    pickup_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Pickup date (YYYY-MM-DD)",
        examples=["2023-12-29"],
    )
    pickup_location: str = Field(
        ...,
        description="Registered client warehouse / pickup location",
    )
    expected_package_count: int = Field(
        ...,
        ge=1,
        description="Expected number of packages for pickup",
    )


class DelhiveryPickupSuccessResponse(BaseModel):
    pickup_location_name: str
    client_name: str
    pickup_time: str = Field(..., pattern=r"^\d{2}:\d{2}:\d{2}$")
    pickup_id: int
    incoming_center_name: str
    expected_package_count: int
    pickup_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")

    # 🔒 Reject unknown / extra fields
    model_config = ConfigDict(extra="forbid")


class DelhiveryPackingSlipRequest(BaseModel):
    waybill: str = Field(..., description="Waybill number of the shipment")
    pdf: Optional[bool] = Field(
        False,
        description=(
            "If True: returns S3 PDF link (non-customizable). "
            "If False: returns JSON response."
        ),
    )
    pdf_size: Optional[Literal["A4", "4R"]] = Field(
        None,
        description="PDF size: A4 (8x11) or 4R (4x6)",
    )

    def build_params(self) -> dict:
        params: dict[str, str] = {
            "wbns": self.waybill,
        }

        if self.pdf is not None:
            # Delhivery accepts boolean-style query params
            params["pdf"] = str(self.pdf).lower()  # true / false

        if self.pdf_size:
            params["pdf_size"] = self.pdf_size

        return params


class DelhiveryPackingSlipPackage(BaseModel):
    wbn: str = Field(..., description="Waybill number")
    pdf_download_link: Optional[str] = Field(
        None,
        description="S3 PDF download link (present when pdf=true)",
    )


class DelhiveryPackingSlipResponse(BaseModel):
    packages: List[DelhiveryPackingSlipPackage] = Field(default_factory=list)
    packages_found: int = 0

    @property
    def waybills(self) -> list[str]:
        return [pkg.wbn for pkg in self.packages]

    @property
    def pdf_links(self) -> list[str]:
        return [pkg.pdf_download_link for pkg in self.packages if pkg.pdf_download_link]

    @property
    def first_pdf_link(self) -> Optional[str]:
        return self.pdf_links[0] if self.pdf_links else None


class DelhiveryOrderTrackingRequest(BaseModel):
    waybills: Optional[List[str]] = None
    ref_ids: Optional[str] = ""

    def build_params(self) -> dict:
        params: dict[str, str] = {}

        if self.waybills:
            params["waybill"] = ",".join(self.waybills)

        if self.ref_ids is not None:
            params["ref_ids"] = ",".join(self.waybills)
        return params


class DelhiveryPackageEditRequest(BaseModel):
    waybill: str = Field(..., min_length=8, description="Delhivery waybill number")
    cancellation: Literal["true", "false"] = Field(
        "true",
        description="Set to 'true' to cancel shipment",
    )


class DelhiveryPackageEditResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


class DelhiveryCenter(BaseModel):
    code: Optional[str] = None
    cn: Optional[str] = None  # center name
    sort_code: Optional[str] = None
    s: Optional[str] = None  # start datetime
    e: Optional[str] = None  # end datetime
    u: Optional[str] = None  # updated by
    ud: Optional[str] = None  # update datetime


class DelhiveryPostalCode(BaseModel):
    pin: int
    city: Optional[str] = None
    district: Optional[str] = None
    state_code: Optional[str] = None
    country_code: Optional[str] = None

    inc: Optional[str] = None
    sort_code: Optional[str] = None
    remarks: Optional[str] = None

    max_weight: Optional[float] = None
    max_amount: Optional[float] = None

    cod: Optional[str] = None  # Y / N
    pre_paid: Optional[str] = None  # Y / N
    cash: Optional[str] = None  # Y / N
    pickup: Optional[str] = None  # Y / N
    repl: Optional[str] = None  # Y / N

    is_oda: Optional[str] = None  # Y / N
    covid_zone: Optional[str] = None  # G / R / O
    protect_blacklist: Optional[bool] = None
    sun_tat: Optional[bool] = None

    center: List[DelhiveryCenter] = []


class DelhiveryDeliveryCode(BaseModel):
    postal_code: DelhiveryPostalCode


class DelhiveryPincodeResponse(BaseModel):
    delivery_codes: list[DelhiveryDeliveryCode] = []

    # -----------------------
    # Convenience helpers
    # -----------------------

    @property
    def is_serviceable(self) -> bool:
        return bool(self.delivery_codes)

    @property
    def postal_code(self) -> Optional[DelhiveryPostalCode]:
        if not self.delivery_codes:
            return None
        return self.delivery_codes[0].postal_code

    @property
    def supports_cod(self) -> bool:
        pc = self.postal_code
        return pc.cod == "Y" if pc else False

    @property
    def supports_prepaid(self) -> bool:
        pc = self.postal_code
        return pc.pre_paid == "Y" if pc else False

    @property
    def is_oda(self) -> bool:
        pc = self.postal_code
        return pc.is_oda == "Y" if pc else False


class ShipmentConfig(BaseModel):
    payment_mode: Literal["Prepaid", "COD"] = Field(
        default="Prepaid", description="Payment mode for the shipment"
    )
    shipping_mode: Literal["Surface", "Express"] = Field(
        default="Surface", description="Shipping mode"
    )
    shipment_width: int = Field(default=100, gt=0, description="Shipment width in cm")
    shipment_height: int = Field(default=100, gt=0, description="Shipment height in cm")
    warehouse: str = Field(
        ..., min_length=1, description="Warehouse identifier or name"
    )
