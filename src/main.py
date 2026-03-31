import json
import os
import argparse
from src.geometry import Rectangle
from src.engine import DRCEngine
from src.parser import RuleParser
from src.visualizer import DRCVisualizer

def load_shapes_from_json(filepath):
    """Loads extracted OpenROAD geometries from a JSON file."""
    if not os.path.exists(filepath):
        print(f"Error: Could not find {filepath}.")
        return []
        
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    rectangles = []
    for item in data:
        rect = Rectangle(
            name=item['name'],
            layer=item['layer'],
            x_min=item['x_min'],
            y_min=item['y_min'],
            x_max=item['x_max'],
            y_max=item['y_max']
        )
        rectangles.append(rect)
    return rectangles

def main():
    # --- SETUP COMMAND LINE ARGUMENTS ---
    parser = argparse.ArgumentParser(description="GSOC26 DRC Agent - Autonomous Layout Verification")
    parser.add_argument("--rules", required=True, help="Path to the YAML rules file")
    parser.add_argument("--layout", required=True, help="Path to the extracted JSON layout")
    parser.add_argument("--output", default="drc_results.png", help="Filename for visualization")
    
    args = parser.parse_args()

    # 1. Load Tech Rules
    rule_parser = RuleParser(args.rules)
    tech_rules = rule_parser.load_rules()
    print(f"Successfully loaded {len(tech_rules)} rules from {args.rules}")
    
    # 2. Load Layout Geometries
    layout_shapes = load_shapes_from_json(args.layout)
    if not layout_shapes:
        return
    print(f"Loaded {len(layout_shapes)} shapes from {args.layout}")

    # 3. Initialize High-Performance DRC Engine
    engine = DRCEngine()

    # 4. Run Verification Loop
    print("\n--- Starting Physical Verification ---")
    for rule in tech_rules:
        r_type = rule['check_type']
        layer = rule['layer1']
        val = rule['value']

        # Filter shapes for the specific layer defined in the rule
        target_shapes = [s for s in layout_shapes if s.layer == layer]
        if not target_shapes:
            continue

        if r_type == 'min_width':
            print(f"Checking Min-Width on {len(target_shapes)} shapes in layer: {layer}...")
            for shape in target_shapes:
                engine.check_min_width(shape, val)
        
        elif r_type == 'min_spacing':
            print(f"Running Spatial R-Tree Spacing Check on {len(target_shapes)} shapes in layer: {layer}...")
            # Using the O(N log N) spatial indexing method
            engine.run_spatial_spacing_check(target_shapes, val)

    # 5. Output Results
    engine.report()

    # 6. Generate Visual Diagnostic Map
    viz = DRCVisualizer(all_shapes=layout_shapes, violations=engine.violations)
    viz.plot_and_save(args.output)

if __name__ == "__main__":
    main()