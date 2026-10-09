"""Provides support for scanning Beckhoff barcodes"""


from plugin import InvenTreePlugin

import re
from plugin.mixins import SettingsMixin

from . import PLUGIN_VERSION


class BeckhoffBarcodePlugin(SettingsMixin, InvenTreePlugin):

    """BeckhoffBarcodePlugin - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "BeckhoffBarcodePlugin"
    NAME = "BeckhoffBarcodePlugin"
    SLUG = "beckhoffbarcodeplugin"
    DESCRIPTION = "Provides support for scanning Beckhoff barcodes"
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "Antoine Trotte"
    
    LICENSE = "MIT"

    # Optionally specify supported InvenTree versions
    # MIN_VERSION = '0.18.0'
    # MAX_VERSION = '2.0.0'

    
    
    
    # Plugin settings (from SettingsMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/settings/
    SETTINGS = {
        # Define your plugin settings here...
        'CUSTOM_VALUE': {
            'name': 'Custom Value',
            'description': 'A custom value',
            'validator': int,
            'default': 42,
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
    
    
    
    
    
