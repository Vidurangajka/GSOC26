import json
import os
import argparse
from src.geometry import Rectangle
from src.engine import DRCEngine
from src.parser import RuleParser
from src.visualizer import DRCVisualizer

def load_shapes_from_json(filepath):
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
    parser = argparse.ArgumentParser(description="Gemini DRC Agent - Autonomous Layout Verification")
    parser.add_argument("--rules", required=True, help="Path to the YAML rules file (e.g., rules/gf180.yaml)")
    parser.add_argument("--layout", required=True, help="Path to the extracted JSON layout (e.g., li1_shapes.json)")
    parser.add_argument("--output", default="drc_results.png", help="Filename for the result visualization")
    
    args = parser.parse_args()

    # 1. Load Rules
    rule_parser = RuleParser(args.rules)
    tech_rules = rule_parser.load_rules()
    
    # 2. Load Layout
    layout_shapes = load_shapes_from_json(args.layout)
    if not layout_shapes:
        return

    print(f"Loaded {len(layout_shapes)} shapes from {args.layout}")

    # 3. Run Engine
    engine = DRCEngine()
    for rule in tech_rules:
        r_type = rule['check_type']
        layer = rule['layer1']
        val = rule['value']

        if r_type == 'min_width':
            target_shapes = [s for s in layout_shapes if s.layer == layer]
            for shape in target_shapes:
                engine.check_min_width(shape, val)

    engine.report()

    # 4. Visualize
    viz = DRCVisualizer(all_shapes=layout_shapes, violations=engine.violations)
    viz.plot_and_save(args.output)

if __name__ == "__main__":
    main()