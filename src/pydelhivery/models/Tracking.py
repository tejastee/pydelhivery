from pydantic import BaseModel
from typing import Optional, List, Any


# --------------------------------------------------
# Scan Models
# --------------------------------------------------


class DelhiveryScanDetail(BaseModel):
    ScanDateTime: Optional[str] = None
    ScanType: Optional[str] = None
    Scan: Optional[str] = None
    StatusDateTime: Optional[str] = None
    ScannedLocation: Optional[str] = None
    StatusCode: Optional[str] = None
    Instructions: Optional[str] = None


class DelhiveryScan(BaseModel):
    ScanDetail: Optional[DelhiveryScanDetail] = None


# --------------------------------------------------
# Status Model
# --------------------------------------------------


class DelhiveryShipmentStatus(BaseModel):
    Status: Optional[str] = None
    StatusLocation: Optional[str] = None
    StatusDateTime: Optional[str] = None
    RecievedBy: Optional[str] = None
    StatusCode: Optional[str] = None
    StatusType: Optional[str] = None
    Instructions: Optional[str] = None


# --------------------------------------------------
# Consignee Model
# --------------------------------------------------


class DelhiveryConsignee(BaseModel):
    City: Optional[str] = None
    Name: Optional[str] = None
    Address1: List[Any] = []
    Address2: List[Any] = []
    Address3: Optional[str] = None
    PinCode: Optional[int] = None
    State: Optional[str] = None
    Telephone1: Optional[str] = None
    Telephone2: Optional[str] = None
    Country: Optional[str] = None


# --------------------------------------------------
# Shipment Model
# --------------------------------------------------


class DelhiveryShipmentTracker(BaseModel):
    AWB: Optional[str] = None
    ReferenceNo: Optional[str] = None
    OrderType: Optional[str] = None

    PickUpDate: Optional[str] = None
    PickedupDate: Optional[str] = None
    DeliveryDate: Optional[str] = None
    ReturnedDate: Optional[str] = None
    FirstAttemptDate: Optional[str] = None

    ExpectedDeliveryDate: Optional[str] = None
    PromisedDeliveryDate: Optional[str] = None
    ReturnPromisedDeliveryDate: Optional[str] = None
    RTOStartedDate: Optional[str] = None

    Origin: Optional[str] = None
    Destination: Optional[str] = None
    PickupLocation: Optional[str] = None

    OriginRecieveDate: Optional[str] = None
    DestRecieveDate: Optional[str] = None
    OutDestinationDate: Optional[str] = None

    SenderName: Optional[str] = None
    Quantity: Optional[str] = None
    DispatchCount: Optional[int] = None

    CODAmount: Optional[float] = None
    InvoiceAmount: Optional[float] = None
    ChargedWeight: Optional[float] = None

    ReverseInTransit: Optional[bool] = None
    Extras: Optional[str] = None

    Status: Optional[DelhiveryShipmentStatus] = None
    Scans: List[DelhiveryScan] = []
    Consignee: Optional[DelhiveryConsignee] = None
    Ewaybill: List[Any] = []


# --------------------------------------------------
# Wrapper Models
# --------------------------------------------------


class DelhiveryShipmentWrapper(BaseModel):
    Shipment: Optional[DelhiveryShipmentTracker] = None


class DelhiveryTrackingResponse(BaseModel):
    ShipmentData: List[DelhiveryShipmentWrapper] = []

    # --------------------------------------------------
    # Convenience helpers
    # --------------------------------------------------

    @property
    def shipments(self) -> list[DelhiveryShipmentTracker]:
        return [
            wrapper.Shipment
            for wrapper in self.ShipmentData
            if wrapper.Shipment is not None
        ]

    @property
    def first_shipment(self) -> Optional[DelhiveryShipmentTracker]:
        shipments = self.shipments
        return shipments[0] if shipments else None

    @property
    def latest_status(self) -> Optional[str]:
        shipment = self.first_shipment
        if shipment and shipment.Status:
            return shipment.Status.Status
        return None

    @property
    def latest_status_location(self) -> Optional[str]:
        shipment = self.first_shipment
        if shipment and shipment.Status:
            return shipment.Status.StatusLocation
        return None

    @property
    def latest_scan(self) -> Optional[DelhiveryScanDetail]:
        shipment = self.first_shipment
        if shipment and shipment.Scans:
            return shipment.Scans[-1].ScanDetail
        return None

    @property
    def is_delivered(self) -> bool:
        return self.latest_status == "Delivered"

    @property
    def is_rto(self) -> bool:
        shipment = self.first_shipment
        return bool(shipment and shipment.RTOStartedDate)
