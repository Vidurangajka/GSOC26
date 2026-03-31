from src.geometry import Rectangle

class DRCEngine:
    def __init__(self):
        # We will now store dictionaries instead of just strings
        self.violations = []

    def check_min_width(self, rect, min_w):
        # Using min() ensures we check the narrowest part of the shape
        if min(rect.width(), rect.height()) < min_w:
            self.violations.append({
                "msg": f"VIOLATION [Min Width]: {rect.name} is below {min_w}",
                "shapes": [rect] # Store the bad shape!
            })

    def check_min_spacing(self, rect1, rect2, min_space):
        if rect1.layer != rect2.layer:
            return 
            
        horizontal_gap = max(0, max(rect1.x_min, rect2.x_min) - min(rect1.x_max, rect2.x_max))
        vertical_gap = max(0, max(rect1.y_min, rect2.y_min) - min(rect1.y_max, rect2.y_max))

        if horizontal_gap < min_space and vertical_gap < min_space:
             self.violations.append({
                 "msg": f"VIOLATION [Min Spacing]: Between {rect1.name} and {rect2.name} is below {min_space}",
                 "shapes": [rect1, rect2] # Store BOTH bad shapes!
             })

    def report(self):
        if not self.violations:
            print("DRC PASS: No violations found.")
        else:
            print(f"--- DRC FAILURES ({len(self.violations)} found) ---")
            for v in self.violations:
                print(v["msg"])