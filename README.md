# ESM Tool Overview - Jekyll Static Site

A Jekyll-based static website version of https://github.com/gesiscss/ESM_tool_overview.


## Getting Started

### Prerequisites

- Ruby 2.7+ 
- Bundler gem

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd esm-tool-overview-static
   ```

2. **Install dependencies**
   ```bash
   bundle install
   ```

3. **Serve locally**
   ```bash
   bundle exec jekyll serve
   ```

4. **View the site**
   Open http://localhost:4000 in your browser


## Configuration

### Site Configuration (`_config.yml`)

The site behavior is controlled by several configuration sections in `_config.yml`:

#### Default Empty Value
```yaml
default_empty_value: "-"
```
Sets the default value displayed when a field is empty. Can be overridden per field.

#### Detail Page Sections
```yaml
detail_info_sections:
  - name: "Basic Information"
    fields: ["category", "pricing"]
  - name: "Technical Details" 
    fields: ["components", "sensor_data_types"]
  - name: "Metadata"
    fields: ["license", "last_updated"]
```
Defines how fields are grouped in the "Tool Information" box on detail pages. Fields marked with `display: ["detail_info"]` but not listed in any section will automatically appear in an "Other" section.

#### Field Configuration
Fields are configured under the `fields:` section with the following properties:

**Display Contexts:**
- `"table"` - Show in main overview table
- `"detail_overview"` - Show in overview sidebar on detail pages
- `"detail_info"` - Show in tool information sections on detail pages  
- `"detail_publication"` - Show in publication section on detail pages

**Field Properties:**
- `label` - Display name for the field
- `type` - Field type (`string`, `array`, `category`, `url`, `date`)
- `display` - Array of display contexts where field appears
- `display_style` - Visual style (`"badge"` for category fields)
- `sortable` - Whether table column is sortable (boolean)
- `show_if_empty` - Show field even when empty (boolean)
- `empty_value` - Custom empty value (overrides `default_empty_value`)
- `tooltip` - Help text shown on hover
- `filter` - Filter configuration for table view

**Filter Configuration:**
```yaml
filter:
  display: true/false          # Show filter for this field
  type: "select"               # Single-select dropdown
        "multiselect-and"      # Multi-select (ALL must match)
        "multiselect-or"       # Multi-select (ANY can match)
  label: "Custom Filter Label" # Override field label for filter
```

#### Publication Fields
Two separate fields handle publications:
- `publication_url` - Link shown in overview sidebar
- `publication_citation` - Bibliographical reference with copy-to-clipboard functionality

### Adding New Tools

1. Create a new file in `_tools/` with `.md` extension
2. Add YAML frontmatter with tool metadata
3. Optionally add markdown content for detailed description
4. Set `output: false` to hide tool from listings

Example tool file:
```yaml
---
layout: tool
name: "Example Tool"
description: "Tool description"
category: "Platform"
pricing: "Free"
components: ["Web Interface", "Mobile App"]
sensor_data_types: ["GPS", "Accelerometer"]
maintainer: "Organization Name"
link: "https://example.com"
publication_url: "https://doi.org/10.1234/example"
publication_citation: "Author, A. (2024). Example Tool. Journal Name, 1(1), 1-10."
license: "MIT"
last_updated: "2024-01-01"
tags: ["research", "data-collection"]
---

Optional detailed description content in markdown format.
```

   
## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your tools or improvements
4. Submit a pull request
