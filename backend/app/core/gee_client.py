"""Google Earth Engine client wrapper for EcoSat Monitor."""

import json
import logging
from typing import Any, Dict, Optional

import ee

from app.config import get_settings
from app.core.exceptions import GEEException

logger = logging.getLogger(__name__)


class GEEClient:
    """Wrapper for Google Earth Engine operations."""

    _instance: Optional["GEEClient"] = None

    def __new__(cls) -> "GEEClient":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize GEE client if not already done."""
        if self._initialized:
            return

        settings = get_settings()

        try:
            # Initialize Earth Engine with service account if provided
            if settings.GEE_SERVICE_ACCOUNT_JSON:
                service_account_info = json.loads(settings.GEE_SERVICE_ACCOUNT_JSON)
                credentials = ee.ServiceAccountCredentials(
                    email=service_account_info.get("client_email"),
                    key_data=service_account_info.get("private_key"),
                )
                ee.Initialize(credentials, project=settings.GEE_PROJECT_ID)
            else:
                # Use Application Default Credentials
                ee.Initialize(project=settings.GEE_PROJECT_ID)

            logger.info("Google Earth Engine client initialized successfully")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Google Earth Engine: {e}")
            raise GEEException(f"GEE initialization failed: {e}")

    def get_ndvi(
        self,
        geometry: ee.Geometry,
        start_date: str,
        end_date: str,
        reducer: str = "median",
    ) -> ee.Image:
        """
        Calculate NDVI from Sentinel-2 data.

        Args:
            geometry: ee.Geometry object for AOI
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            reducer: Reducer type ('median', 'mean', 'max', 'min')

        Returns:
            ee.Image with NDVI values
        """
        try:
            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterDate(start_date, end_date)
                .filterBounds(geometry)
                .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
            )

            if collection.size().getInfo() == 0:
                logger.warning(f"No Sentinel-2 images found for {start_date} to {end_date}")
                return None

            def add_ndvi(image: ee.Image) -> ee.Image:
                """Add NDVI band to image."""
                ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
                return image.addBands(ndvi)

            ndvi_collection = collection.map(add_ndvi)

            # Apply reducer
            if reducer == "median":
                result = ndvi_collection.select("NDVI").median()
            elif reducer == "mean":
                result = ndvi_collection.select("NDVI").mean()
            elif reducer == "max":
                result = ndvi_collection.select("NDVI").max()
            elif reducer == "min":
                result = ndvi_collection.select("NDVI").min()
            else:
                result = ndvi_collection.select("NDVI").median()

            return result.clip(geometry)
        except Exception as e:
            logger.error(f"Failed to calculate NDVI: {e}")
            raise GEEException(f"NDVI calculation failed: {e}")

    def get_pollution(
        self,
        geometry: ee.Geometry,
        start_date: str,
        end_date: str,
        pollutant: str = "NO2",
    ) -> ee.Image:
        """
        Get pollution data from Sentinel-5P TROPOMI.

        Args:
            geometry: ee.Geometry object for AOI
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            pollutant: Pollutant type ('NO2', 'SO2', 'CO', 'O3', 'CH4')

        Returns:
            ee.Image with pollution data
        """
        try:
            asset_mapping = {
                "NO2": "COPERNICUS/S5P/OFFL/L3_NO2",
                "SO2": "COPERNICUS/S5P/OFFL/L3_SO2",
                "CO": "COPERNICUS/S5P/OFFL/L3_CO",
                "O3": "COPERNICUS/S5P/OFFL/L3_O3",
                "CH4": "COPERNICUS/S5P/OFFL/L3_CH4",
            }
            band_mapping = {
                "NO2": "NO2_column_number_density",
                "SO2": "SO2_column_number_density",
                "CO": "CO_column_number_density",
                "O3": "O3_column_number_density",
                "CH4": "CH4_column_volume_mixing_ratio_dry_air",
            }

            asset = asset_mapping.get(pollutant, asset_mapping["NO2"])
            band = band_mapping.get(pollutant, band_mapping["NO2"])

            collection = (
                ee.ImageCollection(asset)
                .select(band)
                .filterDate(start_date, end_date)
                .filterBounds(geometry)
            )

            if collection.size().getInfo() == 0:
                logger.warning(f"No {pollutant} data found for {start_date} to {end_date}")
                return None

            return collection.mean().clip(geometry)
        except Exception as e:
            logger.error(f"Failed to get {pollutant} data: {e}")
            raise GEEException(f"{pollutant} data retrieval failed: {e}")

    def get_rainfall(
        self,
        geometry: ee.Geometry,
        start_date: str,
        end_date: str,
    ) -> ee.Image:
        """
        Get rainfall data from NASA GPM IMERG.

        Args:
            geometry: ee.Geometry object for AOI
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            ee.Image with rainfall data
        """
        try:
            collection = (
                ee.ImageCollection("NASA/GPM_L3/IMERG_V06")
                .select("precipitationCal")
                .filterDate(start_date, end_date)
                .filterBounds(geometry)
            )

            if collection.size().getInfo() == 0:
                logger.warning(f"No rainfall data found for {start_date} to {end_date}")
                return None

            return collection.sum().clip(geometry)
        except Exception as e:
            logger.error(f"Failed to get rainfall data: {e}")
            raise GEEException(f"Rainfall data retrieval failed: {e}")

    def get_lst(
        self,
        geometry: ee.Geometry,
        start_date: str,
        end_date: str,
        sensor: str = "TERRA",
    ) -> ee.Image:
        """
        Get Land Surface Temperature from MODIS.

        Args:
            geometry: ee.Geometry object for AOI
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            sensor: Sensor type ('TERRA', 'AQUA')

        Returns:
            ee.Image with LST data in Celsius
        """
        try:
            asset = "MODIS/061/MOD11A1" if sensor == "TERRA" else "MODIS/061/MYD11A1"

            collection = (
                ee.ImageCollection(asset)
                .select("LST_Day_1km")
                .filterDate(start_date, end_date)
                .filterBounds(geometry)
            )

            if collection.size().getInfo() == 0:
                logger.warning(f"No LST data found for {start_date} to {end_date}")
                return None

            # Convert from Kelvin to Celsius (multiply by 0.02 to get Kelvin, then subtract 273.15)
            def kelvin_to_celsius(image: ee.Image) -> ee.Image:
                kelvin = image.multiply(0.02)
                celsius = kelvin.subtract(273.15)
                return celsius.rename("LST_C")

            lst_celsius = collection.map(kelvin_to_celsius)
            return lst_celsius.mean().clip(geometry)
        except Exception as e:
            logger.error(f"Failed to get LST data: {e}")
            raise GEEException(f"LST data retrieval failed: {e}")

    def get_region_statistics(
        self,
        image: ee.Image,
        geometry: ee.Geometry,
        scale: int = 1000,
    ) -> Dict[str, Any]:
        """
        Calculate statistics for an image over a region.

        Args:
            image: ee.Image to analyze
            geometry: ee.Geometry for AOI
            scale: Scale in meters

        Returns:
            Dictionary with mean, min, max, stdDev values
        """
        try:
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean()
                .combine(ee.Reducer.minMax(), sharedInputs=True)
                .combine(ee.Reducer.stdDev(), sharedInputs=True),
                geometry=geometry,
                scale=scale,
                maxPixels=1e9,
            )
            return stats.getInfo()
        except Exception as e:
            logger.error(f"Failed to calculate region statistics: {e}")
            raise GEEException(f"Statistics calculation failed: {e}")

    def export_image(
        self,
        image: ee.Image,
        file_name_prefix: str,
        bucket: str,
        region: Optional[ee.Geometry] = None,
        scale: int = 30,
    ) -> str:
        """
        Export image to Google Cloud Storage (for future implementation).

        Args:
            image: ee.Image to export
            file_name_prefix: Prefix for exported file
            bucket: GCS bucket name
            region: ee.Geometry for AOI
            scale: Scale in meters

        Returns:
            Task ID
        """
        try:
            task = ee.batch.Export.image.toCloudStorage(
                image=image,
                description=file_name_prefix,
                bucket=bucket,
                fileNamePrefix=file_name_prefix,
                region=region,
                scale=scale,
                crs="EPSG:3857",
            )
            task.start()
            logger.info(f"Export task started: {task.id}")
            return task.id
        except Exception as e:
            logger.error(f"Failed to export image: {e}")
            raise GEEException(f"Image export failed: {e}")
