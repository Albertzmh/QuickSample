import os
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QSpinBox, QDoubleSpinBox, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QSizePolicy, QHeaderView,
    QAbstractItemView, QFrame
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from qgis.core import QgsProject

from .sampler import sample_first_n, sample_last_n, sample_random_n, sample_percentage
from .exporter import export_to_csv, export_to_gpkg


class QuickSampleDialog(QDialog):
    def __init__(self, iface, layer, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.layer = layer
        self.sampled_features = []
        self.setWindowTitle(f"QuickSample — {layer.name()}")
        self.setMinimumWidth(750)
        self.setMinimumHeight(560)
        self._build_ui()

    # ------------------------------------------------------------------ UI --

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)

        # ── Layer info ──────────────────────────────────────────────────────
        info_label = QLabel(
            f"<b>Layer:</b> {self.layer.name()}   "
            f"<b>Total features:</b> {self.layer.featureCount()}"
        )
        root.addWidget(info_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        root.addWidget(sep)

        # ── Sampling method ─────────────────────────────────────────────────
        method_box = QGroupBox("Sampling Method")
        method_layout = QVBoxLayout()
        method_box.setLayout(method_layout)

        # First N
        row_first = QHBoxLayout()
        self.rb_first = QRadioButton("First N rows")
        self.rb_first.setChecked(True)
        self.spin_first = QSpinBox()
        self.spin_first.setRange(1, max(1, self.layer.featureCount()))
        self.spin_first.setValue(min(10, self.layer.featureCount()))
        self.spin_first.setFixedWidth(90)
        row_first.addWidget(self.rb_first)
        row_first.addWidget(self.spin_first)
        row_first.addStretch()
        method_layout.addLayout(row_first)

        # Last N
        row_last = QHBoxLayout()
        self.rb_last = QRadioButton("Last N rows")
        self.spin_last = QSpinBox()
        self.spin_last.setRange(1, max(1, self.layer.featureCount()))
        self.spin_last.setValue(min(10, self.layer.featureCount()))
        self.spin_last.setFixedWidth(90)
        row_last.addWidget(self.rb_last)
        row_last.addWidget(self.spin_last)
        row_last.addStretch()
        method_layout.addLayout(row_last)

        # Random N
        row_random = QHBoxLayout()
        self.rb_random = QRadioButton("Random N rows")
        self.spin_random = QSpinBox()
        self.spin_random.setRange(1, max(1, self.layer.featureCount()))
        self.spin_random.setValue(min(10, self.layer.featureCount()))
        self.spin_random.setFixedWidth(90)
        row_random.addWidget(self.rb_random)
        row_random.addWidget(self.spin_random)
        row_random.addStretch()
        method_layout.addLayout(row_random)

        # Percentage
        row_pct = QHBoxLayout()
        self.rb_pct = QRadioButton("Percentage  %")
        self.spin_pct = QDoubleSpinBox()
        self.spin_pct.setRange(0.1, 100.0)
        self.spin_pct.setValue(10.0)
        self.spin_pct.setSingleStep(5.0)
        self.spin_pct.setDecimals(1)
        self.spin_pct.setFixedWidth(90)
        row_pct.addWidget(self.rb_pct)
        row_pct.addWidget(self.spin_pct)
        row_pct.addStretch()
        method_layout.addLayout(row_pct)

        root.addWidget(method_box)

        # ── Sample button ────────────────────────────────────────────────────
        btn_sample = QPushButton("▶  Run Sampling")
        btn_sample.setFixedHeight(34)
        btn_sample.setFont(QFont("", 10, QFont.Bold))
        btn_sample.clicked.connect(self._run_sampling)
        root.addWidget(btn_sample)

        # ── Preview table ────────────────────────────────────────────────────
        preview_box = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        preview_box.setLayout(preview_layout)

        self.result_label = QLabel("No sample yet.")
        preview_layout.addWidget(self.result_label)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.table)

        root.addWidget(preview_box)

        # ── Export buttons ───────────────────────────────────────────────────
        export_layout = QHBoxLayout()
        self.btn_csv = QPushButton("💾  Export to CSV")
        self.btn_csv.clicked.connect(self._export_csv)
        self.btn_csv.setEnabled(False)

        self.btn_gpkg = QPushButton("🗺  Save as New Layer (GPKG)")
        self.btn_gpkg.clicked.connect(self._export_gpkg)
        self.btn_gpkg.setEnabled(False)

        self.btn_select = QPushButton("✔  Select on Map")
        self.btn_select.clicked.connect(self._select_on_map)
        self.btn_select.setEnabled(False)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)

        export_layout.addWidget(self.btn_csv)
        export_layout.addWidget(self.btn_gpkg)
        export_layout.addWidget(self.btn_select)
        export_layout.addStretch()
        export_layout.addWidget(btn_close)
        root.addLayout(export_layout)

    # -------------------------------------------------------- Sampling logic --

    def _run_sampling(self):
        total = self.layer.featureCount()
        if total == 0:
            QMessageBox.warning(self, "Empty Layer", "The active layer has no features.")
            return

        if self.rb_first.isChecked():
            n = self.spin_first.value()
            features = sample_first_n(self.layer, n)
        elif self.rb_last.isChecked():
            n = self.spin_last.value()
            features = sample_last_n(self.layer, n)
        elif self.rb_random.isChecked():
            n = self.spin_random.value()
            features = sample_random_n(self.layer, n)
        else:  # percentage
            pct = self.spin_pct.value()
            features = sample_percentage(self.layer, pct)

        self.sampled_features = features
        self._populate_table(features)

        self.result_label.setText(
            f"<b>{len(features)}</b> features sampled out of <b>{total}</b> total."
        )
        self.btn_csv.setEnabled(True)
        self.btn_gpkg.setEnabled(True)
        self.btn_select.setEnabled(True)

    def _populate_table(self, features):
        if not features:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        field_names = [f.name() for f in self.layer.fields()]
        self.table.setColumnCount(len(field_names))
        self.table.setHorizontalHeaderLabels(field_names)
        self.table.setRowCount(len(features))

        for row_idx, feat in enumerate(features):
            for col_idx, fname in enumerate(field_names):
                val = feat[fname]
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)

    # ------------------------------------------------------------ Export ------

    def _export_csv(self):
        if not self.sampled_features:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Sample as CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return
        success, msg = export_to_csv(self.sampled_features, self.layer, path)
        if success:
            QMessageBox.information(self, "Export Successful", msg)
        else:
            QMessageBox.critical(self, "Export Failed", msg)

    def _export_gpkg(self):
        if not self.sampled_features:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Sample as GeoPackage", "", "GeoPackage (*.gpkg)"
        )
        if not path:
            return
        layer_name = os.path.splitext(os.path.basename(path))[0]
        success, msg = export_to_gpkg(
            self.sampled_features, self.layer, path, layer_name
        )
        if success:
            # Load the new layer into QGIS
            from qgis.core import QgsVectorLayer
            new_layer = QgsVectorLayer(f"{path}|layername={layer_name}", layer_name, "ogr")
            if new_layer.isValid():
                QgsProject.instance().addMapLayer(new_layer)
            QMessageBox.information(self, "Export Successful", msg)
        else:
            QMessageBox.critical(self, "Export Failed", msg)

    def _select_on_map(self):
        if not self.sampled_features:
            return
        ids = [f.id() for f in self.sampled_features]
        self.layer.selectByIds(ids)
        self.iface.showAttributeTable(self.layer)
        self.iface.messageBar().pushSuccess(
            "QuickSample",
            f"{len(ids)} features selected and highlighted on the map."
        )
