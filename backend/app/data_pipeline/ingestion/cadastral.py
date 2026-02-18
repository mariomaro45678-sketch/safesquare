"""Ingestor for Agenzia delle Entrate Cadastral Map data.

Source: https://www.agenziaentrate.gov.it/portale/download-massivo-cartografia-catastale
License: CC-BY 4.0

Supported input formats (via geopandas):
  - GeoJSON  (.geojson)
  - Shapefile (.shp, requires .shx/.dbf/.prj alongside)
  - GeoPackage (.gpkg)

The bulk download ships one archive per province/region.  Run this ingestor
once per archive, pointing it at the extracted file.  Duplicate parcels
(same municipality + foglio + particella) are skipped on re-run thanks to
the unique constraint.
"""

import geopandas as gpd
import logging
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session
from shapely.geometry import mapping

from .base import BaseIngestor
from app.models.geography import CadastralParcel, Municipality, OMIZone

logger = logging.getLogger(__name__)

# Columns that the Agenzia Entrate bulk export is known to contain.
# The ingestor is lenient: it looks for these keys case-insensitively.
_KEY_FOGLIO = ["foglio"]
_KEY_PARTICELLA = ["particella", "part"]
_KEY_COMUNE = ["codice_comune", "cod_comune", "comune_code"]


def _find_column(gdf: gpd.GeoDataFrame, candidates: List[str]) -> str | None:
    """Return the first GeoDataFrame column matching any candidate (case-insensitive)."""
    lower_map = {c.lower(): c for c in gdf.columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


class CadastralIngestor(BaseIngestor):
    """ETL ingestor for cadastral parcel shapefiles / GeoJSON."""

    def fetch(self, source: str) -> gpd.GeoDataFrame:
        """Read the spatial file and reproject to EPSG:4326 (WGS84)."""
        logger.info(f"Reading cadastral source: {source}")
        gdf = gpd.read_file(source)

        if gdf.crs is None:
            logger.warning("Source CRS is undefined — assuming EPSG:4326")
            gdf.set_crs(epsg=4326, inplace=True)
        elif gdf.crs.to_epsg() != 4326:
            logger.info(f"Reprojecting from {gdf.crs} to EPSG:4326")
            gdf.to_crs(epsg=4326, inplace=True)

        logger.info(f"Loaded {len(gdf)} features. Columns: {gdf.columns.tolist()}")
        return gdf

    def transform(self, data: gpd.GeoDataFrame) -> List[Dict[str, Any]]:
        """Normalise column names and produce a list of record dicts.

        Each dict contains the raw cadastral fields plus the WKT geometry string.
        Municipality and OMI-zone resolution happens in load() via PostGIS so that
        we can leverage spatial indexes without pulling full geometry tables into
        Python memory.
        """
        col_foglio = _find_column(data, _KEY_FOGLIO)
        col_particella = _find_column(data, _KEY_PARTICELLA)
        col_comune = _find_column(data, _KEY_COMUNE)

        if not col_foglio or not col_particella:
            raise ValueError(
                f"Required columns (foglio, particella) not found. "
                f"Available: {data.columns.tolist()}"
            )

        records = []
        for _, row in data.iterrows():
            foglio = str(row[col_foglio]).strip()
            particella = str(row[col_particella]).strip()

            if not foglio or not particella or row.geometry is None or row.geometry.is_empty:
                continue

            record: Dict[str, Any] = {
                "foglio": foglio,
                "particella": particella,
                "geometry_wkt": row.geometry.wkt,
            }
            if col_comune:
                raw = row[col_comune]
                record["comune_code"] = str(int(raw)).zfill(6) if str(raw).replace('.', '').isdigit() else str(raw).strip()

            records.append(record)

        logger.info(f"Transformed {len(records)} valid parcel records")
        return records

    def load(self, transformed_data: List[Dict[str, Any]]) -> int:
        """Insert parcels with PostGIS-based municipality + OMI zone resolution.

        Resolution strategy:
          1. Municipality: if comune_code is present, direct FK lookup (fast).
             Fallback: ST_Intersects against municipality geometries.
          2. OMI Zone: ST_Intersects against omi_zones.geometry (nullable —
             not every parcel falls inside a defined OMI zone).
        """
        # Pre-fetch municipality lookup by ISTAT code
        municipalities_by_code: Dict[str, int] = {
            m.code: m.id for m in self.db.query(Municipality.code, Municipality.id).all()
        }

        # Pre-fetch existing parcel keys to skip duplicates cheaply
        existing_keys = set(
            self.db.execute(
                text("SELECT municipality_id, foglio, particella FROM cadastral_parcels")
            ).fetchall()
        )

        count = 0
        chunk_size = 500

        for chunk in self.chunk_list(transformed_data, chunk_size):
            for record in chunk:
                # --- Resolve municipality_id ---
                municipality_id: int | None = None

                if "comune_code" in record:
                    municipality_id = municipalities_by_code.get(record["comune_code"])

                if municipality_id is None:
                    # Fallback: spatial lookup via centroid of the parcel geometry
                    row = self.db.execute(
                        text("""
                            SELECT id FROM municipalities
                            WHERE geometry IS NOT NULL
                              AND ST_Intersects(geometry, ST_GeomFromText(:wkt, 4326))
                            LIMIT 1
                        """),
                        {"wkt": record["geometry_wkt"]}
                    ).fetchone()
                    if row:
                        municipality_id = row[0]

                if municipality_id is None:
                    logger.warning(f"Skipping parcel {record['foglio']}/{record['particella']}: no municipality match")
                    continue

                # --- Duplicate check ---
                key = (municipality_id, record["foglio"], record["particella"])
                if key in existing_keys:
                    continue

                # --- Resolve omi_zone_id (best-effort) ---
                omi_row = self.db.execute(
                    text("""
                        SELECT id FROM omi_zones
                        WHERE geometry IS NOT NULL
                          AND ST_Intersects(geometry, ST_GeomFromText(:wkt, 4326))
                        LIMIT 1
                    """),
                    {"wkt": record["geometry_wkt"]}
                ).fetchone()
                omi_zone_id = omi_row[0] if omi_row else None

                # --- Insert ---
                parcel = CadastralParcel(
                    municipality_id=municipality_id,
                    omi_zone_id=omi_zone_id,
                    foglio=record["foglio"],
                    particella=record["particella"],
                    geometry=f"SRID=4326;{record['geometry_wkt']}",
                )
                self.db.add(parcel)
                existing_keys.add(key)
                count += 1

            self.db.commit()
            logger.info(f"Committed chunk — {count} parcels inserted so far")

        logger.info(f"Cadastral ingestion complete. Total new parcels: {count}")
        return count
