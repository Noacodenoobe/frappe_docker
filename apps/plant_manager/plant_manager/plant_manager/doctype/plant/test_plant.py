# Copyright (c) 2024, AI Agent and contributors
# For license information, please see license.txt

import frappe
import unittest
from plant_manager.plant_manager.doctype.plant.plant import create_plant_from_csv_data
from plant_manager.plant_manager.doctype.location.location import create_location_if_not_exists


class TestPlant(unittest.TestCase):
    """Test cases for Plant DocType."""
    
    def setUp(self):
        """Set up test data."""
        self.test_plants = []
        self.test_locations = []
        
        # Create test location hierarchy
        self.pietro = create_location_if_not_exists("P10", "Pietro")
        self.strefa = create_location_if_not_exists("Kuchnia", "Strefa", self.pietro)
        self.location = create_location_if_not_exists("Test Location", "Lokalizacja szczegółowa", self.strefa)
        
        self.test_locations.extend([self.pietro, self.strefa, self.location])
    
    def tearDown(self):
        """Clean up test data."""
        # Delete plants first (they reference locations)
        for plant_name in self.test_plants:
            if frappe.db.exists("Plant", plant_name):
                frappe.delete_doc("Plant", plant_name)
        
        # Delete locations
        for location_name in reversed(self.test_locations):  # Delete in reverse order
            if frappe.db.exists("Location", location_name):
                frappe.delete_doc("Location", location_name)
    
    def test_plant_creation(self):
        """Test basic plant creation."""
        plant = frappe.get_doc({
            "doctype": "Plant",
            "plant_name": "Test Plant 001",
            "species": "Epipremnum",
            "location": self.location,
            "health_status": "Healthy"
        })
        plant.insert()
        self.test_plants.append(plant.name)
        
        # Verify plant was created
        self.assertTrue(frappe.db.exists("Plant", plant.name))
        
        # Test location path method
        location_path = plant.get_location_path()
        self.assertIn("P10", location_path)
        self.assertIn("Kuchnia", location_path)
        self.assertIn("Test Location", location_path)
    
    def test_plant_validation(self):
        """Test plant validation."""
        # Test missing plant name
        with self.assertRaises(frappe.ValidationError):
            plant = frappe.get_doc({
                "doctype": "Plant",
                "species": "Epipremnum",
                "location": self.location
            })
            plant.insert()
        
        # Test invalid location
        with self.assertRaises(frappe.ValidationError):
            plant = frappe.get_doc({
                "doctype": "Plant",
                "plant_name": "Test Plant Invalid",
                "species": "Epipremnum",
                "location": "Non-existent Location"
            })
            plant.insert()
    
    def test_create_plant_from_csv_data(self):
        """Test CSV data import."""
        csv_row = {
            'ID_Rosliny': 'P10_R1',
            'Roslina': 'Epipremnum',
            'Pietro': '10',
            'Strefa_glowna': 'Kuchnia',
            'Lokalizacja_szczegolowa': '',
            'Lokalizacja_precyzyjna': '1',
            'Rodzaj_donicy': 'Test Location'
        }
        
        result = create_plant_from_csv_data(csv_row)
        
        self.assertIsNotNone(result)
        self.assertTrue(frappe.db.exists("Plant", result))
        self.test_plants.append(result)
        
        # Verify plant data
        plant_doc = frappe.get_doc("Plant", result)
        self.assertEqual(plant_doc.species, "Epipremnum")
        self.assertEqual(plant_doc.location, self.location)
    
    def test_plant_name_validation(self):
        """Test plant name validation."""
        # Test short name
        with self.assertRaises(frappe.ValidationError):
            plant = frappe.get_doc({
                "doctype": "Plant",
                "plant_name": "A",  # Too short
                "species": "Test Species",
                "location": self.location
            })
            plant.insert()
        
        # Test whitespace handling
        plant = frappe.get_doc({
            "doctype": "Plant",
            "plant_name": "  Test Plant Whitespace  ",
            "species": "Test Species",
            "location": self.location
        })
        plant.insert()
        self.test_plants.append(plant.name)
        
        # Should trim whitespace
        self.assertEqual(plant.plant_name, "Test Plant Whitespace")
    
    def test_default_acquisition_date(self):
        """Test default acquisition date setting."""
        plant = frappe.get_doc({
            "doctype": "Plant",
            "plant_name": "Test Plant Date",
            "species": "Test Species",
            "location": self.location
        })
        plant.insert()
        self.test_plants.append(plant.name)
        
        # Should set today's date as default
        self.assertIsNotNone(plant.acquisition_date)
        self.assertEqual(plant.acquisition_date, frappe.utils.today())