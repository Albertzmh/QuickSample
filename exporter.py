import csv
import os
from qgis.core import (
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsFeature,
    QgsFields,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
)


def export_to_csv(features, layer, file_path):
    """
    Export sampled features to a CSV file.
    Returns (success: bool, message: str)
    """
    if not features:
        return False, "No features to export."

    fields = layer.fields()
    field_names = [field.name() for field in fields]

    try:
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            for feat in features:
                row = {name: feat[name] for name in field_names}
                writer.writerow(row)
        return True, f"Exported {len(features)} features to:\n{file_path}"
    except Exception as e:
        return False, f"Export failed: {str(e)}"


def export_to_gpkg(features, layer, file_path, layer_name="sampled_features"):
    """
    Export sampled features to a GeoPackage and load it into QGIS.
    Returns (success: bool, message: str)
    """
    if not features:
        return False, "No features to export."

    fields = layer.fields()
    crs = layer.crs()
    wkb_type = layer.wkbType()

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.layerName = layer_name
    options.fileEncoding = "UTF-8"

    # Build a temporary in-memory layer to write from
    geom_type_str = QgsWkbTypes.displayString(wkb_type)
    crs_auth = crs.authid()
    mem_layer = QgsVectorLayer(
        f"{geom_type_str}?crs={crs_auth}", layer_name, "memory"
    )
    mem_provider = mem_layer.dataProvider()
    mem_provider.addAttributes(fields.toList())
    mem_layer.updateFields()

    new_features = []
    for feat in features:
        new_feat = QgsFeature(fields)
        new_feat.setGeometry(feat.geometry())
        new_feat.setAttributes(feat.attributes())
        new_features.append(new_feat)

    mem_provider.addFeatures(new_features)

    try:
        error, msg, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
            mem_layer,
            file_path,
            QgsCoordinateTransformContext(),
            options,
        )
        if error == QgsVectorFileWriter.NoError:
            return True, f"Saved {len(features)} features to:\n{file_path}"
        else:
            return False, f"GPKG export failed: {msg}"
    except Exception as e:
        return False, f"Export failed: {str(e)}"
