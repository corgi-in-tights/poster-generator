from .image import apply_hue_shift, set_hue_from_hex

class OperationFactory:
    def __init__(self):
        self._registry = {}
        self._register_defaults()
    
    def _register_defaults(self):
        self.register("apply_hue_shift", apply_hue_shift, supported_types=["image"])
        self.register("set_hue_from_hex", set_hue_from_hex, supported_types=["image"])
    
    def register(self, operation_name: str, operation_func, supported_types: list[str]):
        """
        Register a new element type with the factory.
        
        Args:
            element_type: String identifier for the element type (e.g., "text", "image")
            element_class: The class to instantiate for this type
        """
        self._registry[operation_name] = {
            "func": operation_func, "supported_types": supported_types
        }
    
    def get_operation(self, operation_name: str):
        """Retrieve a registered operation by name."""
        return self._registry.get(operation_name, None)
        
    def get_registered_types(self) -> list[str]:
        """Return a list of all registered element types."""
        return list(self._registry.keys())
    
    def is_registered(self, element_type: str) -> bool:
        """Check if an element type is registered."""
        return element_type in self._registry


_default_factory = OperationFactory()

def get_operation_factory() -> OperationFactory:
    """Get the default factory instance."""
    return _default_factory
