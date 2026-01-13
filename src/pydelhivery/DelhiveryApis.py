from uuid import UUID
import dotenv
import os
import requests
from typing import Optional, Dict, Any
from pydelhivery import logger
from pydantic import BaseModel

from pydelhivery.models.DelhiveryModels import (
    DelhiveryInvoiceChargeItem,
    DelhiveryOrderTrackingRequest,
    DelhiveryOrderUpdateRequest,
    DelhiveryPackageEditRequest,
    DelhiveryPackingSlipRequest,
    DelhiveryPackingSlipResponse,
    DelhiveryPickupRequest,
    DelhiveryPickupSuccessResponse,
    DelhiveryPincodeResponse,
    DelhiveryShippingCostRequest,
    ShipmentConfig,
)
from pydelhivery.models.DelhiveryModels import (
    DelhiveryCMUCreateRequest,
    DelhiveryCMUCreateResponse,
    DelhiveryPickupLocation,
    DelhiveryShipment,
)
from pydelhivery.models.DelhiveryModels import (
    DelhiveryTrackingResponse,
)

from typing import Optional
from pydelhivery.models.ShippingCreateRequest import AddressData
from pydelhivery.models.WareHouseModels import (
    DelhiveryWarehouseCreateRequest,
    DelhiveryWarehouseUpdateRequest,
)


class DelhiveryIntegration:
    def __init__(self):
        dotenv.load_dotenv()
        self.auth_token = os.getenv("DELHIVERY_AUTH_TOKEN")
        # Make base URL configurable via environment variable, default to production
        self.base_url = os.getenv(
            "DELHIVERY_API_BASE_URL",
            "https://track.delhivery.com",
        )

    def _parse_response(self, response: requests.Response, pydantic_model: BaseModel):
        """
        Accept ONLY the known-success pickup response.
        Raise HTTPError with debug logs for anything else.
        """

        try:
            payload = response.json()
        except Exception:
            logger.debug(
                "Pickup response not JSON | status=%s | body=%s",
                response.status_code,
                response.text,
            )
            raise requests.exceptions.HTTPError(
                "Delhivery pickup response is not valid JSON",
                response=response,
            )

        try:
            parsed = pydantic_model.model_validate(payload)
            return parsed

        except Exception as exc:
            logger.debug(
                "Unexpected response from Delhivery | status=%s | payload=%s",
                response.status_code,
                payload,
                exc_info=True,
            )

            raise requests.exceptions.HTTPError(
                f"Unexpected Delhivery pickup response: {payload}",
                response=response,
            ) from exc

    def _get_headers(self) -> Dict[str, str]:
        if not self.auth_token:
            raise ValueError(
                "DELHIVERY_AUTH_TOKEN is not configured in environment variables"
            )
        return {
            "Authorization": f"Token {self.auth_token}",
            "Content-Type": "application/json",
        }

    def check_pincode_serviceability(
        self, pincode: str, filter_codes: Optional[str] = None
    ) -> DelhiveryPincodeResponse:
        """
        Check if a pincode is serviceable for delivery using Delhivery API.

        Args:
            pincode: The pincode to check serviceability for
            filter_codes: Optional filter parameter. If not provided, uses pincode

        Returns:
            Dictionary containing the API response with serviceability information

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If auth_token is not configured
        """
        if not self.auth_token:
            raise ValueError(
                "DELHIVERY_AUTH_TOKEN is not configured in environment variables"
            )

        # Use pincode as filter_codes if not provided
        filter_value = filter_codes if filter_codes is not None else pincode

        # Construct the API endpoint
        url = f"{self.base_url}/c/api/pin-codes/json/"
        params = {"filter_codes": filter_value}

        # Set up headers with authentication
        headers = self._get_headers()

        try:
            logger.info(f"Checking pincode serviceability for pincode: {pincode}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            parsed = self._parse_response(response, DelhiveryPincodeResponse)

            if not parsed.is_serviceable:
                raise ValueError("Pincode not serviceable")

            pc = parsed.postal_code

            logger.info(
                "Pincode=%s | City=%s | COD=%s | Prepaid=%s | ODA=%s",
                pc.pin,
                pc.city,
                parsed.supports_cod,
                parsed.supports_prepaid,
                parsed.is_oda,
            )
            logger.info(
                f"Pincode serviceability check successful for pincode: {pincode}"
            )
            return parsed

        except requests.exceptions.HTTPError as e:
            response_text = (
                e.response.text if e.response is not None else "No response available"
            )
            logger.error(
                f"HTTP error checking pincode serviceability: {e}, Response: {response_text}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error checking pincode serviceability: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking pincode serviceability: {e}")
            raise

    def create_warehouse(
        self,
        warehouse: DelhiveryWarehouseCreateRequest,
    ) -> bool:
        """
        Create a warehouse in Delhivery B2C system.

        Args:
            warehouse: Validated warehouse payload (Pydantic model)

        Returns:
            API response dict

        Raises:
            ValueError: If auth token missing
            requests.exceptions.RequestException: API failures
        """

        if not self.auth_token:
            raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")

        url = f"{self.base_url}/api/backend/clientwarehouse/create/"

        headers = self._get_headers()

        payload = warehouse.model_dump()

        try:
            logger.info(f"Creating Delhivery warehouse: {warehouse.name}")
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()

            logger.info("Warehouse creation successful")
            return True

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Delhivery warehouse creation failed | "
                f"Status: {e.response.status_code} | "
                f"Response: {e.response.text}"
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error creating warehouse: {e}")
            raise

    def update_warehouse(
        self, warehouse_update: DelhiveryWarehouseUpdateRequest
    ) -> bool:
        """
        Update an existing warehouse in Delhivery B2C system.

        Args:
            warehouse_update: Validated update payload

        Returns:
            API response dict
        """

        if not self.auth_token:
            raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")

        url = f"{self.base_url}/api/backend/clientwarehouse/edit/"

        headers = self._get_headers()

        # Exclude None values so only provided fields are updated
        payload = warehouse_update.model_dump(exclude_none=True)

        try:
            logger.info(f"Updating Delhivery warehouse: {warehouse_update.name}")

            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()

            logger.info("Warehouse update successful")
            return True

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Delhivery warehouse update failed | "
                f"Status: {e.response.status_code} | "
                f"Response: {e.response.text}"
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error updating warehouse: {e}")
            raise

    def calculate_shipping_cost(
        self, request_data: DelhiveryShippingCostRequest
    ) -> DelhiveryInvoiceChargeItem:
        """
        Calculate shipping cost using Delhivery B2C API.

        Args:
            request_data: Validated shipping cost request payload

        Returns:
            API response dict
        """

        if not self.auth_token:
            raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")

        url = f"{self.base_url}/api/kinko/v1/invoice/charges/"

        headers = self._get_headers()

        params = request_data.model_dump()

        try:
            logger.info(
                f"Calculating shipping cost "
                f"{params['o_pin']} -> {params['d_pin']} | "
                f"Weight: {params['cgm']}g"
            )

            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()

            logger.info("Shipping cost calculation successful")
            logger.debug(f"Shipping cost response: {response.text}")
            responseObj = DelhiveryInvoiceChargeItem.from_xml(response.text)
            return responseObj

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Shipping cost calculation failed | "
                f"Status: {e.response.status_code} | "
                f"Response: {e.response.text}"
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error calculating shipping cost: {e}")
            raise

    def create_order(
        self, shipment_config: ShipmentConfig, order_id: UUID
    ) -> DelhiveryCMUCreateResponse:
        """
        Create a B2C order in Delhivery.

        Args:
            order_data: Validated order payload

        Returns:
            API response dict
        """

        if not self.auth_token:
            raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")

        url = f"{self.base_url}/api/cmu/create.json"
        logger.info(f"Creating Delhivery order")

        shipping_address: AddressData
        shipment_request_obj = DelhiveryCMUCreateRequest(
            shipments=[
                DelhiveryShipment(
                    name=shipping_address.fullName,
                    add=shipping_address.streetAddress,
                    pin=str(shipping_address.pincode),
                    city=shipping_address.city,
                    state=shipping_address.state,
                    phone=shipping_address.phone,
                    order=str(order_id),
                    payment_mode=shipment_config.payment_mode,
                    shipping_mode=shipment_config.shipping_mode,
                    shipment_width=str(shipment_config.shipment_width),
                    shipment_height=str(shipment_config.shipment_height),
                )
            ],
            pickup_location=DelhiveryPickupLocation(name=shipment_config.warehouse),
        )

        headers = self._get_headers()
        payload = shipment_request_obj.build_payload()

        try:
            logger.info(
                f"Creating Delhivery order: {shipment_request_obj.shipments[0].order}"
            )

            response = requests.post(url, headers=headers, data=payload, timeout=20)
            response.raise_for_status()

            logger.info("Order creation successful")
            logger.debug(f"Order creation response: {response.text}")

            deliveryResponse = self._parse_response(
                response, DelhiveryCMUCreateResponse
            )
            deliveryResponse.raise_for_failure(response)

            return deliveryResponse

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Order creation failed | "
                f"Status: {e.response.status_code} | "
                f"Response: {e.response.text}"
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error creating order: {e}")
            raise

    def update_order(self, order_update: DelhiveryOrderUpdateRequest) -> Dict[str, Any]:
        """
        Update an existing order in Delhivery B2C.

        Args:
            order_update: Validated update payload

        Returns:
            API response dict
        """

        if not self.auth_token:
            raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")

        url = f"{self.base_url}/api/cmu/update.json"

        headers = self._get_headers()

        payload = {"shipments": [order_update.model_dump(exclude_none=True)]}

        try:
            logger.info(f"Updating Delhivery order: {order_update.order}")

            response = requests.post(url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()

            logger.info("Order update successful")
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Order update failed | "
                f"Status: {e.response.status_code} | "
                f"Response: {e.response.text}"
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error updating order: {e}")
            raise

    def schedule_pickup(
        self, pickup_request: DelhiveryPickupRequest
    ) -> DelhiveryPickupSuccessResponse:
        """
        Schedule a pickup with Delhivery B2C.

        Args:
            pickup_request: Validated pickup payload

        Returns:
            API response dict
        """

        if not self.auth_token:
            raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")

        url = f"{self.base_url}/fm/request/new/"
        headers = self._get_headers()
        payload = pickup_request.model_dump(exclude_none=True)

        try:
            logger.info(
                f"Scheduling pickup for {pickup_request.pickup_date} | "
                f"{pickup_request.pickup_location}"
            )

            response = requests.post(url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()

            logger.info("Pickup scheduled successfully")
            parsed = self._parse_response(response, DelhiveryPickupSuccessResponse)
            return parsed

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Pickup scheduling failed | "
                f"Status: {e.response.status_code} | "
                f"Response: {e.response.text}"
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error scheduling pickup: {e}")
            raise

    def generate_shipping_label(
        self, label_request: DelhiveryPackingSlipRequest
    ) -> DelhiveryPackingSlipResponse:
        """
        Generate packing slip / shipping label for a waybill.
        """

        if not self.auth_token:
            raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")

        url = f"{self.base_url}/api/p/packing_slip"
        headers = self._get_headers()

        params = label_request.build_params()

        try:
            logger.info(
                "Generating packing slip | waybill=%s | pdf=%s | pdf_size=%s",
                label_request.waybill,
                label_request.pdf,
                label_request.pdf_size,
            )

            response = requests.get(
                url,
                headers=headers,
                params=params,  # ✅ QUERY PARAMS
                timeout=20,
            )
            response.raise_for_status()

            logger.info("Packing slip generated successfully")
            parsed = self._parse_response(response, DelhiveryPackingSlipResponse)
            if parsed.packages_found == 0:
                raise requests.exceptions.HTTPError(
                    "No packages found for packing slip",
                    response=response,
                )

            logger.info(
                "Packing slip generated | waybills=%s | pdf_links=%s",
                parsed.waybills,
                parsed.pdf_links,
            )

            return parsed

        except requests.exceptions.HTTPError as e:
            logger.error(
                "Packing slip generation failed | Status=%s | Response=%s",
                e.response.status_code,
                e.response.text,
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error generating packing slip: {e}")
            raise

    def track_orders(
        self, tracking_request: DelhiveryOrderTrackingRequest
    ) -> DelhiveryTrackingResponse:
        """
        Track one or more orders via Delhivery B2C Tracking API.

        Args:
            tracking_request: Validated tracking request payload

        Returns:
            JSON response with tracking details
        """

        if not self.auth_token:
            raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")

        url = f"{self.base_url}/api/v1/packages/json/"
        headers = self._get_headers()

        payload = tracking_request.build_params()
        try:
            logger.info(f"Tracking waybills: {tracking_request.waybills}")

            response = requests.get(url, headers=headers, params=payload, timeout=20)
            response.raise_for_status()

            logger.info("Order tracking successful")

            parsed = self._parse_response(response, DelhiveryTrackingResponse)
            shipment = parsed.first_shipment

            logger.info(
                "Waybill=%s | Status=%s | Location=%s",
                shipment.AWB if shipment else None,
                parsed.latest_status,
                parsed.latest_status_location,
            )

            return parsed

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Order tracking failed | "
                f"Status: {e.response.status_code} | "
                f"Response: {e.response.text}"
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error tracking orders: {e}")
            raise

    def cancelShipment(self, waybill: str):
        payload = DelhiveryPackageEditRequest(
            waybill=waybill,
            cancellation="true",
        )
        response = requests.post(
            f"{self.base_url}/api/p/edit",
            headers=self._get_headers(),
            json=payload.model_dump(),
            timeout=15,
        )
        response.raise_for_status()


def delhivery_client(request: requests.Request) -> DelhiveryIntegration:
    return request.app.state.delhivery
