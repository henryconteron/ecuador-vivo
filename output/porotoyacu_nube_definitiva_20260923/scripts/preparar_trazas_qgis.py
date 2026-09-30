"""Create a QGIS-ready GeoPackage with geometry and final support QA only.

The historical layer is used strictly for its verified 32 line geometries.
Outdated scarp-height and crest/toe attributes are removed.
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import struct
from pathlib import Path

import pandas as pd


LAYER = "perfiles_32_final_180m"
DROP = ["estacion_m", "separac_m", "oeste_m", "este_m", "az_traza",
        "angulo", "x_centro", "y_centro", "estado", "pie_m", "corona_m",
        "altura_m"]


def line_coords(blob: bytes) -> list[tuple[float, float]]:
    if blob[:2] != b"GP":
        raise ValueError("Invalid GeoPackage geometry header")
    envelope = (blob[3] >> 1) & 7
    offset = 8 + {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[envelope]
    byte_order, geometry_type, count = struct.unpack_from("<BII", blob, offset)
    if byte_order != 1 or geometry_type != 2:
        raise ValueError("Expected little-endian WKB LineString")
    return [struct.unpack_from("<dd", blob, offset + 9 + 16*i)
            for i in range(count)]


def gpkg_line(coords: list[tuple[float, float]]) -> bytes:
    xs, ys = zip(*coords)
    header = b"GP\x00\x03" + struct.pack("<i4d", 32718, min(xs), max(xs),
                                           min(ys), max(ys))
    wkb = b"\x01" + struct.pack("<II", 2, len(coords))
    wkb += b"".join(struct.pack("<dd", x, y) for x, y in coords)
    return header + wkb


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical-gpkg", type=Path, required=True)
    parser.add_argument("--geometry-csv", type=Path, required=True)
    parser.add_argument("--support-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.historical_gpkg, args.output)
    geometry = pd.read_csv(args.geometry_csv).set_index("number")
    support = pd.read_csv(args.support_csv)
    support = support[support.semiancho_faja_m == 5.0].set_index("perfil")
    with sqlite3.connect(args.output) as db:
        # The inherited spatial-index triggers call SpatiaLite functions even
        # for attribute-only updates. Supply the simple GeoPackage equivalents.
        db.create_function("ST_IsEmpty", 1, lambda blob: int(blob is None))
        db.create_function("ST_MinX", 1, lambda blob: struct.unpack_from("<d", blob, 8)[0])
        db.create_function("ST_MaxX", 1, lambda blob: struct.unpack_from("<d", blob, 16)[0])
        db.create_function("ST_MinY", 1, lambda blob: struct.unpack_from("<d", blob, 24)[0])
        db.create_function("ST_MaxY", 1, lambda blob: struct.unpack_from("<d", blob, 32)[0])
        db.execute("PRAGMA foreign_keys=OFF")
        rows = db.execute(f"SELECT numero, perfil, geom FROM {LAYER} ORDER BY numero").fetchall()
        if len(rows) != 32:
            raise ValueError("Historical GeoPackage does not contain 32 profiles")
        for number, name, blob in rows:
            if name != f"P{number}":
                raise ValueError(f"Unexpected profile name {name}")
            actual = line_coords(blob)
            expected = geometry.loc[number]
            for point, xy in zip((actual[0], actual[-1]),
                                 ((expected.x0, expected.y0),
                                  (expected.x1, expected.y1))):
                if max(abs(point[0]-xy[0]), abs(point[1]-xy[1])) > .01:
                    raise ValueError(f"P{number}: geometry differs from final sampling")
        for column in DROP:
            db.execute(f"ALTER TABLE {LAYER} DROP COLUMN {column}")
        for name, datatype in (("soporte", "TEXT"),
                               ("cobertura_30_170_pct", "REAL"),
                               ("hueco_max_30_170_m", "REAL")):
            db.execute(f"ALTER TABLE {LAYER} ADD COLUMN {name} {datatype}")
        for number, name, _ in rows:
            qc = support.loc[name]
            db.execute(
                f"UPDATE {LAYER} SET soporte=?, cobertura_30_170_pct=?, "
                "hueco_max_30_170_m=? WHERE numero=?",
                (qc.clase_soporte_directo[0],
                 float(qc.cobertura_30_170m_pct),
                 float(qc.hueco_max_30_170m_m), number),
            )
        trace = [(float(geometry.loc[n].trace_x), float(geometry.loc[n].trace_y))
                 for n in range(1, 33)]
        db.execute("CREATE TABLE traza_local_60m "
                   "(fid INTEGER PRIMARY KEY AUTOINCREMENT, geom LINESTRING, "
                   "descripcion TEXT)")
        db.execute("INSERT INTO traza_local_60m (geom, descripcion) VALUES (?, ?)",
                   (gpkg_line(trace), "Posiciones de 60 m; referencia local, no falla confirmada"))
        xs, ys = zip(*trace)
        db.execute(
            "INSERT INTO gpkg_contents "
            "(table_name,data_type,identifier,description,last_change,min_x,min_y,max_x,max_y,srs_id) "
            "VALUES ('traza_local_60m','features','traza_local_60m',"
            "'Local mapped lineament positions; not a confirmed fault',"
            "strftime('%Y-%m-%dT%H:%M:%fZ','now'),?,?,?,?,32718)",
            (min(xs), min(ys), max(xs), max(ys)),
        )
        db.execute(
            "INSERT INTO gpkg_geometry_columns "
            "(table_name,column_name,geometry_type_name,srs_id,z,m) "
            "VALUES ('traza_local_60m','geom','LINESTRING',32718,0,0)"
        )
        db.commit()
    print(args.output)


if __name__ == "__main__":
    main()
