from pydantic import BaseModel, Field
from typing import Optional
import xml.etree.ElementTree as ET


def _get_float(parent: ET.Element, tag: str) -> float:
    el = parent.find(tag)
    if el is None or el.text is None or el.text.strip() == "":
        return 0.0
    return float(el.text)


def _get_text(parent: ET.Element, tag: str) -> Optional[str]:
    el = parent.find(tag)
    if el is None or el.text is None or el.text.strip() == "":
        return None
    return el.text.strip()


class DelhiveryTaxData(BaseModel):
    swacch_bharat_tax: float = 0
    IGST: float = 0
    SGST: float = 0
    service_tax: float = 0
    krishi_kalyan_cess: float = 0
    CGST: float = 0

    @classmethod
    def from_xml(cls, tax_el: Optional[ET.Element]) -> "DelhiveryTaxData":
        if tax_el is None:
            return cls()

        return cls(
            swacch_bharat_tax=_get_float(tax_el, "swacch_bharat_tax"),
            IGST=_get_float(tax_el, "IGST"),
            SGST=_get_float(tax_el, "SGST"),
            service_tax=_get_float(tax_el, "service_tax"),
            krishi_kalyan_cess=_get_float(tax_el, "krishi_kalyan_cess"),
            CGST=_get_float(tax_el, "CGST"),
        )


class DelhiveryInvoiceChargeItem(BaseModel):
    charge_ROV: float = 0
    charge_REATTEMPT: float = 0
    charge_RTO: float = 0
    charge_MPS: float = 0
    charge_pickup: float = 0
    charge_CWH: float = 0

    tax_data: DelhiveryTaxData = Field(default_factory=DelhiveryTaxData)

    charge_DEMUR: float = 0
    charge_AWB: float = 0
    zone: Optional[str] = None
    wt_rule_id: Optional[str] = None
    charge_AIR: float = 0
    charge_FSC: float = 0
    charge_LABEL: float = 0
    charge_COD: float = 0
    status: Optional[str] = None
    charge_PEAK: float = 0
    charge_POD: float = 0
    charge_LM: float = 0
    adhoc_data: Optional[str] = None
    charge_CCOD: float = 0
    gross_amount: float = 0
    charge_E2E: float = 0
    charge_DTO: float = 0
    charge_COVID: float = 0
    zonal_cl: Optional[str] = None
    charge_DL: float = 0
    total_amount: float = 0
    charge_DPH: float = 0
    charge_FOD: float = 0
    charge_DOCUMENT: float = 0
    charge_WOD: float = 0
    charge_INS: float = 0
    charge_FS: float = 0
    charge_CNC: float = 0
    charge_FOV: float = 0
    charge_QC: float = 0
    charged_weight: float = 0

    @classmethod
    def from_xml(cls, xml: str) -> "DelhiveryInvoiceChargeItem":
        root = ET.fromstring(xml)
        item = root.find("list-item")
        if item is None:
            raise ValueError("Invalid XML: <list-item> not found")

        return cls(
            charge_ROV=_get_float(item, "charge_ROV"),
            charge_REATTEMPT=_get_float(item, "charge_REATTEMPT"),
            charge_RTO=_get_float(item, "charge_RTO"),
            charge_MPS=_get_float(item, "charge_MPS"),
            charge_pickup=_get_float(item, "charge_pickup"),
            charge_CWH=_get_float(item, "charge_CWH"),
            tax_data=DelhiveryTaxData.from_xml(item.find("tax_data")),
            charge_DEMUR=_get_float(item, "charge_DEMUR"),
            charge_AWB=_get_float(item, "charge_AWB"),
            zone=_get_text(item, "zone"),
            wt_rule_id=_get_text(item, "wt_rule_id"),
            charge_AIR=_get_float(item, "charge_AIR"),
            charge_FSC=_get_float(item, "charge_FSC"),
            charge_LABEL=_get_float(item, "charge_LABEL"),
            charge_COD=_get_float(item, "charge_COD"),
            status=_get_text(item, "status"),
            charge_PEAK=_get_float(item, "charge_PEAK"),
            charge_POD=_get_float(item, "charge_POD"),
            charge_LM=_get_float(item, "charge_LM"),
            adhoc_data=_get_text(item, "adhoc_data"),
            charge_CCOD=_get_float(item, "charge_CCOD"),
            gross_amount=_get_float(item, "gross_amount"),
            charge_E2E=_get_float(item, "charge_E2E"),
            charge_DTO=_get_float(item, "charge_DTO"),
            charge_COVID=_get_float(item, "charge_COVID"),
            zonal_cl=_get_text(item, "zonal_cl"),
            charge_DL=_get_float(item, "charge_DL"),
            total_amount=_get_float(item, "total_amount"),
            charge_DPH=_get_float(item, "charge_DPH"),
            charge_FOD=_get_float(item, "charge_FOD"),
            charge_DOCUMENT=_get_float(item, "charge_DOCUMENT"),
            charge_WOD=_get_float(item, "charge_WOD"),
            charge_INS=_get_float(item, "charge_INS"),
            charge_FS=_get_float(item, "charge_FS"),
            charge_CNC=_get_float(item, "charge_CNC"),
            charge_FOV=_get_float(item, "charge_FOV"),
            charge_QC=_get_float(item, "charge_QC"),
            charged_weight=_get_float(item, "charged_weight"),
        )
