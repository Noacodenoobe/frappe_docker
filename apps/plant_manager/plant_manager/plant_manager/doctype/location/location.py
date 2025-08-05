# Copyright (c) 2024, AI Agent and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet


class Location(NestedSet):
    """Location DocType with tree structure for plant management."""
    
    def validate(self):
        """Validation method called before saving the document."""
        self.validate_location_hierarchy()
    
    def validate_location_hierarchy(self):
        """Validate the location hierarchy rules."""
        if self.parent_location:
            parent = frappe.get_doc("Location", self.parent_location)
            
            # Define allowed hierarchy
            hierarchy_rules = {
                "Pietro": [],  # Pietro can be root
                "Strefa": ["Pietro"],  # Strefa can have Pietro as parent
                "Lokalizacja szczegółowa": ["Strefa", "Pietro"],  # Detailed location
                "Lokalizacja precyzyjna": ["Lokalizacja szczegółowa", "Strefa"]  # Precise location
            }
            
            allowed_parents = hierarchy_rules.get(self.location_type, [])
            
            if allowed_parents and parent.location_type not in allowed_parents:
                frappe.throw(
                    f"Location type '{self.location_type}' cannot have parent of type '{parent.location_type}'. "
                    f"Allowed parent types: {', '.join(allowed_parents)}"
                )
    
    def before_insert(self):
        """Method called before inserting the document into database."""
        # Auto-set is_group based on location_type
        if self.location_type in ["Pietro", "Strefa"]:
            self.is_group = 1
        else:
            self.is_group = 0
    
    def get_full_path(self):
        """Get the full hierarchical path of this location."""
        path_parts = [self.location_name]
        current_location = self
        
        while current_location.parent_location:
            parent = frappe.get_doc("Location", current_location.parent_location)
            path_parts.insert(0, parent.location_name)
            current_location = parent
        
        return " -> ".join(path_parts)


def get_location_by_path(path_components):
    """
    Find location by hierarchical path components.
    
    Args:
        path_components (list): List of location names in hierarchical order
        
    Returns:
        str: Name of the location document or None if not found
    """
    if not path_components:
        return None
    
    # Start with root level (no parent)
    current_parent = None
    
    for component in path_components:
        # Find location with this name and current parent
        filters = {
            "location_name": component,
            "parent_location": current_parent
        }
        
        locations = frappe.get_list("Location", filters=filters, limit=1)
        
        if not locations:
            return None
        
        current_parent = locations[0].name
    
    return current_parent


def create_location_if_not_exists(location_name, location_type, parent_location=None, description=None):
    """
    Create a location if it doesn't exist.
    
    Args:
        location_name (str): Name of the location
        location_type (str): Type of location (Pietro, Strefa, etc.)
        parent_location (str): Name of parent location
        description (str): Optional description
        
    Returns:
        str: Name of the location document
    """
    # Check if location already exists
    filters = {
        "location_name": location_name,
        "parent_location": parent_location
    }
    
    existing = frappe.get_list("Location", filters=filters, limit=1)
    
    if existing:
        return existing[0].name
    
    # Create new location
    try:
        location = frappe.get_doc({
            "doctype": "Location",
            "location_name": location_name,
            "location_type": location_type,
            "parent_location": parent_location,
            "description": description or ""
        })
        
        location.insert()
        frappe.db.commit()
        
        frappe.logger().info(f"Created location: {location_name} ({location_type})")
        return location.name
        
    except Exception as e:
        frappe.log_error(f"Error creating location {location_name}: {str(e)}", "Location Creation Error")
        raise