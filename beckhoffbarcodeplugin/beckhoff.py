"""The BeckhoffBarcodePlugin is meant to integrate the Beckhoff API into InvenTree.

This plugin can currently only match Beckhoff barcodes to supplier parts.
"""

import re

from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, SupplierBarcodeMixin


class BeckhoffPlugin(SupplierBarcodeMixin, SettingsMixin, InvenTreePlugin):
    """Plugin to integrate the LCSC API into InvenTree."""

    NAME = 'BeckhoffBarcodePlugin'
    SLUG = 'Beckhoffplugin'
    TITLE = _('Supplier Integration - Beckhoff')
    DESCRIPTION = _('Provides support for scanning Beckhoff barcodes')
    VERSION = '1.0.0'
    AUTHOR = _('Antoine Trotte')

    DEFAULT_SUPPLIER_NAME = 'Beckhoff'
    SETTINGS = {
        'SUPPLIER_ID': {
            'name': _('Supplier'),
            'description': _("The Supplier which acts as 'Beckhoff'"),
            'model': 'company.company',
            'model_filters': {'is_supplier': True},
        }
    }

    BECKHOFF_BARCODE_REGEX = re.compile(r'1P.{1,6}S.{0,11}1K.{1,30}Q.{1,5}.+')

    # Custom field mapping for Beckhoff barcodes
    # 1P : Beckhoff order number
    # S(BTN) : Beckhoff Traceability Number (BTN)
    # 1K : Article description (Part Name)
    # Q : Quantity (in packaging)

    # Optional fields 
    # 2P : Batch number (datecode of production)
    # 51S : ID/serial number
    # 30P : Variant number
    
    def extract_barcode_fields(self, barcode_data: str) -> dict[str, str]:
        """
        Get supplier_part and barcode_fields from Beckhoff QR-Code.
        Example Beckhoff QR-Code: 1P072222SBTNk4p562d71KEL1809 Q1 51S678294
        """
        if not self.BECKHOFF_BARCODE_REGEX.fullmatch(barcode_data):
            return {}

        # Extract fields
        spn = re.findall(r'1P[\S]{0,6}', barcode_data)[0][2:]
        btn = re.findall(r'S[BTN]?[\S]{0,10}', barcode_data)[0][4:]
        mpn = re.findall(r'1K[\S]{1,30}', barcode_data)[0][2:]
        qty = re.findall(r'Q[\S]{1,5}', barcode_data)[0][1:]
        #bc = re.findall(r'2P[\S]{1,12}', barcode_data)[0][2:]
        sn = re.findall(r'51S[\S]{1,9}', barcode_data)[0][3:]

        # If item does not support BTN
        if not btn:
            btn = sn

        barcode_fields = {
            'supplier_order_number' : spn,
            'serial_number' : btn,
            'manufacturer_part_number' : mpn,
            'quantity' : qty,
            #'batch_number' : bc
        }

        return barcode_fields