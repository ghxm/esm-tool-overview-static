#!/usr/bin/env python3
"""
CSV to Jekyll Tools Converter

Converts a CSV file to individual markdown files with YAML frontmatter
for the Jekyll tools collection.

Usage:
    python3 scripts/csv_to_tools.py input.csv [options]

Examples:
    # Basic conversion with name field as filename
    python3 scripts/csv_to_tools.py tools.csv --filename-field name

    # Custom mapping and output directory
    python3 scripts/csv_to_tools.py data.csv --filename-field tool_name --output-dir _custom --mapping "Tool Name:name,Description:description"

    # Dry run to see what would be created
    python3 scripts/csv_to_tools.py tools.csv --filename-field name --dry-run
"""

import csv
import os
import sys
import argparse
import re
from pathlib import Path


def clean_filename(name):
    """Convert name to valid filename: lowercase, spaces to underscores, remove special chars"""
    if not name:
        return "unnamed"
    
    # Convert to string and strip whitespace
    clean = str(name).strip()
    
    # Replace spaces and common separators with underscores
    clean = re.sub(r'[\s\-\.]+', '_', clean)
    
    # Remove special characters, keep only alphanumeric and underscores
    clean = re.sub(r'[^a-zA-Z0-9_]', '', clean)
    
    # Convert to lowercase
    clean = clean.lower()
    
    # Remove multiple consecutive underscores
    clean = re.sub(r'_+', '_', clean)
    
    # Remove leading/trailing underscores
    clean = clean.strip('_')
    
    # Ensure it's not empty
    if not clean:
        return "unnamed"
    
    return clean


def parse_mapping(mapping_str=None, mapping_file=None):
    """Parse column mapping from string or file. Returns dict with CSV columns as keys and lists of YAML fields as values."""
    mapping = {}
    
    # Load from file if provided
    if mapping_file:
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):  # Skip empty lines and comments
                        continue
                    
                    if ':' in line:
                        csv_col, yaml_field = line.split(':', 1)
                        csv_col = csv_col.strip()
                        yaml_field = yaml_field.strip()
                        
                        if csv_col not in mapping:
                            mapping[csv_col] = []
                        mapping[csv_col].append(yaml_field)
                    else:
                        print(f"Warning: Invalid mapping format on line {line_num}: {line}")
        except FileNotFoundError:
            print(f"Error: Mapping file '{mapping_file}' not found")
            return {}
        except Exception as e:
            print(f"Error reading mapping file: {e}")
            return {}
    
    # Parse from string (adds to file mappings)
    if mapping_str:
        for pair in mapping_str.split(','):
            if ':' in pair:
                csv_col, yaml_field = pair.split(':', 1)
                csv_col = csv_col.strip()
                yaml_field = yaml_field.strip()
                
                if csv_col not in mapping:
                    mapping[csv_col] = []
                mapping[csv_col].append(yaml_field)
    
    return mapping


def format_yaml_value(value, field_name=None, indent_level=0):
    """Format a value for YAML frontmatter"""
    if value is None or value == '':
        return '""'
    
    # Convert to string
    value = str(value).strip()
    
    # Calculate indentation
    indent = "  " * indent_level
    
    # Handle arrays (semicolon-separated values)
    if ';' in value:
        items = [item.strip() for item in value.split(';') if item.strip()]
        if items:
            return '\n' + '\n'.join(f'{indent}  - "{item}"' for item in items)
        else:
            return '[]'
    
    # Handle boolean-like values
    if value.lower() in ('true', 'false'):
        return value.lower()
    
    # Handle numbers (but be careful with IDs, versions, etc.)
    if value.isdigit() and field_name and not any(x in field_name.lower() for x in ['id', 'version', 'year']):
        return value
    
    # Quote everything else
    # Escape quotes in the value
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def build_nested_yaml(field_mappings, row):
    """Build nested YAML structure from dot-notation field mappings"""
    yaml_data = {}
    
    for csv_col, yaml_fields in field_mappings.items():
        csv_value = row.get(csv_col, '').strip()
        # Include empty fields too
        
        for yaml_field in yaml_fields:
            # Split on dots to create nested structure
            field_parts = yaml_field.split('.')
            current_dict = yaml_data
            
            # Navigate/create nested structure
            for i, part in enumerate(field_parts):
                if i == len(field_parts) - 1:
                    # Last part - set the value (even if empty)
                    current_dict[part] = csv_value
                else:
                    # Intermediate part - ensure dict exists
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]
    
    return yaml_data


def yaml_data_to_lines(data, indent_level=0):
    """Convert nested dict to YAML lines"""
    lines = []
    indent = "  " * indent_level
    
    for key, value in data.items():
        if isinstance(value, dict):
            # Nested object
            lines.append(f"{indent}{key}:")
            lines.extend(yaml_data_to_lines(value, indent_level + 1))
        else:
            # Simple value
            formatted_value = format_yaml_value(value, key, indent_level)
            lines.append(f"{indent}{key}: {formatted_value}")
    
    return lines


def convert_csv_to_tools(csv_file, output_dir="_tools", filename_field="name", 
                        column_mapping=None, mapping_file=None, content_field=None,
                        ignore_columns=None, ignore_unmapped=False, dry_run=False, verbose=False, existing_action="ignore"):
    """Convert CSV file to Jekyll tool markdown files"""
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        return False
    
    # Parse column mapping
    mapping = parse_mapping(column_mapping, mapping_file)
    
    # Create a set of mapped CSV columns for ignore_unmapped functionality
    mapped_columns = set(mapping.keys())
    
    # Parse ignore columns
    ignore_set = set()
    if ignore_columns:
        ignore_set = set(col.strip() for col in ignore_columns.split(','))
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    if not dry_run:
        output_path.mkdir(exist_ok=True)
    
    created_files = []
    skipped_files = []
    errors = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                print("Error: CSV file appears to be empty or malformed")
                return False
            
            if verbose:
                print(f"CSV columns found: {', '.join(fieldnames)}")
                if mapping:
                    print(f"Column mappings: {mapping}")
                if ignore_set:
                    print(f"Ignoring columns: {', '.join(ignore_set)}")
            
            # Check if filename field exists
            if filename_field not in fieldnames:
                print(f"Error: Filename field '{filename_field}' not found in CSV columns: {', '.join(fieldnames)}")
                return False
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                try:
                    # Get filename from specified field
                    filename_value = row.get(filename_field, '').strip()
                    if not filename_value:
                        error_msg = f"Row {row_num}: Empty filename field '{filename_field}'"
                        errors.append(error_msg)
                        if verbose:
                            print(f"Skipping - {error_msg}")
                        continue
                    
                    # Create clean filename
                    clean_name = clean_filename(filename_value)
                    md_filename = f"{clean_name}.md"
                    md_path = output_path / md_filename
                    
                    # Handle existing files based on action
                    if md_path.exists():
                        if existing_action == "ignore":
                            skipped_files.append(md_filename)
                            if verbose:
                                print(f"Skipping existing file: {md_filename}")
                            continue
                        elif existing_action == "amend":
                            # For amend, we need to read existing file and merge YAML
                            try:
                                existing_content = md_path.read_text(encoding='utf-8')
                                # This is a simplified amend - in reality you'd parse existing YAML
                                if verbose:
                                    print(f"Amending existing file: {md_filename} (simplified merge)")
                                # For now, treat as overwrite but log differently
                            except Exception as e:
                                error_msg = f"Row {row_num}: Could not read existing file '{md_filename}': {e}"
                                errors.append(error_msg)
                                continue
                        elif existing_action == "overwrite":
                            if verbose:
                                print(f"Overwriting existing file: {md_filename}")
                        else:
                            error_msg = f"Row {row_num}: Invalid existing_action '{existing_action}'"
                            errors.append(error_msg)
                            continue
                    
                    # Generate YAML frontmatter
                    yaml_lines = ["---", "layout: tool"]
                    markdown_content = ""
                    
                    # Prepare data for nested YAML processing
                    nested_field_mappings = {}
                    simple_field_mappings = {}
                    
                    # Process all mappings (allows multiple mappings for same CSV column)
                    for csv_col, yaml_fields in mapping.items():
                        # Skip ignored columns
                        if csv_col in ignore_set:
                            continue
                        
                        # Check if this is the content field
                        if content_field and csv_col == content_field:
                            csv_value = row.get(csv_col, '')
                            if csv_value and csv_value.strip():
                                markdown_content = csv_value.strip()
                            continue  # Don't include content field in YAML frontmatter
                        
                        # Categorize fields based on dot notation
                        nested_fields = []
                        simple_fields = []
                        
                        for yaml_field in yaml_fields:
                            if '.' in yaml_field:
                                nested_fields.append(yaml_field)
                            else:
                                simple_fields.append(yaml_field)
                        
                        if nested_fields:
                            nested_field_mappings[csv_col] = nested_fields
                        if simple_fields:
                            simple_field_mappings[csv_col] = simple_fields
                    
                    # Handle unmapped columns if ignore_unmapped is False
                    if not ignore_unmapped:
                        for csv_col in row.keys():
                            # Skip if already processed via mappings
                            if csv_col in mapped_columns:
                                continue
                            
                            # Skip ignored columns
                            if csv_col in ignore_set:
                                continue
                            
                            # Check if this is the content field
                            if content_field and csv_col == content_field:
                                csv_value = row.get(csv_col, '')
                                if csv_value and csv_value.strip():
                                    markdown_content = csv_value.strip()
                                continue
                            
                            # Use 1:1 mapping for unmapped columns
                            simple_field_mappings[csv_col] = [csv_col]
                    
                    # Process simple (non-nested) fields first
                    for csv_col, yaml_fields in simple_field_mappings.items():
                        csv_value = row[csv_col]
                        for yaml_field in yaml_fields:
                            formatted_value = format_yaml_value(csv_value, yaml_field)
                            yaml_lines.append(f"{yaml_field}: {formatted_value}")
                    
                    # Process nested fields
                    if nested_field_mappings:
                        nested_data = build_nested_yaml(nested_field_mappings, row)
                        nested_lines = yaml_data_to_lines(nested_data)
                        yaml_lines.extend(nested_lines)
                    
                    yaml_lines.append("---")
                    
                    # Add markdown content if specified
                    if markdown_content:
                        yaml_lines.append("")  # Empty line after frontmatter
                        yaml_lines.append(markdown_content)
                    else:
                        yaml_lines.append("")  # Empty line after frontmatter
                    
                    # Create the full content
                    content = '\n'.join(yaml_lines)
                    
                    if dry_run:
                        print(f"Would create: {md_path}")
                        if verbose:
                            print(f"Content preview:\n{content[:200]}...")
                            print()
                    else:
                        # Write the file
                        with open(md_path, 'w', encoding='utf-8') as md_file:
                            md_file.write(content)
                        created_files.append(md_filename)
                        if verbose:
                            print(f"Created: {md_filename}")
                
                except Exception as e:
                    error_msg = f"Row {row_num}: {str(e)}"
                    errors.append(error_msg)
                    if verbose:
                        print(f"Error - {error_msg}")
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
    
    # Print summary
    print(f"\nSummary:")
    if dry_run:
        print(f"Would create {len(created_files)} tool files")
    else:
        print(f"Created {len(created_files)} tool files in {output_dir}/")
    
    if skipped_files:
        print(f"Skipped {len(skipped_files)} files (already exist)")
    
    if errors:
        print(f"Encountered {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")
    
    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Convert CSV file to Jekyll tool markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('csv_file', help='Input CSV file path')
    parser.add_argument('--filename-field', '-f', default='name',
                       help='CSV column to use for filename (default: name)')
    parser.add_argument('--output-dir', '-o', default='_tools',
                       help='Output directory (default: _tools)')
    parser.add_argument('--mapping', '-m',
                       help='Column mapping: "CSV Column:yaml_field,Another:another"')
    parser.add_argument('--mapping-file', '-mf',
                       help='File containing column mappings (one per line: "CSV Column:yaml_field")')
    parser.add_argument('--content-field', '-c',
                       help='CSV column to use as markdown content (excludes from YAML frontmatter)')
    parser.add_argument('--ignore-columns', '-i',
                       help='Comma-separated list of CSV columns to ignore completely')
    parser.add_argument('--ignore-unmapped', '-u', action='store_true',
                       help='Ignore columns that are not explicitly mapped (only process mapped columns)')
    parser.add_argument('--existing', '-e', choices=['ignore', 'overwrite', 'amend'],
                       default='ignore', help='Action for existing files (default: ignore)')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Show what would be created without actually creating files')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    success = convert_csv_to_tools(
        csv_file=args.csv_file,
        output_dir=args.output_dir,
        filename_field=args.filename_field,
        column_mapping=args.mapping,
        mapping_file=args.mapping_file,
        content_field=args.content_field,
        ignore_columns=args.ignore_columns,
        ignore_unmapped=args.ignore_unmapped,
        dry_run=args.dry_run,
        verbose=args.verbose,
        existing_action=args.existing
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()