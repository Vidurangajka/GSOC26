from shapely.geometry import box

class Rectangle:
    def __init__(self, name, layer, x_min, y_min, x_max, y_max):
        self.name = name
        self.layer = layer
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def width(self):
        return self.x_max - self.x_min

    def height(self):
        return self.y_max - self.y_min

    def to_shapely(self):
        """Converts our simple rectangle into a Shapely polygon for advanced math."""
        return box(self.x_min, self.y_min, self.x_max, self.y_max)

    def __repr__(self):
        return f"[{self.layer}] {self.name}: ({self.x_min}, {self.y_min}) to ({self.x_max}, {self.y_max})"