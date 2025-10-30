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

## Configuration Reference

**IMPORTANT:** For detailed configuration documentation including field configuration, display contexts, filter setup, and data schema, see the **Configuration** section in `README.md`. Keep that documentation up to date whenever configuration options change.

Key configuration concepts:
- **Display Contexts:** `table`, `detail_overview`, `detail_info`, `detail_publication`
- **Field Types:** `string`, `category`, `array`, `url`, `date`
- **Filter Types:** `select`, `multiselect-and`, `multiselect-or`
- **Publication Fields:** Separate `publication_url` and `publication_citation` fields
- **Automatic Sectioning:** Uncategorized `detail_info` fields appear in "Other" section

## Common Issues

**Filter not working:** Check that field values in `_tools/` files match exactly (case-sensitive) and that arrays are properly formatted with YAML list syntax.

**JavaScript errors:** Ensure all referenced DOM elements exist. The code expects specific IDs like `tools-table`, `no-results`, `clear-filters`.

**Build failures:** Usually related to YAML syntax errors in tool frontmatter. Use `bundle exec jekyll doctor` to check for issues.

## GitHub Pages Deployment

The site is configured for deployment at `https://ghxm.github.io/esm-tool-overview-static/`:

- `baseurl: "/esm-tool-overview-static"` in `_config.yml`
- JavaScript links use `{{ site.baseurl }}` for proper routing
- View buttons use `{{ tool.url | relative_url }}` filter