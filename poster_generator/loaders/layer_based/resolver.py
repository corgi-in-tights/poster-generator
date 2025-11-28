import re


class PointResolver:
    POINT_DIMENSIONS = 2

    def should_resolve(self, field_name):
        return field_name in ("anchor", "position", "offset")

    def resolve_alphabetic_position(self, value):
        value_lower = value.strip().lower()
        if value_lower in ("left", "top"):
            return 0.0
        if value_lower in ("center", "middle"):
            return 0.5
        if value_lower in ("right", "bottom"):
            return 1.0
        return None

    def resolve_position_value(self, value, default=0):
        if value is None:
            return default

        # Handle string values
        if isinstance(value, str):
            value_lower = value.strip().lower()

            n = self.resolve_alphabetic_position(value_lower)
            if n is not None:
                return n

            # Handle percentages
            if value_lower.endswith("%"):
                try:
                    percentage = float(value_lower[:-1])
                    return percentage / 100.0
                except ValueError as err:
                    msg = f"Invalid percentage value: {value}"
                    raise ValueError(msg) from err

        # Handle numeric values
        try:
            return float(value)
        except (ValueError, TypeError) as err:
            msg = f"Invalid position value: {value}"
            raise ValueError(msg) from err

    def resolve(self, field_name, field_value, default_x=0, default_y=0):
        if isinstance(field_value, str):
            parts = field_value.split(",")
            if len(parts) != PointResolver.POINT_DIMENSIONS:
                msg = f"Point string must be in 'x,y' format: {field_value}"
                raise ValueError(msg)
            x = self.resolve_position_value(parts[0].strip(), default_x)
            y = self.resolve_position_value(parts[1].strip(), default_y)

        # Handle list format: [x, y]
        elif isinstance(field_value, list):
            if len(field_value) != PointResolver.POINT_DIMENSIONS:
                msg = f"Point list must contain exactly 2 elements: {field_value}"
                raise ValueError(msg)
            x = self.resolve_position_value(field_value[0], default_x)
            y = self.resolve_position_value(field_value[1], default_y)

        # Handle dict format: {x: ..., y: ...}
        elif isinstance(field_value, dict):
            x = self.resolve_position_value(field_value.get("x"), default_x)
            y = self.resolve_position_value(field_value.get("y"), default_y)

        else:
            msg = f"Invalid point data type: {type(field_value)}"
            raise TypeError(msg)

        return (x, y)


class ColorResolver:
    def should_resolve(self, field_name):
        return field_name in ("background", "fill", "outline", "color")

    def resolve(self, field_name, field_value):
        if isinstance(field_value, str):
            return field_value  # Assume hex string is fine as is
        if isinstance(field_value, list) and len(field_value) in (3, 4):
            return tuple(field_value)
        if isinstance(field_value, dict):
            keys = ("red", "green", "blue", "alpha")
            try:
                return tuple(field_value.get(k, 255) for k in keys)
            except KeyError as err:
                msg = f"Invalid color dictionary for field '{field_name}': missing key {err}"
                raise ValueError(msg) from err
        return field_value


class LayerBasedResolver:
    VARIABLE_PATTERN = r"--\$\{([^}]+)\}--"

    def __init__(self, variables, additional_resolvers=None):
        self.variables = variables
        self.additional_resolvers = additional_resolvers or [
            ColorResolver(),
            PointResolver(),
        ]

    def attempt_additional_resolution(self, field_name, field_value):
        if field_name is None:
            return field_value

        for extra in self.additional_resolvers:
            if extra.should_resolve(field_name):
                field_value = extra.resolve(field_name, field_value)

        return field_value

    def resolve_variable(self, value, key=None):
        if not isinstance(value, str):
            return self.attempt_additional_resolution(key, value)

        match = re.match(self.VARIABLE_PATTERN, value)
        if match:
            var_name = match.group(1)
            if var_name not in self.variables:
                msg = f"Missing variable for template: {var_name}"
                raise AttributeError(msg)
            value = self.variables[var_name]

        return self.attempt_additional_resolution(key, value)

    def deep_resolve_variables(self, data, key=None):
        # Directly resolve if its a string or can be resolved by an additional resolver
        matches_any_resolver = False
        for resolver in self.additional_resolvers:
            matches_any_resolver = resolver.should_resolve(key)
            if matches_any_resolver:
                break

        if matches_any_resolver or isinstance(data, str):
            return self.resolve_variable(data, key=key)

        if isinstance(data, dict):
            return {k: self.deep_resolve_variables(v, key=k) for k, v in data.items()}

        if isinstance(data, list):
            return [self.deep_resolve_variables(item, key=None) for item in data]

        return data
