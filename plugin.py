import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .dialog import QuickSampleDialog


class QuickSamplePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self.action = QAction(icon, "QuickSample", self.iface.mainWindow())
        self.action.setToolTip("Sample features from the active layer")
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu("QuickSample", self.action)

    def unload(self):
        self.iface.removePluginVectorMenu("QuickSample", self.action)
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        layer = self.iface.activeLayer()
        if not layer or layer.type() != layer.VectorLayer:
            self.iface.messageBar().pushWarning(
                "QuickSample", "Please select a vector layer first."
            )
            return

        self.dialog = QuickSampleDialog(self.iface, layer)
        self.dialog.exec_()
