import re


class YamlResolver:
    VARIABLE_PATTERN = r"--\$\{([^}]+)\}--"
    POINT_DIMENSIONS = 2

    def __init__(self, variables):
        self.variables = variables

    def resolve_variable(self, value):
        if not isinstance(value, str):
            return value

        def replace_var(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return str(self.variables[var_name])
            msg = f"Undefined variable: {var_name}"
            raise ValueError(msg)

        return re.sub(YamlResolver.VARIABLE_PATTERN, replace_var, value)

    def deep_resolve_variables(self, data):
        if isinstance(data, dict):
            return {k: self.deep_resolve_variables(v) for k, v in data.items()}

        if isinstance(data, list):
            return [self.deep_resolve_variables(item) for item in data]

        if isinstance(data, str):
            return self.resolve_variable(data)

        return data

    def _resolve_alphabetic_position(self, value):
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

        # Resolve variables first
        value = self.resolve_variable(value)

        # Handle string values
        if isinstance(value, str):
            value_lower = value.strip().lower()

            n = self._resolve_alphabetic_position(value_lower)
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


    def resolve_point(self, point_data, default_x=0, default_y=0):
        # Handle string format: "x,y"
        if isinstance(point_data, str):
            parts = point_data.split(",")
            if len(parts) != YamlResolver.POINT_DIMENSIONS:
                msg = f"Point string must be in 'x,y' format: {point_data}"
                raise ValueError(msg)
            x = self.resolve_position_value(parts[0].strip(), default_x)
            y = self.resolve_position_value(parts[1].strip(), default_y)

        # Handle list format: [x, y]
        elif isinstance(point_data, list):
            if len(point_data) != YamlResolver.POINT_DIMENSIONS:
                msg = f"Point list must contain exactly 2 elements: {point_data}"
                raise ValueError(msg)
            x = self.resolve_position_value(point_data[0], default_x)
            y = self.resolve_position_value(point_data[1], default_y)

        # Handle dict format: {x: ..., y: ...}
        elif isinstance(point_data, dict):
            x = self.resolve_position_value(point_data.get("x"), default_x)
            y = self.resolve_position_value(point_data.get("y"), default_y)

        else:
            msg = f"Invalid point data type: {type(point_data)}"
            raise TypeError(msg)

        return (x, y)
