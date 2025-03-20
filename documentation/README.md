 # Mantis AI Documentation

This directory contains the documentation for the Mantis AI project, built using MkDocs Material.

## Local Development

To work on the documentation locally:

1. Install the required dependencies:
   ```bash
   pip install mkdocs-material
   ```

2. Start the development server:
   ```bash
   mkdocs serve
   ```

3. Build the documentation:
   ```bash
   mkdocs build
   ```

## Deployment

The documentation is automatically deployed to Cloudflare Pages when changes are pushed to the `main` branch. The deployment is handled by the GitHub Actions workflow in `.github/workflows/deploy-docs.yml`.

## Structure

- `docs/` - Contains all the documentation source files in Markdown format
- `mkdocs.yml` - Configuration file for MkDocs
- `site/` - Generated documentation site (created when building)

## Adding New Content

1. Add new Markdown files to the `docs/` directory
2. Update the navigation in `mkdocs.yml` to include the new pages
3. Commit and push your changes to trigger the automatic deployment