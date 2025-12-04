# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Always keep the information in this file up to date.

## Development Commands

**Start development server:**
```bash
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

**Alternative port if 4000 is in use:**
```bash
bundle exec jekyll serve --host 127.0.0.1 --port 4001
```

**Install dependencies:**
```bash
bundle install
```

**Build for production:**
```bash
bundle exec jekyll build
```

**Clean Jekyll cache (if encountering issues):**
```bash
bundle exec jekyll clean
```

## Architecture Overview

This is a Jekyll-based static site for displaying ESM (Experience Sampling Method) tools with a searchable, filterable table interface.

### Core Architecture

**Single Source of Truth:** Tool data lives in `_tools/` as markdown files with YAML frontmatter. This eliminates duplication between data files and detail pages.

**Configuration-Driven Filters:** The table columns and filter types are defined in `_config.yml` under `fields`. This allows dynamic generation of filters without code changes.

**Nested Data Architecture:** Supports nested YAML structures (e.g., `metadata.category`, `technical.components`) with dynamic field access via custom includes.

**Value Label System:** Allows custom display labels for field values while preserving original data integrity for filtering and export.

**Hybrid Filtering System:** Uses List.js for basic search/sort functionality but implements custom JavaScript for complex multiselect filters with AND/OR logic.

### Key Components

**Main Table (`index.html`):**
- Dynamically generates filter controls from `_config.yml` configuration
- Implements three filter types: `select`, `multiselect-and`, `multiselect-or`
- Uses List.js for search and sorting, custom JS for filtering
- Handles edge cases like "no results" display

**Tool Collection (`_tools/`):**
- Jekyll collection with permalink structure `/tools/:name/`
- Each markdown file has frontmatter with nested tool metadata structure
- Generated automatically from CSV using `scripts/csv_to_tools.py`
- Supports nested structures like `metadata.category`, `technical.components`, `data.sensor.types`

**Dynamic Field Access (`_includes/`):**
- `get_field_value.html`: Dynamically accesses nested fields using dot notation
- `apply_value_label.html`: Transforms display values while preserving original data
- Enables configuration-driven field access without hardcoded paths

**Dynamic Filter Generation:**
- Filters are generated in Liquid templates based on `_config.yml`
- Multiselect filters use Bootstrap dropdowns with checkboxes
- Filter state management handled in JavaScript
- CSS class names sanitized (dots replaced with dashes) for compatibility

### JavaScript Architecture

**Manual Row Visibility Control:**
- Bypasses List.js filter method for complex filtering
- Directly manipulates `display: none` on table rows
- Ensures proper "no results" behavior when no items match

**Event Delegation:**
- Row clicks use event delegation for better performance
- Multiselect dropdown state managed through data attributes

### Jekyll Compatibility

**Version Constraints:**
- Uses Jekyll 3.9.0 for M4 Mac compatibility
- Includes `kramdown-parser-gfm` for GitHub Flavored Markdown
- Local bundle path to avoid permission issues

## Configuration Reference

**IMPORTANT:** For detailed configuration documentation including field configuration, display contexts, filter setup, and data schema, see the **Configuration** section in `README.md`. Keep that documentation up to date whenever configuration options change.

Key configuration concepts:
- **Display Contexts:** `table`, `detail_overview`, `detail_info`, `detail_publication`
- **Field Types:** `string`, `category`, `array`, `url`, `date`
- **Filter Types:** `select`, `multiselect-and`, `multiselect-or`
- **Nested Field Names:** Use dot notation (e.g., `metadata.category`, `technical.components`)
- **Value Labels:** Custom display labels via `value_labels` config option
- **Auto Title Case:** Automatic title casing with `titlecase: true` option
- **Popover Descriptions:** Rich help text via `popover.title` and `popover.content`
- **Publication Fields:** Separate `publication_url` and `publication_citation` fields
- **Automatic Sectioning:** Uncategorized `detail_info` fields appear in "Other" section

## Data Management Scripts

**CSV Data Cleaning (`scripts/old_to_clean.py`):**
- Cleans and transforms raw EMA tools CSV data
- Implements device field simplification to Phone/Web/Smartwatch categories
- Generic string replacement system for data standardization
- Usage: `python3 scripts/old_to_clean.py`

**CSV to Jekyll Tools Conversion (`scripts/csv_to_tools.py`):**
- Converts cleaned CSV data to Jekyll markdown files with YAML frontmatter
- Supports nested YAML structure generation via dot-notation mapping
- Multi-mapping support: single CSV column → multiple YAML fields
- Ignore unmapped columns option with `--ignore-unmapped` flag
- Usage: `python3 scripts/csv_to_tools.py cleaned_EMA_tools.csv --filename-field tool_name --mapping-file scripts/mapping.txt`

**Field Mapping (`scripts/mapping.txt`):**
- Defines CSV column to YAML field mappings
- Supports nested structures (e.g., `csv_col:metadata.field`)
- Allows multiple mappings for single CSV column
- Comments supported with `#` prefix

## Common Issues

**Filter not working:** Check that field values in `_tools/` files match exactly (case-sensitive) and that arrays are properly formatted with YAML list syntax.

**JavaScript errors:** Ensure all referenced DOM elements exist. The code expects specific IDs like `tools-table`, `no-results`, `clear-filters`.

**Build failures:** Usually related to YAML syntax errors in tool frontmatter. Use `bundle exec jekyll doctor` to check for issues.

**Nested field not displaying:** Ensure the field name uses proper dot notation in `_config.yml` and that templates use the `get_field_value.html` include.

**Value labels not working:** Check that `value_labels` are defined in field config and that templates use the `apply_value_label.html` include.

**Empty CSV/JSON exports:** Exports show template code instead of processed data - ensure Jekyll server is running and download from served URLs, not raw template files.

**Filter dropdowns showing "other" instead of custom labels:** Value labels only affect display in table/detail pages, not filter options (by design for data consistency).

## GitHub Pages Deployment

The site is configured for deployment at `https://ghxm.github.io/esm-tool-overview-static/`:

- `baseurl: "/esm-tool-overview-static"` in `_config.yml`
- JavaScript links use `{{ site.baseurl }}` for proper routing
- View buttons use `{{ tool.url | relative_url }}` filter