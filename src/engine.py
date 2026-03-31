import math
from rtree import index

class DRCEngine:
    def __init__(self):
        self.violations = []

    def check_min_width(self, rect, min_w):
        actual_w = min(rect.width(), rect.height())
        # Use 1nm tolerance (0.001um) to handle floating point noise
        if actual_w < (min_w - 0.001): 
            delta = min_w - actual_w
            self.violations.append({
                "type": "MIN_WIDTH",
                "msg": f"VIOLATION [Min Width]: {rect.name} is {actual_w:.3f}um (Min: {min_w}um)",
                "fix": f"Expand {rect.name} by {delta:.3f}um to satisfy rule.",
                "shapes": [rect]
            })

    def run_spatial_spacing_check(self, shapes, min_space):
        """High-performance R-Tree spacing check with floating point tolerance."""
        if not shapes:
            return

        idx = index.Index()
        for i, s in enumerate(shapes):
            idx.insert(i, (s.x_min, s.y_min, s.x_max, s.y_max))

        for i, s1 in enumerate(shapes):
            # Create a search window expanded by the min_space
            search_window = (
                s1.x_min - min_space, 
                s1.y_min - min_space, 
                s1.x_max + min_space, 
                s1.y_max + min_space
            )
            
            for neighbor_idx in idx.intersection(search_window):
                if neighbor_idx <= i: # Skip self and already-checked pairs
                    continue
                
                s2 = shapes[neighbor_idx]
                self._calculate_spacing(s1, s2, min_space)

    def _calculate_spacing(self, rect1, rect2, min_space):
        # Calculate horizontal and vertical gaps
        h_gap = max(0, max(rect1.x_min, rect2.x_min) - min(rect1.x_max, rect2.x_max))
        v_gap = max(0, max(rect1.y_min, rect2.y_min) - min(rect1.y_max, rect2.y_max))

        # Euclidean distance between bounding boxes
        dist = math.sqrt(h_gap**2 + v_gap**2)

        # Apply 1nm tolerance to distance check
        if 0 < dist < (min_space - 0.001):
            delta = min_space - dist
            self.violations.append({
                "type": "MIN_SPACING",
                "msg": f"VIOLATION [Min Spacing]: {rect1.name} and {rect2.name} are {dist:.3f}um apart",
                "fix": f"Increase separation between {rect1.name} and {rect2.name} by {delta:.3f}um.",
                "shapes": [rect1, rect2]
            })

    def report(self):
        if not self.violations:
            print("\n✅ DRC PASS: No violations found (within 1nm tolerance).")
        else:
            print(f"\n--- [Agentic DRC Report: {len(self.violations)} Issues] ---")
            for i, v in enumerate(self.violations, 1):
                print(f"{i}. {v['msg']}")
                print(f"   💡 SUGGESTION: {v['fix']}")