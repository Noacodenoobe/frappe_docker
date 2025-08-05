# Copyright (c) 2024, AI Agent and contributors
# For license information, please see license.txt

import frappe
import unittest
from plant_manager.plant_manager.doctype.location.location import get_location_by_path, create_location_if_not_exists


class TestLocation(unittest.TestCase):
    """Test cases for Location DocType."""
    
    def setUp(self):
        """Set up test data."""
        self.test_locations = []
    
    def tearDown(self):
        """Clean up test data."""
        for location_name in self.test_locations:
            if frappe.db.exists("Location", location_name):
                frappe.delete_doc("Location", location_name)
    
    def test_location_hierarchy_validation(self):
        """Test location hierarchy validation."""
        # Create Pietro (root)
        pietro = frappe.get_doc({
            "doctype": "Location",
            "location_name": "P10",
            "location_type": "Pietro"
        })
        pietro.insert()
        self.test_locations.append(pietro.name)
        
        # Create Strefa under Pietro (valid)
        strefa = frappe.get_doc({
            "doctype": "Location",
            "location_name": "Kuchnia",
            "location_type": "Strefa",
            "parent_location": pietro.name
        })
        strefa.insert()
        self.test_locations.append(strefa.name)
        
        # Try to create invalid hierarchy (should fail)
        with self.assertRaises(frappe.ValidationError):
            invalid_location = frappe.get_doc({
                "doctype": "Location",
                "location_name": "Invalid",
                "location_type": "Pietro",
                "parent_location": strefa.name  # Pietro cannot have Strefa as parent
            })
            invalid_location.insert()
    
    def test_get_location_by_path(self):
        """Test path-based location lookup."""
        # Create hierarchy: P10 -> Kuchnia -> Detailed
        pietro = create_location_if_not_exists("P10", "Pietro")
        strefa = create_location_if_not_exists("Kuchnia", "Strefa", pietro)
        detailed = create_location_if_not_exists("Detailed Location", "Lokalizacja szczegółowa", strefa)
        
        self.test_locations.extend([pietro, strefa, detailed])
        
        # Test path lookup
        found_location = get_location_by_path(["P10", "Kuchnia", "Detailed Location"])
        self.assertEqual(found_location, detailed)
        
        # Test non-existent path
        not_found = get_location_by_path(["P10", "NonExistent"])
        self.assertIsNone(not_found)
    
    def test_full_path_method(self):
        """Test the get_full_path method."""
        # Create hierarchy
        pietro = create_location_if_not_exists("P10", "Pietro")
        strefa = create_location_if_not_exists("Kuchnia", "Strefa", pietro)
        detailed = create_location_if_not_exists("Detailed Location", "Lokalizacja szczegółowa", strefa)
        
        self.test_locations.extend([pietro, strefa, detailed])
        
        # Test full path
        location_doc = frappe.get_doc("Location", detailed)
        full_path = location_doc.get_full_path()
        self.assertEqual(full_path, "P10 -> Kuchnia -> Detailed Location")