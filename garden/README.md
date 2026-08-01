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
    │   │   └── cover.jpg       # Optional local images
    │   └── /best-coffee
    │
    ├── build_index.py          # Generates the homepage grid
    ├── garden_parser.py        # Converts .md files to .html
    ├── plant.sh                # Script to scaffold new pages
    ├── publish.sh              # Script to build and deploy
    ├── style.css               # Global Tailwind/CSS overrides
    └── index.html              # The generated homepage (do not edit manually)

---

## ✍️ Creating Content

To create a new page, use the `plant.sh` script. This will automatically generate a new folder in `/pages/` and create a `content.md` file with the correct YAML frontmatter and today's date.

**Basic Usage (Blog Post):**
    ./plant.sh folder-name

**Using a Specific Template:**
You can pass a second argument to generate a specific page layout. Currently supported types are `blog` (default) and `institution` (for cafe/restaurant reviews).
    ./plant.sh best-coffee institution

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

When you are done writing or editing, use the `publish.sh` script to compile the Markdown into HTML and update the homepage grid.

**1. Test Locally (No Git Push)**
To build the site and preview it on your local machine without committing changes to your repository:
    ./publish.sh local

**2. Publish to the Web**
To parse all files, build the index, stage the changes, generate a timestamped commit message, and push directly to GitHub:
    ./publish.sh

---

## 🛠️ System Details
*   **Markdown Parsing:** Handled via the Python `markdown` library. Paragraph spacing requires an empty line, and nested lists require exactly 4 spaces of indentation.
*   **Styling:** Powered by Tailwind CSS via CDN, utilizing the `@tailwindcss/typography` plugin for the prose formatting.
*   **Favicon:** Uses an inline, animated SVG (a red circle that slowly fades through Tailwind blue and green over a 15-second loop).