"""Custom exception definitions for EcoSat Monitor."""


class EcoSatException(Exception):
    """Base exception for EcoSat Monitor."""

    pass


class GEEException(EcoSatException):
    """Exception raised during Google Earth Engine operations."""

    pass


class DataIngestionException(EcoSatException):
    """Exception raised during data ingestion process."""

    pass


class TileGenerationException(EcoSatException):
    """Exception raised during tile generation."""

    pass


class AOIException(EcoSatException):
    """Exception related to Area of Interest operations."""

    pass


class DatabaseException(EcoSatException):
    """Exception raised during database operations."""

    pass


class NotFoundError(EcoSatException):
    """Resource not found error."""

    pass


class ValidationError(EcoSatException):
    """Data validation error."""

    pass
