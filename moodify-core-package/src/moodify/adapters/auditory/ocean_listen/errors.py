class OceanBridgeError(RuntimeError):
    """Base bridge error."""


class ConfigurationError(OceanBridgeError):
    """Invalid bridge configuration."""


class OceanExecutionError(OceanBridgeError):
    """Ocean Listen process failed."""


class MappingError(OceanBridgeError):
    """Ocean report could not be mapped."""


class LicenseError(OceanBridgeError):
    """Required upstream license material is missing."""
