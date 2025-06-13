import setuptools


setuptools.setup(
    name='RawNetPrintPlugin',

    entry_points={"inventree_plugins": ["RawNetPrintPlugin = raw_net_print_plugin.printing:RawNetPrintPluginClass"]},

    requires=[
        'pycups'
    ]
)
