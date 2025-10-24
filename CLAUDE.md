# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

**Configuration-Driven Filters:** The table columns and filter types are defined in `_config.yml` under `table_columns`. This allows dynamic generation of filters without code changes.

**Hybrid Filtering System:** Uses List.js for basic search/sort functionality but implements custom JavaScript for complex multiselect filters with AND/OR logic.

### Key Components

**Main Table (`index.html`):**
- Dynamically generates filter controls from `_config.yml` configuration
- Implements three filter types: `select`, `multiselect-and`, `multiselect-or`
- Uses List.js for search and sorting, custom JS for filtering
- Handles edge cases like "no results" display

**Tool Collection (`_tools/`):**
- Jekyll collection with permalink structure `/tools/:name/`
- Each markdown file has frontmatter with tool metadata
- Supports arrays for `components` and `sensor_data_types` fields

**Dynamic Filter Generation:**
- Filters are generated in Liquid templates based on `_config.yml`
- Multiselect filters use Bootstrap dropdowns with checkboxes
- Filter state management handled in JavaScript

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

## Data Schema

Tools in `_tools/` must include:
- `layout: tool` (required)
- `name`, `description`, `category` (required fields)
- `pricing`, `components`, `sensor_data_types` (recommended arrays)

## Filter Configuration

Add new filters by updating `_config.yml`:

```yaml
table_columns:
  - name: "Field Name"
    field: "field_name"
    filter:
      type: "select|multiselect-and|multiselect-or"
      label: "Display Label"
```

Filter types:
- `select`: Single-value dropdown
- `multiselect-and`: All selected values must be present in tool
- `multiselect-or`: Any selected value can be present in tool

## Common Issues

**Filter not working:** Check that field values in `_tools/` files match exactly (case-sensitive) and that arrays are properly formatted with YAML list syntax.

**JavaScript errors:** Ensure all referenced DOM elements exist. The code expects specific IDs like `tools-table`, `no-results`, `clear-filters`.

**Build failures:** Usually related to YAML syntax errors in tool frontmatter. Use `bundle exec jekyll doctor` to check for issues.