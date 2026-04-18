# Chroma Admin CLI

A powerful, interactive command-line interface (TUI) for ChromaDB administration and data exploration. 

## ✨ Features
* **Interactive TUI:** Navigate through collections, inspect chunks, and return to menus continuously using your keyboard arrows.
* **Embedding Previews:** Safely preview high-dimensional vectors without flooding your terminal screen.
* **Multi-Tenant Support:** Easily switch between different tenants and databases on the fly.
* **Persistent Configuration:** Set your host URL and credentials once and forget about them.

## 🚀 Installation

We recommend using `pipx` to install the CLI globally in an isolated environment:

1. **Install pipx** (if you haven't already):
   * **Mac:** `brew install pipx`
   * **Windows:** `python -m pip install --user pipx`
   * **Linux:** `sudo apt install pipx`
   *(Note: Run `pipx ensurepath` after installation to register global commands).*

2. **Install the CLI:**
   `pipx install git+https://github.com/Pedro-Marquardt/chroma-admin-cli.git`

## 🛠️ How to Use

### 1. Initial Setup
Configure your database host, user, and password. You only need to run this once.
`chroma-cli config`

### 2. Interactive Exploration
Launch the interactive terminal UI to browse collections, read document texts, and inspect metadata.
`chroma-cli explore`

### 3. Filtering Chunks by Metadata
Interactively browse only the chunks of a specific collection, optionally filtering by metadata key and value. For example, to filter by a filename:
```
chroma-cli filter-chunks --collection COLLECTION_NAME --metadata-key filename --metadata-value "myfile.pdf"
```
You can also specify tenant and database:
```
chroma-cli filter-chunks --collection COLLECTION_NAME --tenant TENANT_ID --database DATABASE_ID --metadata-key filename --metadata-value "myfile.pdf"
```
If you omit the metadata filter, all chunks from the collection will be listed for navigation.

### 4. Using Custom Tenants and Databases
By default, the CLI connects to `default_tenant` and `default_database`. If your ChromaDB instance uses custom namespaces, you can pass them as flags:
`chroma-cli explore --tenant "2a73d61d-a7de-4f06-89c1-4f65e066debe" --database "88a9e3ab-7d12-46b7-9dbd-2a7b126924c5"`

To see all available commands and options at any time, run:
`chroma-cli --help`

## ⚠️ Compatibility & Troubleshooting

This CLI leverages modern ChromaDB API features and is designed to work with **ChromaDB Server versions 1.5.x and newer**.

**Troubleshooting JSON API Errors:**
If you experience a `KeyError: '_type'` or sudden crashes when exploring collections, it means your target ChromaDB server is running an outdated, legacy version (such as `0.4.x`). 

To resolve this, **you must upgrade your ChromaDB server container/instance** to a modern version (`1.5.0` or higher). This CLI does not support connecting to deprecated server versions.