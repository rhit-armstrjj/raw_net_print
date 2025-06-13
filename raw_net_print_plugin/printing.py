import cups
from os import write
from tempfile import NamedTemporaryFile

from plugin import InvenTreePlugin, registry
from plugin.machine.machine_types import LabelPrinterBaseDriver
from machine.machine_types.label_printer import LabelPrinterStatus

from django.template.loader import render_to_string
from django.core.validators import MinValueValidator

class RawNetPrintPluginClass(InvenTreePlugin):
    """Plugin metadata class"""
    NAME = "RawNetPrintPlugin"
    SLUG = 'raw-net-print'

    AUTHOR = "rhit-armstrjj"
    DESCRIPTION = "Simple CUPS Driver Plugin"
    VERSION = "0.0.3"

class CUPSLabelPrinterDriver(LabelPrinterBaseDriver):
    """"""
    SLUG = 'cups-driver'
    NAME = 'CUPS Printer Driver'
    DESCRIPTION = 'An updated driver for connecting to and printing via cups.'

    MACHINE_SETTINGS = {
        'SERVER': {
            'name': 'Server',
            'description': 'IP/Hostname to connect to the cups server',
            'default': 'localhost',
            'required': True
        },
        'PORT': {
            'name': 'Port',
            'description': 'CUPS Server Port',
            'default': 631,
            'required': True,
            'validator': [
                int,
                MinValueValidator(1)
            ]
        },
        'USER': {
            'name': 'User',
            'description': 'CUPS Server Username',
            'required': True
        },
        'PASS': {
            'name': 'Password',
            'description': 'CUPS Password',
            'required': False,
            'protected': True,
        },

        'PRINTER': {
            'name': 'Printer Name',
            'description': 'Printer Queue Name',
            'required': True
        },

    }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def init_machine(self, machine):
        """Check the status of the printer in cups""" 
        cups.setServer(machine.get_setting('SERVER', 'D'))
        print(machine, "has port of", machine.get_setting('PORT','D'))

        cups.setPort(machine.get_setting('PORT', 'D'))
        cups.setUser(machine.get_setting('USER', 'D'))
        cups.setPasswordCB(lambda: machine.get_setting('PASSWORD', 'D'))

        conn = cups.Connection()

        # Make sure that the printer queue actually exists before giving green light.
        if machine.get_setting('PRINTER', 'D') not in conn.getPrinters().keys():
            machine.set_status(LabelPrinterStatus.DISCONNECTED)
            machine.set_status_text("Invalid Printer Name")
            return
        
        machine.set_status(LabelPrinterStatus.CONNECTED)
        machine.set_status_text("Ready to print.")


    def print_label(
            self,
            machine,
            label,
            item,
            **kwargs
    ):
        """Sends a label print job to the cups endpoint."""

        # Set CUPS connection setups.
        cups.setServer(machine.get_setting('SERVER', 'D'))
        cups.setPort(machine.get_setting('PORT', 'D'))
        cups.setUser(machine.get_setting('USER', 'D'))
        cups.setPasswordCB(lambda: machine.get_setting('PASSWORD', 'D'))

        conn = cups.Connection()

        if machine.get_setting('PRINTER', 'D') not in conn.getPrinters().keys():
            machine.set_status(LabelPrinterStatus.DISCONNECTED)
            machine.set_status_text("Could not find printer.")

        with NamedTemporaryFile() as f:
            pre_string = self.render_to_html(label, item)
            # I don't like having to write to filesystem, but it works for now.
            # TODO: Figure out file streaming.
            f.write(bytes(pre_string, 'UTF-8'))
            f.flush()
            conn.printFile(machine.get_setting('PRINTER','D'), f.name, 'InvenTree Job', {}) 
