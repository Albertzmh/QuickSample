def classFactory(iface):
    from .plugin import QuickSamplePlugin
    return QuickSamplePlugin(iface)
