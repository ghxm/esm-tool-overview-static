#!/usr/bin/env python3
"""
Data cleaning script for EMA tools CSV.
Applies transformation rules to convert old format to clean format.
"""

import csv
import argparse
import sys
from typing import Dict, List, Any


def to_title_case(value: str, na_values: set = None) -> str:
    """Convert comma-separated values to Title Case for category fields."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    if not value or value in na_values:
        return ''
    
    values = [v.strip().title() for v in value.split(',') if v.strip() and v not in na_values]
    return ', '.join(values)


def remove_other_operation(row: Dict[str, str], field: str, to_delete: List[str], na_values: set = None) -> str:
    """Remove 'other' entries from field and delete _other column."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    value = row.get(field, '')
    if not value or value in na_values:
        return ''
    
    # Remove 'other' from comma-separated values
    values = [v.strip() for v in value.split(',') if v.strip() and v.lower() != 'other' and v not in na_values]
    to_delete.extend([f"{field}_other"])
    return ', '.join(values)


def keep_other_with_description(row: Dict[str, str], field: str, to_delete: List[str], na_values: set = None) -> tuple[str, str]:
    """Keep 'other' values and rename _other column to _other_description."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    value = row.get(field, '')
    other_value = row.get(f"{field}_other", '')
    
    if not value or value in na_values:
        return '', ''
    
    # Split value by comma and check for 'other'
    values = [v.strip() for v in value.split(',') if v.strip() and v not in na_values]
    has_other = any(v.lower() == 'other' for v in values)
    
    # Remove 'other' from main values
    clean_values = [v for v in values if v.lower() != 'other']
    
    # If there was 'other' and we have other_value, add it back with description
    if has_other and other_value and other_value not in na_values:
        clean_values.append('Other')
        to_delete.append(f"{field}_other")  # Will be renamed, so delete original
        return ', '.join(clean_values), other_value
    
    to_delete.append(f"{field}_other")
    return ', '.join(clean_values), ''


def combine_columns(row: Dict[str, str], main_field: str, additional_fields: List[str], to_delete: List[str], na_values: set = None) -> str:
    """Combine multiple fields into one."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    values = []
    
    # Get main field value
    main_value = row.get(main_field, '')
    if main_value and main_value not in na_values:
        values.append(main_value)
    
    # Get additional field values
    for field in additional_fields:
        value = row.get(field, '')
        if value and value not in na_values:
            values.append(value)
    
    # Mark additional fields for deletion
    to_delete.extend(additional_fields)
    
    # Clean up and deduplicate
    all_items = []
    for value in values:
        items = [item.strip() for item in value.split(',') if item.strip() and item not in na_values]
        all_items.extend(items)
    
    return ', '.join(sorted(set(all_items)))


def incorporate_other_into_main(row: Dict[str, str], field: str, to_delete: List[str], na_values: set = None) -> str:
    """Incorporate _other values into main field, replacing 'other' entries."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    main_value = row.get(field, '')
    other_value = row.get(f"{field}_other", '')
    
    if not main_value or main_value in na_values:
        main_value = ''
    
    values = [v.strip() for v in main_value.split(',') if v.strip() and v.strip().lower() != 'other' and v.strip() not in na_values]
    
    # Add other_value if it exists
    if other_value and other_value not in na_values:
        other_items = [item.strip() for item in other_value.split(',') if item.strip() and item not in na_values]
        values.extend(other_items)
    
    to_delete.append(f"{field}_other")
    return ', '.join(sorted(set(values)))


def recode_values(row: Dict[str, str], field: str, mapping: Dict[str, str], na_values: set = None) -> str:
    """Recode values according to mapping."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    value = row.get(field, '')
    if not value or value in na_values:
        return ''
    
    # For comma-separated values
    if ',' in value:
        values = []
        for v in value.split(','):
            v = v.strip()
            if v not in na_values and v.lower() in mapping:
                values.append(mapping[v.lower()])
        return ', '.join(sorted(set(values)))
    else:
        # Single value
        v = value.strip()
        if v not in na_values:
            return mapping.get(v.lower(), '')
        return ''


def simplify_install(value: str, na_values: set = None) -> str:
    """Simplify install field to: store / no store / not applicable."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    if not value or value in na_values:
        return 'Not Applicable'
    
    value_lower = value.lower()
    if 'store' in value_lower or 'app store' in value_lower or 'google play' in value_lower:
        return 'Store'
    elif 'download' in value_lower or 'apk' in value_lower or 'sideload' in value_lower:
        return 'No Store'
    else:
        return 'Not Applicable'


def clean_boolean_field(value: str, na_values: set = None) -> str:
    """Clean boolean fields to consistent yes/no format."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    if not value or value in na_values:
        return 'No'
    
    value_lower = value.lower()
    if value_lower in ['true', 'yes', '1', 'TRUE']:
        return 'Yes'
    elif value_lower in ['false', 'no', '0', 'FALSE']:
        return 'No'
    else:
        return 'No'


def simplify_device_field(value: str, na_values: set = None) -> str:
    """Simplify device field to Phone, Web, or Smartwatch."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    if not value or value in na_values:
        return ''
    
    # Convert to lowercase for matching
    value_lower = value.lower()
    
    devices = []
    
    # Check for phone/smartphone/mobile devices
    if any(term in value_lower for term in ['smartphone', 'phone', 'mobile', 'tablet']):
        devices.append('Phone')
    
    # Check for web/desktop interfaces
    if any(term in value_lower for term in ['desktop', 'web', 'interface', 'browser', 'pc', 'laptop']):
        devices.append('Web')
    
    # Check for smartwatch/wearable devices
    if any(term in value_lower for term in ['smartwatch', 'watch', 'wearable']):
        devices.append('Smartwatch')
    
    # Remove duplicates and return
    return ', '.join(sorted(set(devices)))


def replace_strings(value: str, replacements: dict, na_values: set = None) -> str:
    """Replace strings according to replacement mapping."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    if not value or value in na_values:
        return ''
    
    import re
    result = value
    for old_str, new_str in replacements.items():
        result = re.sub(rf'\b{re.escape(old_str)}\b', new_str, result, flags=re.IGNORECASE)
    
    return result


def apply_transformations(row: Dict[str, str], na_values: set = None) -> Dict[str, str]:
    """Apply all transformations according to FIELDS instructions."""
    if na_values is None:
        na_values = {'NA', 'unknown', 'Unknown'}
    
    cleaned = dict(row)  # Start with copy of original
    to_delete = []  # Track fields to delete
    
    # 1. Category: Other + Desc Field for other
    category, category_desc = keep_other_with_description(cleaned, 'tool_category', to_delete, na_values)
    cleaned['tool_category'] = to_title_case(category, na_values)
    if category_desc:
        cleaned['tool_category_other_description'] = category_desc
    
    # 2. Software components: as category (same as category)
    components, components_desc = keep_other_with_description(cleaned, 'software_components', to_delete, na_values)
    cleaned['software_components'] = to_title_case(components, na_values)
    if components_desc:
        cleaned['software_components_other_description'] = components_desc
    
    # 3. Provider: no other
    cleaned['provider'] = to_title_case(remove_other_operation(cleaned, 'provider', to_delete, na_values), na_values)
    
    # 4. Developer: as provider
    cleaned['developer'] = to_title_case(remove_other_operation(cleaned, 'developer', to_delete, na_values), na_values)
    
    # 5. Target: no other; stick to academic, clinical, commercial, therapy
    target_mapping = {
        'academic': 'Academic',
        'clinical': 'Clinical', 
        'commercial': 'Commercial',
        'therapy': 'Therapy'
    }
    cleaned['target'] = recode_values(cleaned, 'target', target_mapping, na_values)
    to_delete.extend(['target_other'])
    
    # 6. Pricing: no other
    cleaned['pricing'] = to_title_case(remove_other_operation(cleaned, 'pricing', to_delete, na_values), na_values)
    
    # 7. Sensor data consolidation: rename and combine with _other fields
    cleaned['sensorlog_description'] = to_title_case(incorporate_other_into_main(cleaned, 'sensorlog', to_delete, na_values), na_values)
    cleaned['devicelog_description'] = to_title_case(incorporate_other_into_main(cleaned, 'devicelog', to_delete, na_values), na_values)
    cleaned['usagelog_description'] = to_title_case(incorporate_other_into_main(cleaned, 'usagelog', to_delete, na_values), na_values)
    cleaned['items'] = to_title_case(incorporate_other_into_main(cleaned, 'items', to_delete, na_values), na_values)
    to_delete.extend(['sensorlog', 'devicelog', 'usagelog', 'sensor_data'])
    
    # 8. Input validation: no other, merge
    cleaned['input_validation'] = remove_other_operation(cleaned, 'input_validation', to_delete, na_values)
    
    # 9. Survey flow: no other, remove 'other' from survey flow column
    cleaned['survey_flow'] = remove_other_operation(cleaned, 'survey_flow', to_delete, na_values)
    
    # 10. Media tests: delete
    to_delete.append('media_tests')
    
    # 11. Schedules: no other, remove 'other' value + add schedules_event values
    schedules_clean = remove_other_operation(cleaned, 'schedules', to_delete, na_values)
    schedules_event = cleaned.get('schedules_event', '')
    if schedules_event and schedules_event not in na_values:
        if schedules_clean:
            schedules_clean += f", {schedules_event}"
        else:
            schedules_clean = schedules_event
    cleaned['schedules'] = schedules_clean
    
    # 12. Schedules_time: no other, remove 'other' value
    cleaned['schedules_time'] = remove_other_operation(cleaned, 'schedules_time', to_delete, na_values)
    
    # 13. Schedules_event: delete (already incorporated above)
    to_delete.append('schedules_event')
    
    # 14. Signalling: no other, incorporate other into signalling, simplify
    cleaned['signalling'] = incorporate_other_into_main(cleaned, 'signalling', to_delete, na_values)
    
    # 15. Device: no other, incorporate other into device, simplify to Phone/Web/Smartwatch
    device_combined = incorporate_other_into_main(cleaned, 'device', to_delete, na_values)
    cleaned['device'] = simplify_device_field(device_combined, na_values)
    
    # 15b. String replacements (e.g. capitalize Android)
    string_replacements = {'android': 'Android'}
    for field in cleaned.keys():
        if field.startswith('system_') or field in ['device']:  # Apply to system fields and device
            cleaned[field] = replace_strings(cleaned[field], string_replacements, na_values)
    
    # 16. System tablet: delete
    to_delete.append('system_tablet')
    
    # 17. Install: no other, simplify into store / no store / not applicable
    cleaned['install'] = simplify_install(cleaned.get('install', ''), na_values)
    to_delete.append('install_other')
    
    # 18. Various deletions
    to_delete.extend([
        'participant_access_other', 'linking', 'linking_yes', 'incentives', 'incentives_other', 
        'incentives_yes', 'export_format_other', 'data_preprocessing', 'preprocessing_disabling',
        'data_analysis', 'data_analysis_specified', 'data_visualization', 'data_visualization_specified',
        'resources', 'resources_other', 'technical_support_availability', 'advice_availability'
    ])
    
    # 19. Accessibility: only accessibility_specified
    if 'accessibility_specified' in cleaned:
        cleaned['accessibility'] = cleaned['accessibility_specified']
    to_delete.extend(['accessibility_specified'])
    
    # 20. Other features: move to comments
    comments = []
    if cleaned.get('other_features'):
        comments.append(f"Other features: {cleaned['other_features']}")
    if cleaned.get('comments'):
        comments.append(cleaned['comments'])
    cleaned['comments'] = '; '.join(comments)
    to_delete.append('other_features')
    
    # 21. Required IT skills: no other, 'other' -> NA
    it_skills = cleaned.get('required_IT_skills', '')
    if it_skills and it_skills.lower() == 'other':
        cleaned['required_IT_skills'] = ''
    to_delete.append('required_IT_skills_other')
    
    # 22. Updates: no other, rename to is_maintained
    updates = cleaned.get('updates', '')
    if updates and updates not in na_values and 'continuous' in updates.lower():
        cleaned['is_maintained'] = 'Yes'
    else:
        cleaned['is_maintained'] = 'No'
    to_delete.extend(['updates', 'updates_other'])
    
    # 23. Special guidance: no other, consultation yes/no
    guidance = cleaned.get('special_guidance', '')
    if guidance and guidance not in na_values and 'consultation' in guidance.lower():
        cleaned['consultation'] = 'Yes'
    else:
        cleaned['consultation'] = 'No'
    to_delete.extend(['special_guidance', 'special_guidance_other'])
    
    # 24. Contribution: no other
    cleaned['contribution'] = remove_other_operation(cleaned, 'contribution', to_delete, na_values)
    to_delete.append('contribution_yes')
    
    # 25. Clean boolean fields
    boolean_fields = ['data_sources_selfreport', 'data_sources_sensor', 'media_yn', 'documentation_yes']
    for field in boolean_fields:
        if field in cleaned:
            cleaned[field] = clean_boolean_field(cleaned[field], na_values)
    
    # 26. Delete unwanted tracking/metadata fields
    metadata_fields = ['X', 'lfdn', 'termination', 'collection_date', 'collection_time', 
                      'collection_date_format', 'screening1', 'screening2', 'survey_flow_yes',
                      'info', 'info_other', 'data_sources', 'media_other', 'technical_support']
    to_delete.extend(metadata_fields)
    
    # Remove all fields marked for deletion
    for field in set(to_delete):
        if field in cleaned:
            del cleaned[field]
    
    # Remove empty fields and NA values
    cleaned = {k: v for k, v in cleaned.items() if v and str(v).strip() and str(v) not in na_values}
    
    return cleaned


def main():
    parser = argparse.ArgumentParser(description='Clean EMA tools CSV data')
    parser.add_argument('input_csv', help='Input CSV file path')
    parser.add_argument('-o', '--output', help='Output CSV file path', 
                       default='cleaned_EMA_tools.csv')
    parser.add_argument('--na-values', help='Comma-separated list of values to treat as NA (default: NA,unknown,Unknown)', 
                       default='NA,unknown,Unknown')
    
    args = parser.parse_args()
    
    # Parse NA values
    na_values = set(v.strip() for v in args.na_values.split(',') if v.strip())
    
    try:
        # Read input CSV
        with open(args.input_csv, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
            original_header = reader.fieldnames
        
        if not rows:
            print("Error: Input CSV is empty")
            sys.exit(1)
        
        # Clean all rows
        cleaned_rows = []
        for row in rows:
            cleaned_row = apply_transformations(row, na_values)
            if cleaned_row.get('tool_name'):  # Only include rows with tool names
                cleaned_rows.append(cleaned_row)
        
        if not cleaned_rows:
            print("Error: No valid rows found after cleaning")
            sys.exit(1)
        
        # Map original fields to cleaned fields for ordering
        field_mapping = {
            'tool_name': 'tool_name',
            'tool_category': 'tool_category', 
            'tool_category_other': 'tool_category_other_description',
            'software_components': 'software_components',
            'software_components_other': 'software_components_other_description',
            'provider': 'provider',
            'provider_name': 'provider_name',
            'developer': 'developer',
            'developer_name': 'developer_name',
            'target': 'target',
            'distribution': 'distribution',
            'server_location': 'server_location',
            'licensing': 'licensing', 
            'pricing': 'pricing',
            'info_website': 'info_website',
            'info_github': 'info_github',
            'info_publication': 'info_publication',
            'data_sources_selfreport': 'data_sources_selfreport',
            'data_sources_sensor': 'data_sources_sensor',
            'sensorlog': 'sensorlog_description',
            'devicelog': 'devicelog_description', 
            'usagelog': 'usagelog_description',
            'items': 'items',
            'input_validation': 'input_validation',
            'survey_flow': 'survey_flow',
            'media_yn': 'media_yn',
            'media': 'media',
            'schedules': 'schedules',
            'schedules_time': 'schedules_time',
            'signalling': 'signalling',
            'device': 'device',
            'system_smartphone': 'system_smartphone',
            'system_watch': 'system_watch',
            'install': 'install',
            'participant_access': 'participant_access',
            'export_format': 'export_format',
            'accessibility_specified': 'accessibility',
            'required_IT_skills': 'required_IT_skills',
            'documentation_yes': 'documentation_yes',
            'updates': 'is_maintained',
            'special_guidance': 'consultation',
            'contribution': 'contribution',
            'selfreport_notes': 'selfreport_notes',
            'comments': 'comments'
        }
        
        # Get all unique fieldnames from cleaned data
        all_fieldnames = set()
        for row in cleaned_rows:
            all_fieldnames.update(row.keys())
        
        # Order fields based on original CSV order where possible
        fieldnames = []
        if original_header:
            for orig_field in original_header:
                if orig_field in field_mapping:
                    mapped_field = field_mapping[orig_field]
                    if mapped_field in all_fieldnames and mapped_field not in fieldnames:
                        fieldnames.append(mapped_field)
                        all_fieldnames.discard(mapped_field)
        
        # Add any remaining fields alphabetically
        fieldnames.extend(sorted(all_fieldnames))
        
        # Write output CSV
        with open(args.output, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)
        
        print(f"Successfully cleaned {len(cleaned_rows)} tools")
        print(f"Output saved to: {args.output}")
        print(f"Fields in output: {len(fieldnames)}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_csv}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()