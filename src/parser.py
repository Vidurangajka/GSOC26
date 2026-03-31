import yaml
import os

class RuleParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.rules = []
        self.tech_name = ""

    def load_rules(self):
        if not os.path.exists(self.filepath):
            print(f"Error: Rule file not found at {self.filepath}")
            return []

        with open(self.filepath, 'r') as file:
            data = yaml.safe_load(file)
            self.tech_name = data.get('name', 'Unknown_Tech')
            self.rules = data.get('rules', [])
            print(f"Loaded {len(self.rules)} rules for {self.tech_name}")
            
        return self.rules