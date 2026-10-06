# 🌱 Liam's Digital Garden

A custom, lightweight Static Site Generator (SSG) built with Python and Shell scripts. It converts Markdown files into styled HTML, handles internal wiki-style linking, manages automatic revision dates, and deploys directly to GitHub Pages.

---

## 📂 Folder Structure

    /garden
    │
    ├── /pages                  # Contains all your garden notes
    │   ├── /the-seed           # Each page gets its own folder
    │   │   ├── content.md      # The raw markdown file
    │   │   ├── index.html      # The generated HTML (do not edit manually)
    │   └── └── cover.jpg       # Optional local images
    │
    ├── garden_cli.py           # Command-line entry point
    ├── garden_core.py          # Reusable garden operations
    ├── build_index.py          # Generates the homepage grid
    ├── garden_parser.py        # Converts .md files to .html
    ├── plant.sh                # Compatibility wrapper for `garden plant`
    ├── publish.sh              # Compatibility wrapper for build/deploy
    ├── pyproject.toml          # Python package and CLI metadata
    ├── style.css               # Global Tailwind/CSS overrides
    └── index.html              # The generated homepage (do not edit manually)

---

## ✍️ Creating Content

Install the command from this directory with `python3 -m pip install -e .`. The install is editable so the command continues to use this Garden's templates and pages. Run `garden --help` (or `garden -help`) to see available commands.

To create a new page, use `garden plant`. This creates a folder in `/pages/` and a `content.md` file from the selected template with today's date.

**Basic Usage (Blog Post):**
    garden plant folder-name

**Using a Specific Template:**
Pass `--type` to select any available template, such as `media`, `recipe`, or `adventure`.
    garden plant best-coffee --type place

Use `--force` only when you intend to replace an existing page's `content.md`.
    garden plant folder-name --force

---

## 📝 Formatting & Frontmatter

Your pages are driven by standard Markdown and YAML Frontmatter. The Python scripts strictly read the frontmatter block at the top of `content.md` to build the site.

### The Frontmatter Block
    ---
    title: The Seed
    description: A quick summary of this page.
    created: 2026-07-30
    tags: Field Notes, Engineering
    image: cover.jpg
    type: blog
    ---

*   **`image` (Optional):** Drop an image file into the same folder as your `content.md` and put the exact filename here. The parser will automatically generate a Hero Image on the page and an Image Card on the homepage. If left blank, it defaults to a clean white text card.
*   **`type` (Optional):** Determines the HTML template. If set to `institution`, the parser will also look for `location:` and `rating:` tags to build a custom info card.
*   **`revised` (Automatic):** You do not need to add this! The parser will automatically append a new revision date if you edit the file more than 7 days after its creation/last edit, generating a sliding date accordion on the page.

### Internal Linking
To link to other pages within your garden, use the custom double-parentheses syntax. This prevents standard Markdown links from breaking while keeping your writing flow natural.

**Syntax:** `[Display Text]((folder-name))`

**Example:** 
    I have been spending too much time dialing in my [espresso setup]((espresso-setup)).

*The parser automatically intercepts this and routes it to `../espresso-setup/index.html`.*

---

## 🚀 Building and Publishing

When you are done writing or editing, build the Garden to compile Markdown pages and update the homepage grid.

**Build locally (no Git operations):**
    garden build

To rebuild one page and the homepage:
    garden build --page media/open-task-light

**Deploy**
Deploy rebuilds, stages Garden changes, creates a dated commit, and pushes to the configured Git remote:
    garden deploy

The existing shell commands remain available as wrappers: `./plant.sh page-name media`, `./publish.sh local`, and `./publish.sh` (deploy).

### Python API

The operations are also importable from `garden_core`:

```python
from garden_core import build_site, plant_page

page_path = plant_page("field-note", page_type="blog")
result = build_site()
```

Pass `root_dir="/path/to/garden"` to operate on a different Garden project. `build_site` returns a result with the number of updated pages and the generated homepage path. Errors are raised as `GardenError` (or standard filesystem/value errors).

---

## 🛠️ System Details
*   **Markdown Parsing:** Handled via the Python `markdown` library. Paragraph spacing requires an empty line, and nested lists require exactly 4 spaces of indentation.
*   **Styling:** Powered by Tailwind CSS via CDN, utilizing the `@tailwindcss/typography` plugin for the prose formatting.
*   **Favicon:** Uses an inline, animated SVG (a red circle that slowly fades through Tailwind blue and green over a 15-second loop).