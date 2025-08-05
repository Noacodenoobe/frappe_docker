# Copyright (c) 2024, AI Agent and contributors
# For license information, please see license.txt

import frappe
import os
import re
from plant_manager.plant_manager.doctype.location.location import create_location_if_not_exists


def run_location_import():
    """
    Main function to import locations from TXT files.
    Processes all hierarchy files from erpcursor directory.
    """
    frappe.log_error("Starting location import process", "Location Import")
    
    # Define the path to txt files
    txt_files_dir = "/workspace/erpcursor"
    
    # List of expected TXT files (based on validation results)
    txt_files = [
        "Piętro 10 projekt stref wraz z hierarchią.txt",
        "Piętro 11 projekt stref wraz z hierarchią.txt",
        "Piętro 12 projekt stref wraz z hierarchią.txt",
        "Piętro 13 projekt stref wraz z hierarchią.txt",
        "Piętro 14 projekt stref wraz z hierarchią.txt"
    ]
    
    import_stats = {
        "files_processed": 0,
        "locations_created": 0,
        "locations_existing": 0,
        "errors": 0
    }
    
    try:
        for txt_file in txt_files:
            file_path = os.path.join(txt_files_dir, txt_file)
            
            if not os.path.exists(file_path):
                frappe.log_error(f"File not found: {file_path}", "Location Import Warning")
                continue
            
            frappe.logger().info(f"Processing file: {txt_file}")
            
            file_stats = process_hierarchy_file(file_path)
            
            import_stats["files_processed"] += 1
            import_stats["locations_created"] += file_stats["locations_created"]
            import_stats["locations_existing"] += file_stats["locations_existing"]
            import_stats["errors"] += file_stats["errors"]
        
        # Log final statistics
        frappe.logger().info(f"Location import completed: {import_stats}")
        
        frappe.msgprint(
            f"Import zakończony!\n"
            f"Pliki przetworzone: {import_stats['files_processed']}\n"
            f"Lokalizacje utworzone: {import_stats['locations_created']}\n"
            f"Lokalizacje istniejące: {import_stats['locations_existing']}\n"
            f"Błędy: {import_stats['errors']}"
        )
        
    except Exception as e:
        error_msg = f"Critical error in location import: {str(e)}"
        frappe.log_error(error_msg, "Location Import Critical Error")
        frappe.throw(error_msg)
    
    return import_stats


def process_hierarchy_file(file_path):
    """
    Process a single hierarchy TXT file.
    
    Args:
        file_path (str): Path to the TXT file
        
    Returns:
        dict: Processing statistics
    """
    stats = {
        "locations_created": 0,
        "locations_existing": 0,
        "errors": 0
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Parse the hierarchy
        hierarchy_data = parse_hierarchy_from_lines(lines)
        
        # Create locations from hierarchy
        for location_data in hierarchy_data:
            try:
                result = create_location_from_hierarchy(location_data)
                
                if result["created"]:
                    stats["locations_created"] += 1
                else:
                    stats["locations_existing"] += 1
                    
            except Exception as e:
                stats["errors"] += 1
                frappe.log_error(
                    f"Error creating location {location_data}: {str(e)}", 
                    "Location Creation Error"
                )
        
        frappe.logger().info(f"Processed {file_path}: {stats}")
        
    except Exception as e:
        stats["errors"] += 1
        frappe.log_error(f"Error processing file {file_path}: {str(e)}", "File Processing Error")
    
    return stats


def parse_hierarchy_from_lines(lines):
    """
    Parse hierarchy structure from text lines.
    
    Args:
        lines (list): List of text lines from file
        
    Returns:
        list: List of location data dictionaries
    """
    hierarchy_data = []
    parent_stack = []  # Stack to track parent locations
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
        
        # Calculate indentation level
        indent_level = get_indentation_level(line)
        location_name = extract_location_name(line)
        
        if not location_name:
            continue
        
        # Determine location type based on indentation and content
        location_type = determine_location_type(location_name, indent_level)
        
        # Adjust parent stack based on indentation
        while len(parent_stack) > indent_level:
            parent_stack.pop()
        
        # Determine parent
        parent_location = parent_stack[-1] if parent_stack else None
        
        location_data = {
            "name": location_name,
            "type": location_type,
            "parent": parent_location,
            "indent_level": indent_level,
            "line_number": line_num
        }
        
        hierarchy_data.append(location_data)
        
        # Add to parent stack for future children
        parent_stack.append(location_name)
    
    return hierarchy_data


def get_indentation_level(line):
    """
    Calculate indentation level from line.
    
    Args:
        line (str): Text line
        
    Returns:
        int: Indentation level (0 = root)
    """
    # Count leading spaces and special characters
    stripped = line.lstrip()
    indent_chars = line[:len(line) - len(stripped)]
    
    # Convert tree characters to indentation level
    level = 0
    for char in indent_chars:
        if char in ['├', '└', '│']:
            level += 1
        elif char == ' ':
            # Every 4 spaces = 1 level (adjust as needed)
            level += 0.25
    
    return int(level)


def extract_location_name(line):
    """
    Extract location name from line, removing tree characters.
    
    Args:
        line (str): Text line
        
    Returns:
        str: Clean location name
    """
    # Remove tree drawing characters and clean up
    cleaned = re.sub(r'^[│├└─\s]*', '', line.strip())
    
    # Remove any remaining special characters at the beginning
    cleaned = re.sub(r'^[─\s]*', '', cleaned)
    
    # Clean up the name
    location_name = cleaned.strip()
    
    # Skip empty lines or lines with only tree characters
    if not location_name or location_name in ['├', '└', '│', '─']:
        return None
    
    return location_name


def determine_location_type(location_name, indent_level):
    """
    Determine location type based on name and indentation.
    
    Args:
        location_name (str): Name of the location
        indent_level (int): Indentation level
        
    Returns:
        str: Location type
    """
    # Floor level (Pietro) - starts with P and number
    if re.match(r'^P\d+', location_name):
        return "Pietro"
    
    # Main zones - level 1 indentation, common zone names
    elif indent_level == 1:
        return "Strefa"
    
    # Detailed locations - level 2+ indentation
    elif indent_level == 2:
        return "Lokalizacja szczegółowa"
    
    # Precise locations - deepest level
    else:
        return "Lokalizacja precyzyjna"


def create_location_from_hierarchy(location_data):
    """
    Create a location from hierarchy data.
    
    Args:
        location_data (dict): Location data with name, type, parent
        
    Returns:
        dict: Result with created flag and location name
    """
    try:
        # Find parent location if specified
        parent_location_name = None
        if location_data["parent"]:
            # Search for parent by name
            parent_filters = {"location_name": location_data["parent"]}
            parent_locations = frappe.get_list("Location", filters=parent_filters, limit=1)
            
            if parent_locations:
                parent_location_name = parent_locations[0].name
            else:
                frappe.log_error(
                    f"Parent location not found: {location_data['parent']} for {location_data['name']}", 
                    "Parent Location Error"
                )
        
        # Check if location already exists
        existing_filters = {
            "location_name": location_data["name"],
            "parent_location": parent_location_name
        }
        existing = frappe.get_list("Location", filters=existing_filters, limit=1)
        
        if existing:
            frappe.logger().info(f"Location already exists: {location_data['name']}")
            return {"created": False, "name": existing[0].name}
        
        # Create new location
        location_name = create_location_if_not_exists(
            location_name=location_data["name"],
            location_type=location_data["type"],
            parent_location=parent_location_name,
            description=f"Imported from hierarchy file at line {location_data.get('line_number', 'unknown')}"
        )
        
        frappe.logger().info(f"Created location: {location_data['name']} ({location_data['type']})")
        return {"created": True, "name": location_name}
        
    except Exception as e:
        error_msg = f"Error creating location from hierarchy data {location_data}: {str(e)}"
        frappe.log_error(error_msg, "Location Creation Error")
        raise


def run_plant_import():
    """
    Function to import plants from CSV file.
    This will be used after locations are imported.
    """
    frappe.log_error("Starting plant import process", "Plant Import")
    
    csv_file_path = "/workspace/erpcursor/bazaroslin.csv"
    
    if not os.path.exists(csv_file_path):
        frappe.throw(f"CSV file not found: {csv_file_path}")
    
    try:
        from plant_manager.plant_manager.doctype.plant.plant import bulk_import_plants_from_csv
        
        stats = bulk_import_plants_from_csv(csv_file_path)
        
        frappe.msgprint(
            f"Import roślin zakończony!\n"
            f"Całkowita liczba wierszy: {stats['total_rows']}\n"
            f"Udane importy: {stats['successful_imports']}\n"
            f"Błędne importy: {stats['failed_imports']}\n"
            f"Pominięte: {stats['skipped']}"
        )
        
        frappe.logger().info(f"Plant import completed: {stats}")
        return stats
        
    except Exception as e:
        error_msg = f"Critical error in plant import: {str(e)}"
        frappe.log_error(error_msg, "Plant Import Critical Error")
        frappe.throw(error_msg)


# Convenience functions for manual execution
def import_locations():
    """Convenience function to import only locations."""
    return run_location_import()


def import_plants():
    """Convenience function to import only plants."""
    return run_plant_import()


def import_all():
    """Import both locations and plants."""
    frappe.logger().info("Starting full import process (locations + plants)")
    
    # First import locations
    location_stats = run_location_import()
    
    # Then import plants
    plant_stats = run_plant_import()
    
    combined_stats = {
        "locations": location_stats,
        "plants": plant_stats
    }
    
    frappe.logger().info(f"Full import completed: {combined_stats}")
    return combined_stats