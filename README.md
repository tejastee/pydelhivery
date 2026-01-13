# pydelhivery

![PyPI](https://img.shields.io/pypi/v/pydelhivery)

A Python wrapper for Delhivery's B2C API, providing a clean and type-safe interface for integrating with India's largest third-party logistics service provider.

This library is based on the [Delhivery Developer Portal Documentation](https://one.delhivery.com/developer-portal/documents).

> **Note**: This is an independent, open-source project. The author is not affiliated with Delhivery in any way. This project is provided as-is in the hope that others find it helpful for integrating with Delhivery's APIs.

## Features

- ✅ **Pincode Serviceability Check** - Verify if a location is serviceable for delivery
- ✅ **Warehouse Management** - Create and update warehouse configurations
- ✅ **Shipping Cost Calculation** - Calculate shipping charges before creating orders
- ✅ **Order Management** - Create, update, and cancel shipments
- ✅ **Pickup Scheduling** - Schedule pickups for your shipments
- ✅ **Tracking** - Track shipments using waybill numbers
- ✅ **Label Generation** - Generate packing slips and shipping labels
- ✅ **Type-Safe** - Built with Pydantic for robust data validation
- ✅ **Comprehensive Logging** - Built-in logging for debugging and monitoring

## Installation

```bash
pip install pydelhivery
```

Or using `uv`:

```bash
uv add pydelhivery
```

## Configuration

Set up your Delhivery API credentials using environment variables:

```bash
# Required
DELHIVERY_AUTH_TOKEN=your_auth_token_here

# Optional (defaults to https://track.delhivery.com)
DELHIVERY_API_BASE_URL=https://track.delhivery.com
```

You can use a `.env` file in your project root:

```env
DELHIVERY_AUTH_TOKEN=your_auth_token_here
DELHIVERY_API_BASE_URL=https://track.delhivery.com
```

## Quick Start

```python
from pydelhivery import DelhiveryIntegration
from pydelhivery.models.DelhiveryModels import (
    DelhiveryShippingCostRequest,
    DelhiveryOrderTrackingRequest,
)

# Initialize the client
client = DelhiveryIntegration()

# Check pincode serviceability
pincode_response = client.check_pincode_serviceability("560001")
print(f"Serviceable: {pincode_response.is_serviceable}")
print(f"COD Supported: {pincode_response.supports_cod}")

# Calculate shipping cost
cost_request = DelhiveryShippingCostRequest(
    md="E",  # Express
    cgm=500,  # 500 grams
    o_pin=560001,  # Origin pincode
    d_pin=110053,  # Destination pincode
    ss="Delivered",
    pt="Pre-paid"
)
shipping_cost = client.calculate_shipping_cost(cost_request)
print(f"Shipping cost: {shipping_cost.total_amount}")

# Track an order
tracking_request = DelhiveryOrderTrackingRequest(waybills=["WB1234567890"])
tracking_response = client.track_orders(tracking_request)
print(f"Status: {tracking_response.latest_status}")
```

## API Reference

### `DelhiveryIntegration`

The main client class for interacting with Delhivery APIs.

#### Methods

##### `check_pincode_serviceability(pincode: str, filter_codes: Optional[str] = None) -> DelhiveryPincodeResponse`

Check if a pincode is serviceable for delivery.

**Parameters:**
- `pincode` (str): The pincode to check (6-digit)
- `filter_codes` (str, optional): Optional filter parameter

**Returns:** `DelhiveryPincodeResponse` with serviceability information

**Example:**
```python
response = client.check_pincode_serviceability("560001")
if response.is_serviceable:
    print(f"COD: {response.supports_cod}, Prepaid: {response.supports_prepaid}")
```

##### `create_warehouse(warehouse: DelhiveryWarehouseCreateRequest) -> bool`

Create a new warehouse in Delhivery system.

**Parameters:**
- `warehouse`: Warehouse configuration (Pydantic model)

**Returns:** `bool` - True if successful

**Example:**
```python
from pydelhivery.models.WareHouseModels import DelhiveryWarehouseCreateRequest

warehouse = DelhiveryWarehouseCreateRequest(
    name="My Warehouse",
    registered_name="My Company Pvt Ltd",
    address="123 Main Street",
    city="Bangalore",
    pin="560001",
    phone="9876543210",
    email="warehouse@example.com",
    return_address="123 Main Street",
    return_city="Bangalore",
    return_state="Karnataka",
    return_pin="560001"
)
client.create_warehouse(warehouse)
```

##### `update_warehouse(warehouse_update: DelhiveryWarehouseUpdateRequest) -> bool`

Update an existing warehouse configuration.

**Parameters:**
- `warehouse_update`: Warehouse update payload

**Returns:** `bool` - True if successful

##### `calculate_shipping_cost(request_data: DelhiveryShippingCostRequest) -> DelhiveryInvoiceChargeItem`

Calculate shipping cost for a shipment.

**Parameters:**
- `request_data`: Shipping cost request with origin, destination, weight, etc.

**Returns:** `DelhiveryInvoiceChargeItem` with cost breakdown

**Example:**
```python
from pydelhivery.models.DelhiveryModels import DelhiveryShippingCostRequest

request = DelhiveryShippingCostRequest(
    md="E",  # Express or Surface
    cgm=1000,  # Weight in grams
    o_pin=560001,
    d_pin=110053,
    ss="Delivered",  # Status
    pt="Pre-paid"  # Payment type
)
cost = client.calculate_shipping_cost(request)
print(f"Total: {cost.total_amount}")
```

##### `create_order(shipment_config: ShipmentConfig, order_id: UUID) -> DelhiveryCMUCreateResponse`

Create a new shipment order.

**Parameters:**
- `shipment_config`: Shipment configuration
- `order_id`: Unique order identifier (UUID)

**Returns:** `DelhiveryCMUCreateResponse` with waybill numbers

##### `update_order(order_update: DelhiveryOrderUpdateRequest) -> Dict[str, Any]`

Update an existing order.

**Parameters:**
- `order_update`: Order update payload

**Returns:** API response dictionary

##### `schedule_pickup(pickup_request: DelhiveryPickupRequest) -> DelhiveryPickupSuccessResponse`

Schedule a pickup for shipments.

**Parameters:**
- `pickup_request`: Pickup request with date, time, and location

**Returns:** `DelhiveryPickupSuccessResponse` with pickup details

**Example:**
```python
from pydelhivery.models.DelhiveryModels import DelhiveryPickupRequest

pickup = DelhiveryPickupRequest(
    pickup_date="2025-12-31",
    pickup_time="11:00:00",
    pickup_location="My Warehouse",
    expected_package_count=5
)
response = client.schedule_pickup(pickup)
```

##### `generate_shipping_label(label_request: DelhiveryPackingSlipRequest) -> DelhiveryPackingSlipResponse`

Generate packing slip/shipping label for waybills.

**Parameters:**
- `label_request`: Label request with waybill number and format options

**Returns:** `DelhiveryPackingSlipResponse` with PDF links

**Example:**
```python
from pydelhivery.models.DelhiveryModels import DelhiveryPackingSlipRequest

label_request = DelhiveryPackingSlipRequest(
    waybill="WB1234567890",
    pdf=True,
    pdf_size="A4"
)
response = client.generate_shipping_label(label_request)
print(f"PDF URL: {response.pdf_links[0]}")
```

##### `track_orders(tracking_request: DelhiveryOrderTrackingRequest) -> DelhiveryTrackingResponse`

Track one or more shipments.

**Parameters:**
- `tracking_request`: Tracking request with waybill numbers

**Returns:** `DelhiveryTrackingResponse` with tracking details

**Example:**
```python
from pydelhivery.models.DelhiveryModels import DelhiveryOrderTrackingRequest

request = DelhiveryOrderTrackingRequest(waybills=["WB1234567890", "WB0987654321"])
response = client.track_orders(request)
print(f"Latest Status: {response.latest_status}")
print(f"Location: {response.latest_status_location}")
```

##### `cancelShipment(waybill: str) -> None`

Cancel a shipment.

**Parameters:**
- `waybill`: Waybill number to cancel

**Example:**
```python
client.cancelShipment("WB1234567890")
```

## Error Handling

The library uses standard Python exceptions:

- `ValueError`: Raised for invalid input or missing configuration
- `requests.exceptions.HTTPError`: Raised for HTTP errors from the API
- `requests.exceptions.RequestException`: Raised for network/request errors

All errors are logged using the built-in logger.

**Example:**
```python
try:
    response = client.check_pincode_serviceability("560001")
except ValueError as e:
    print(f"Invalid input: {e}")
except requests.exceptions.HTTPError as e:
    print(f"API error: {e.response.status_code} - {e.response.text}")
```

## Logging

The library uses Python's `logging` module. Logs are automatically configured when you import the package.

```python
from pydelhivery import logger

logger.info("Custom log message")
logger.debug("Debug information")
logger.error("Error occurred")
```

## Development

### Prerequisites

- Python >= 3.12
- `uv` (recommended) or `pip`

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pydelhivery
```

2. Install dependencies:
```bash
uv sync
```

Or with pip:
```bash
pip install -e ".[dev]"
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Project Structure

```
pydelhivery/
├── src/
│   └── pydelhivery/
│       ├── __init__.py
│       ├── DelhiveryApis.py      # Main API client
│       ├── models/               # Pydantic models
│       │   ├── DelhiveryModels.py
│       │   ├── ShippingCostModel.py
│       │   ├── ShippingCreateRequest.py
│       │   ├── Tracking.py
│       │   └── WareHouseModels.py
│       └── utils/                # Utilities
│           ├── constants.py
│           └── logger.py
├── tests/                        # Test suite
├── pyproject.toml               # Project configuration
└── README.md
```

### Developer Guidelines

#### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return types
- Use Pydantic models for all API request/response data
- Maximum line length: 100 characters (where reasonable)

#### Adding New API Methods

1. **Create Pydantic Models** (if needed):
   - Add request models in the appropriate file under `models/`
   - Add response models if the API returns structured data
   - Use field validators for input validation

2. **Add API Method**:
   - Add the method to `DelhiveryIntegration` class in `DelhiveryApis.py`
   - Follow the existing pattern:
     ```python
     def new_method(self, request: RequestModel) -> ResponseModel:
         """
         Brief description of what the method does.
         
         Args:
             request: Description of request parameter
         
         Returns:
             Description of return value
         
         Raises:
             ValueError: When auth token is missing
             requests.exceptions.HTTPError: For API errors
         """
         if not self.auth_token:
             raise ValueError("DELHIVERY_AUTH_TOKEN is not configured")
         
         url = f"{self.base_url}/api/endpoint"
         headers = self._get_headers()
         payload = request.model_dump()
         
         try:
             logger.info("Description of action")
             response = requests.post(url, headers=headers, json=payload, timeout=20)
             response.raise_for_status()
             
             logger.info("Action successful")
             parsed = self._parse_response(response, ResponseModel)
             return parsed
             
         except requests.exceptions.HTTPError as e:
             logger.error(f"Action failed | Status: {e.response.status_code}")
             raise
         except requests.exceptions.RequestException as e:
             logger.error(f"Request error: {e}")
             raise
     ```

3. **Use Existing Helpers**:
   - Use `_get_headers()` for authentication headers
   - Use `_parse_response()` for parsing API responses into Pydantic models
   - Always use the logger for important events

4. **Error Handling**:
   - Always check for `auth_token` at the start of public methods
   - Use `response.raise_for_status()` to handle HTTP errors
   - Log errors with context (status code, response text)
   - Re-raise exceptions to allow caller to handle them

5. **Logging**:
   - Use `logger.info()` for successful operations
   - Use `logger.debug()` for detailed information (response bodies, etc.)
   - Use `logger.error()` for errors
   - Include relevant context in log messages (pincodes, waybills, etc.)

#### Testing

1. Write tests for new functionality in the `tests/` directory
2. Use the `scratch/main.py` file for manual testing and experimentation
3. Ensure all tests pass before submitting changes

#### Documentation

1. Update this README when adding new features
2. Include docstrings for all public methods
3. Add usage examples for new APIs
4. Document any breaking changes

#### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following the guidelines above
3. Ensure all tests pass
4. Update documentation
5. Submit a pull request with a clear description

#### Model Design Guidelines

- Use Pydantic `BaseModel` for all data structures
- Use `Field` for field descriptions and validation
- Use `field_validator` for custom validation logic
- Use appropriate types (`str`, `int`, `float`, `bool`, `Optional`, `List`, etc.)
- Use `Literal` types for enum-like string values
- Include descriptions for all fields using `Field(..., description="...")`
- Use `exclude_none=True` in `model_dump()` when updating existing resources

#### API Response Handling

- Always use `_parse_response()` for structured responses
- Handle XML responses separately (e.g., `DelhiveryInvoiceChargeItem.from_xml()`)
- Validate responses using Pydantic models
- Raise meaningful errors when validation fails

#### Environment Configuration

- Use `dotenv` for loading environment variables
- Provide sensible defaults where appropriate
- Document all required and optional environment variables
- Use `os.getenv()` with defaults for optional configuration

## Resources

- [Delhivery Developer Portal Documentation](https://one.delhivery.com/developer-portal/documents) - Official API documentation and reference
- [Delhivery Official Website](https://www.delhivery.com/)

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read the developer guidelines above and submit a pull request.

## Support

For issues and questions:
- Check existing issues in the repository
- Create a new issue with details about your problem
- Include relevant error messages and code snippets
- Refer to the [Delhivery Developer Portal Documentation](https://one.delhivery.com/developer-portal/documents) for API details

