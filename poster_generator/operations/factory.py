"""Factory for registering and applying image operations."""

from .image import apply_hue_shift, set_hue_from_hex

class OperationFactory:
    """
    Factory for managing and applying operations to elements.
    
    Operations are functions that transform elements (typically images).
    Each operation is associated with supported element types.
    """
    
    def __init__(self):
        self._registry = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register the default built-in operations."""
        self.register("apply_hue_shift", apply_hue_shift, supported_types=["image"])
        self.register("set_hue_from_hex", set_hue_from_hex, supported_types=["image"])
    
    def register(self, operation_name: str, operation_func, supported_types: list[str]):
        """
        Register a new operation with the factory.
        
        Args:
            operation_name: Unique name for the operation (e.g., "apply_hue_shift").
            operation_func: Callable that performs the operation.
            supported_types: List of element type names this operation supports.
        """
        self._registry[operation_name] = {
            "func": operation_func, "supported_types": supported_types
        }
    
    def get_operation(self, operation_name: str):
        """
        Retrieve a registered operation by name.
        
        Args:
            operation_name: Name of the operation to retrieve.
        
        Returns:
            dict or None: Operation info dict with 'func' and 'supported_types' keys,
                         or None if not found.
        """
        return self._registry.get(operation_name, None)
        
    def get_registered_types(self) -> list[str]:
        """
        Get a list of all registered operation names.
        
        Returns:
            list[str]: List of registered operation names.
        """
        return list(self._registry.keys())
    
    def is_registered(self, element_type: str) -> bool:
        """
        Check if an operation is registered.
        
        Args:
            element_type: Name of the operation to check.
        
        Returns:
            bool: True if the operation is registered.
        """
        return element_type in self._registry


# Global factory instance for convenience
_default_factory = OperationFactory()

def get_operation_factory() -> OperationFactory:
    """
    Get the default operation factory instance.
    
    Returns:
        OperationFactory: The global operation factory instance.
    """
    return _default_factory
