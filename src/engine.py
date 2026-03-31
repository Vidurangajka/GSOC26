from rtree import index
from src.geometry import Rectangle

class DRCEngine:
    def __init__(self):
        self.violations = []

    def check_min_width(self, rect, min_w):
        if min(rect.width(), rect.height()) < min_w:
            self.violations.append({
                "msg": f"VIOLATION [Min Width]: {rect.name} is {min(rect.width(), rect.height()):.3f}um (Min: {min_w}um)",
                "shapes": [rect]
            })

    def run_spatial_spacing_check(self, shapes, min_space):
        """
        High-performance spacing check using an R-Tree index.
        Complexity: O(N log N) instead of O(N^2)
        """
        if not shapes:
            return

        # 1. Build the Spatial Index
        idx = index.Index()
        for i, s in enumerate(shapes):
            # R-tree uses (left, bottom, right, top)
            idx.insert(i, (s.x_min, s.y_min, s.x_max, s.y_max))

        # 2. Query the Index for each shape
        for i, s1 in enumerate(shapes):
            # Create a "Search Window" expanded by the min_space
            search_window = (
                s1.x_min - min_space, 
                s1.y_min - min_space, 
                s1.x_max + min_space, 
                s1.y_max + min_space
            )
            
            # Find neighbors within the search window
            for neighbor_idx in idx.intersection(search_window):
                if neighbor_idx <= i: # Skip self and duplicate pairs
                    continue
                
                s2 = shapes[neighbor_idx]
                self._calculate_spacing(s1, s2, min_space)

    def _calculate_spacing(self, rect1, rect2, min_space):
        h_gap = max(0, max(rect1.x_min, rect2.x_min) - min(rect1.x_max, rect2.x_max))
        v_gap = max(0, max(rect1.y_min, rect2.y_min) - min(rect1.y_max, rect2.y_max))
        
        import math
        distance = math.sqrt(h_gap**2 + v_gap**2)

        if 0 < distance < min_space:
            self.violations.append({
                "msg": f"VIOLATION [Min Spacing]: {rect1.name} and {rect2.name} are {distance:.3f}um apart",
                "shapes": [rect1, rect2]
            })

    def report(self):
        if not self.violations:
            print("DRC PASS: No violations found.")
        else:
            print(f"--- DRC FAILURES ({len(self.violations)} found) ---")
            for v in self.violations:
                print(v["msg"])