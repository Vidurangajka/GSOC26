import odb
import json

def extract_rectangles_from_db(odb_file_path, target_layer_name, output_json_path):
    print(f"Loading OpenROAD Database: {odb_file_path}")
    db = odb.dbDatabase.create()
    db = odb.read_db(db, odb_file_path)
    
    if db is None:
        print(f"Failed to load {odb_file_path}")
        return

    tech = db.getTech()
    layer = tech.findLayer(target_layer_name)
    if not layer:
        print(f"Error: Layer '{target_layer_name}' not found in Tech.")
        return
    
    chip = db.getChip()
    block = chip.getBlock()

    extracted_shapes = []
    seen_layers = set() # This will track what layers actually exist on the pins!
    
    for inst in block.getInsts():
        loc_x, loc_y = inst.getLocation()
        master = inst.getMaster()
        
        for mterm in master.getMTerms():
            for mpin in mterm.getMPins():
                for box in mpin.getGeometry():
                    layer_obj = box.getTechLayer()
                    if layer_obj:
                        found_layer_name = layer_obj.getName()
                        seen_layers.add(found_layer_name) # Record the layer
                        
                        # FIX: Compare the string names, not the Python objects!
                        if found_layer_name == target_layer_name:
                            dbu = tech.getLefUnits()
                            
                            x_min = (box.xMin() + loc_x) / dbu
                            y_min = (box.yMin() + loc_y) / dbu
                            x_max = (box.xMax() + loc_x) / dbu
                            y_max = (box.yMax() + loc_y) / dbu
                            
                            extracted_shapes.append({
                                "name": f"{inst.getName()}_{mterm.getName()}",
                                "layer": target_layer_name,
                                "x_min": x_min,
                                "y_min": y_min,
                                "x_max": x_max,
                                "y_max": y_max
                            })
                            
    # Save to JSON
    with open(output_json_path, 'w') as f:
        json.dump(extracted_shapes, f, indent=4)
        
    print(f"--- SNOOPER: I scanned the standard cell pins and found these layers: {', '.join(seen_layers)} ---")
    print(f"Extracted {len(extracted_shapes)} shapes to {output_json_path}")