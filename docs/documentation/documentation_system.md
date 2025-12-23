# Documentation System (MkDocs)

This project uses **MkDocs** to generate a static documentation site from Markdown files. This ensures that technical documentation is treated as code, versioned alongside the software, and easily readable.

## What is MkDocs?
**MkDocs** is a fast, simple, and downright gorgeous static site generator that's geared towards building project documentation. Documentation source files are written in Markdown, and configured with a single YAML configuration file.

We rely on **Material for MkDocs**, a theme that provides a modern, responsive, and mobile-friendly interface.

## Implementation Details

### Directory Structure
To make MkDocs work effectively, we structured the project as follows:

```text
cryptoflow/
├── mkdocs.yml            # Main configuration file
├── docs/                 # Root of the documentation site
│   ├── index.md          # Homepage
│   ├── README.md         # Symlinked/Copied project README
│   └── documentation/    # Deep-dive guides
│       ├── microservices_theory.md
│       ├── grpc_implementation_guide.md
│       └── documentation_system.md
```

### Configuration (`mkdocs.yml`)
The `mkdocs.yml` file is the heart of the configuration.
-   **Theme**: Sets the look and feel (Material theme).
-   **Palette**: Defines primary (Indigo) and accent (Cyan) colors.
-   **Nav**: Explicitly defines the left-hand navigation menu structure.

## How to Work with Documentation

### 1. writing documentation
Simply create or edit `.md` files in the `docs/` directory. Standard Markdown syntax applies.

### 2. Previewing Locally
To see your changes live:
```bash
./venv/bin/mkdocs serve
```
This starts a local web server (usually at `http://127.0.0.1:8000`) that auto-reloads whenever you save a file.

### 3. Building for Production
To generate a static HTML site (e.g., for deployment to GitHub Pages):
```bash
mkdocs build
```
This creates a `site/` directory containing the full HTML/CSS/JS ready for hosting.
