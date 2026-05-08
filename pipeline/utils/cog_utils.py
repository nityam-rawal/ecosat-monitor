"""Utility functions for Cloud-Optimized GeoTIFF (COG) operations."""

import logging
from pathlib import Path

import rasterio
from rasterio.io import MemoryFile
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

logger = logging.getLogger(__name__)


def create_cog(input_path: str, output_path: str) -> bool:
    """
    Convert a GeoTIFF to Cloud-Optimized GeoTIFF format.

    Args:
        input_path: Path to input GeoTIFF
        output_path: Path to output COG

    Returns:
        Success boolean
    """
    try:
        with rasterio.open(input_path) as src:
            # Create COG with internal overviews
            with rasterio.open(
                output_path,
                "w",
                driver="COG",
                crs=src.crs,
                transform=src.transform,
                dtype=src.dtypes[0],
                nodata=src.nodata,
                width=src.width,
                height=src.height,
                count=src.count,
                COMPRESS="deflate",
                RESAMPLING="nearest",
            ) as dst:
                for i in range(1, src.count + 1):
                    dst.write(src.read(i), i)

        logger.info(f"Created COG: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to create COG: {e}")
        return False


def generate_overviews(cog_path: str, levels: list = None) -> bool:
    """
    Generate internal overviews for a COG.

    Args:
        cog_path: Path to COG
        levels: Zoom levels for overviews

    Returns:
        Success boolean
    """
    if levels is None:
        levels = [2, 4, 8, 16]

    try:
        with rasterio.open(cog_path, "r+") as src:
            # Build overviews
            src.build_overviews(levels, Resampling.nearest)
            src.update_tags(ns="IMAGE_STRUCTURE", LAYOUT="COG")

        logger.info(f"Generated overviews for {cog_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to generate overviews: {e}")
        return False


def reproject_to_web_mercator(input_path: str, output_path: str) -> bool:
    """
    Reproject raster to Web Mercator (EPSG:3857).

    Args:
        input_path: Path to input raster
        output_path: Path to output raster

    Returns:
        Success boolean
    """
    try:
        with rasterio.open(input_path) as src:
            with WarpedVRT(
                src, crs="EPSG:3857", resampling=Resampling.nearest
            ) as vrt:
                with rasterio.open(
                    output_path,
                    "w",
                    driver="COG",
                    crs=vrt.crs,
                    transform=vrt.transform,
                    dtype=vrt.dtypes[0],
                    width=vrt.width,
                    height=vrt.height,
                    count=vrt.count,
                    nodata=vrt.nodata,
                    COMPRESS="deflate",
                ) as dst:
                    for i in range(1, vrt.count + 1):
                        dst.write(vrt.read(i), i)

        logger.info(f"Reprojected to Web Mercator: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to reproject: {e}")
        return False
