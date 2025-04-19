import json
import os
from typing import Dict, Union
JsonData = Dict[str, Union[str, int, float, Dict[str, float], Dict[str, str]]]

class ProductInput:
    def __init__(self):
        self.product_name = ""
        self.units_per_shipment = 0
        self.dimensions = {"length": 0, "width": 0, "height": 0}
        self.packaging_location = ""
        self.budget_constraint = 0.0

    def get_product_details(self):
        """Get product details from user input with validation"""
        # Product Name
        self.product_name = input("Enter Product Name: ").strip()
        while not self.product_name:
            print("Product name cannot be empty!")
            self.product_name = input("Enter Product Name: ").strip()

        # Units per shipment
        while True:
            try:
                self.units_per_shipment = int(input("Enter Units per shipment: "))
                if self.units_per_shipment <= 0:
                    print("Units must be a positive number!")
                    continue
                break
            except ValueError:
                print("Please enter a valid number!")

        # Dimensions
        print("\nEnter dimensions in centimeters:")
        dimensions_input = ["length", "width", "height"]
        for dim in dimensions_input:
            while True:
                try:
                    value = float(input(f"Enter {dim} (cm): "))
                    if value <= 0:
                        print(f"{dim.capitalize()} must be a positive number!")
                        continue
                    self.dimensions[dim] = value
                    break
                except ValueError:
                    print("Please enter a valid number!")

        # Packaging Location
        self.packaging_location = input("Enter Packaging Location: ").strip()
        while not self.packaging_location:
            print("Packaging location cannot be empty!")
            self.packaging_location = input("Enter Packaging Location: ").strip()

        # Budget Constraint
        while True:
            try:
                self.budget_constraint = float(input("Enter Budget Constraint: "))
                if self.budget_constraint <= 0:
                    print("Budget must be a positive number!")
                    continue
                break
            except ValueError:
                print("Please enter a valid number!")
        
        # Save to JSON
        self.save_to_json()

    def display_details(self):
        """Display the entered product details"""
        print("\nProduct Details:")
        print(f"Product Name: {self.product_name}")
        print(f"Units per shipment: {self.units_per_shipment}")
        print(f"Dimensions (L×W×H): {self.dimensions['length']}×{self.dimensions['width']}×{self.dimensions['height']} cm")
        print(f"Packaging Location: {self.packaging_location}")
        print(f"Budget Constraint: ${self.budget_constraint:.2f}")

    def save_to_json(self):
        """Save product details to JSON file"""
        data = {
            "product_name": self.product_name,
            "units_per_shipment": self.units_per_shipment,
            "dimensions": self.dimensions,
            "packaging_location": self.packaging_location,
            "budget_constraint": self.budget_constraint
        }
        
        filename = os.path.join("temp_KB", f"{self.product_name.lower().replace(' ', '_')}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

def main():
    product = ProductInput()
    product.get_product_details()
    product.display_details()

if __name__ == "__main__":
    main()

   