# Copyright (c) 2024, AI Agent and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Plant(Document):
    """Plant DocType for managing individual plants."""
    
    def validate(self):
        """Validation method called before saving the document."""
        self.validate_location_exists()
        self.validate_plant_name()
    
    def validate_location_exists(self):
        """Validate that the linked location exists."""
        if self.location and not frappe.db.exists("Location", self.location):
            frappe.throw(f"Location '{self.location}' does not exist.")
    
    def validate_plant_name(self):
        """Validate plant name format."""
        if not self.plant_name:
            frappe.throw("Plant name is required.")
        
        # Remove any leading/trailing whitespace
        self.plant_name = self.plant_name.strip()
        
        if len(self.plant_name) < 2:
            frappe.throw("Plant name must be at least 2 characters long.")
    
    def before_save(self):
        """Method called before saving the document."""
        # Set default acquisition date if not provided
        if not self.acquisition_date:
            self.acquisition_date = frappe.utils.today()
    
    def get_location_path(self):
        """Get the full hierarchical path of the plant's location."""
        if not self.location:
            return "No location assigned"
        
        try:
            location_doc = frappe.get_doc("Location", self.location)
            return location_doc.get_full_path()
        except Exception:
            return f"Location: {self.location}"
    
    def get_dashboard_data(self):
        """Return data for plant dashboard."""
        return {
            "fieldname": "plant",
            "transactions": []
        }


def create_plant_from_csv_data(csv_row, location_mapping=None):
    """
    Create a plant from CSV data row.
    
    Args:
        csv_row (dict): Row from CSV with plant data
        location_mapping (dict): Optional mapping for location resolution
        
    Returns:
        str: Name of created plant document or None if failed
    """
    try:
        # Extract data from CSV row according to zasady_agenta.md
        plant_id = csv_row.get('ID_Rosliny', '').strip()
        species = csv_row.get('Roslina', '').strip()
        pietro = csv_row.get('Pietro', '').strip()
        strefa_glowna = csv_row.get('Strefa_glowna', '').strip()
        lokalizacja_szczegolowa = csv_row.get('Lokalizacja_szczegolowa', '').strip()
        lokalizacja_precyzyjna = csv_row.get('Lokalizacja_precyzyjna', '').strip()
        rodzaj_donicy = csv_row.get('Rodzaj_donicy', '').strip()
        
        if not plant_id or not species:
            frappe.log_error(f"Missing required data for plant: {csv_row}", "Plant Import Error")
            return None
        
        # Build location path according to zasady_agenta.md rules
        path_components = [f'P{pietro}']
        
        if strefa_glowna:
            path_components.append(strefa_glowna)
        
        if rodzaj_donicy:  # This is actually the location name according to validation
            if lokalizacja_szczegolowa:
                path_components.append(lokalizacja_szczegolowa)
            path_components.append(rodzaj_donicy)
        elif lokalizacja_szczegolowa:
            path_components.append(lokalizacja_szczegolowa)
        
        # Find location using path
        from plant_manager.plant_manager.doctype.location.location import get_location_by_path
        location_name = get_location_by_path(path_components)
        
        if not location_name:
            frappe.log_error(
                f"Location not found for path: {' -> '.join(path_components)} (Plant: {plant_id})", 
                "Plant Import Location Error"
            )
            return None
        
        # Check if plant already exists
        if frappe.db.exists("Plant", plant_id):
            frappe.logger().info(f"Plant {plant_id} already exists, skipping")
            return plant_id
        
        # Create plant document
        plant_doc = frappe.get_doc({
            "doctype": "Plant",
            "plant_name": plant_id,
            "species": species,
            "location": location_name,
            "health_status": "Unknown",  # Default status for imports
            "description": f"Imported from CSV. Position: {lokalizacja_precyzyjna}" if lokalizacja_precyzyjna else "Imported from CSV"
        })
        
        plant_doc.insert()
        frappe.db.commit()
        
        frappe.logger().info(f"Created plant: {plant_id} ({species}) at {' -> '.join(path_components)}")
        return plant_doc.name
        
    except Exception as e:
        error_msg = f"Error creating plant from CSV data {csv_row}: {str(e)}"
        frappe.log_error(error_msg, "Plant Creation Error")
        return None


def bulk_import_plants_from_csv(csv_file_path):
    """
    Bulk import plants from CSV file.
    
    Args:
        csv_file_path (str): Path to CSV file
        
    Returns:
        dict: Import statistics
    """
    import csv
    
    stats = {
        "total_rows": 0,
        "successful_imports": 0,
        "failed_imports": 0,
        "skipped": 0
    }
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            for row_num, row in enumerate(reader, 1):
                stats["total_rows"] += 1
                
                # Skip header row indicator (lp column)
                if row.get('lp', '').strip() == 'lp':
                    stats["skipped"] += 1
                    continue
                
                result = create_plant_from_csv_data(row)
                
                if result:
                    stats["successful_imports"] += 1
                else:
                    stats["failed_imports"] += 1
                
                # Commit every 50 records to avoid large transactions
                if row_num % 50 == 0:
                    frappe.db.commit()
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error during bulk plant import: {str(e)}", "Bulk Plant Import Error")
        stats["failed_imports"] += 1
    
    return stats