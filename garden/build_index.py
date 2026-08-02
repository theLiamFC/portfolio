import os
import re
import random

def build_index():
    pages_dir = 'pages'
    
    if not os.path.exists(pages_dir):
        print(f"Error: '{pages_dir}' directory not found.")
        return

    generated_cards = []

    # NEW: Loop through Category folders first
    for category_name in os.listdir(pages_dir):
        category_path = os.path.join(pages_dir, category_name)
        
        if not os.path.isdir(category_path):
            continue

        # Loop through Page folders inside the Category
        for folder_name in os.listdir(category_path):
            folder_path = os.path.join(category_path, folder_name)
            md_filepath = os.path.join(folder_path, 'content.md')
            
            if not os.path.isdir(folder_path) or not os.path.exists(md_filepath):
                continue

            with open(md_filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            meta_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not meta_match:
                continue
            frontmatter = meta_match.group(1)

            title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else "Untitled"

            desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
            description = desc_match.group(1).strip() if desc_match else ""

            tags_match = re.search(r'^tags:\s*(.+)$', frontmatter, re.MULTILINE)
            tag_html = ""
            if tags_match:
                tags = [t.strip() for t in tags_match.group(1).split(',') if t.strip()]
                if tags:
                    tag_html = f"<span>{tags[0]}</span>"

            type_match = re.search(r'^type:\s*(.+)$', frontmatter, re.MULTILINE)
            page_type = type_match.group(1).strip() if type_match else "blog"

            image_match = re.search(r'^image:\s*(.+)$', frontmatter, re.MULTILINE)
            image_filename = image_match.group(1).strip(' "\'') if image_match else ""
            
            image_exists = False
            if image_filename and image_filename.lower() not in ["", "none", "null"]:
                image_path = os.path.join(folder_path, image_filename)
                if os.path.exists(image_path):
                    image_exists = True

            if page_type == "photo" and image_exists:
                card_html = f"""
                <div class="aspect-square p-2">
                    <a href="{folder_path}/index.html" class="group relative block h-full w-full overflow-hidden rounded-xl bg-neutral-100">
                        <img src="{image_path}" class="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105">
                    </a>
                </div>"""
            elif image_exists:
                card_html = f"""
                <div class="aspect-square p-2">
                    <a href="{folder_path}/index.html" class="group relative block h-full w-full overflow-hidden rounded-xl bg-neutral-100">
                        <img src="{image_path}" alt="{title}" class="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105">
                        <div class="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent"></div>
                        <div class="relative flex h-full flex-col justify-between p-6 z-10">
                            <div class="flex items-center justify-between text-sm tracking-tight text-white/90">
                                {tag_html}
                            </div>
                            <div>
                                <h3 class="text-3xl font-light text-white drop-shadow-md">{title}</h3>
                                <p class="mt-2 text-sm text-white/90 line-clamp-2 drop-shadow-md">{description}</p>
                            </div>
                        </div>
                    </a>
                </div>"""
            else:
                card_html = f"""
                <div class="aspect-square p-2">
                    <a href="{folder_path}/index.html" class="group block h-full w-full overflow-hidden rounded-xl bg-white transition-colors hover:bg-neutral-50 border border-neutral-200">
                        <div class="flex h-full flex-col justify-between p-6">
                            <div class="flex items-center justify-between text-sm tracking-tight text-neutral-400">
                                {tag_html}
                            </div>
                            <div>
                                <h3 class="text-3xl font-light text-neutral-900">{title}</h3>
                                <p class="mt-2 text-sm text-neutral-500 line-clamp-3">{description}</p>
                            </div>
                        </div>
                    </a>
                </div>"""
                
            generated_cards.append(card_html)

    random.shuffle(generated_cards)
    all_cards_html = "\n".join(generated_cards)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <title>Liam's Garden</title>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='%23ef4444'><animate attributeName='fill' values='%23ef4444;%233b82f6;%2310b981;%23ef4444' dur='15s' repeatCount='indefinite'/></circle></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="style.css">
</head>
<body class="bg-white selection:bg-red-200">
    <main class="mx-auto w-full max-w-screen-sm px-8 md:max-w-screen-md lg:max-w-screen-lg xl:max-w-screen-xl">
        
        <nav class="sticky top-0 z-10 flex items-center justify-between py-4 bg-white/80 backdrop-blur-md">
            <div class="flex rounded-lg border border-neutral-200 bg-white p-1 shadow-sm">
                <a class="rounded py-1 px-3 text-sm tracking-tight text-neutral-900 font-medium hover:bg-neutral-100 transition-colors" href="https://liamfcampbell.com">Liam Campbell</a>
                <a class="rounded py-1 px-3 text-sm tracking-tight text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100 transition-colors" href="/garden">Garden</a>
            </div>
            <div class="hidden md:flex gap-4">
                <a href="https://github.com/" class="text-sm tracking-tight text-neutral-400 hover:text-neutral-900 transition-colors">GitHub</a>
                <a href="#" class="text-sm tracking-tight text-neutral-400 hover:text-neutral-900 transition-colors">Resume</a>
            </div>
        </nav>

        <section class="min-h-[80vh] flex flex-col justify-center py-12 px-2">
            <h1 class="text-4xl font-light leading-snug text-neutral-500 md:text-5xl lg:text-6xl lg:leading-tight">
                Hello, I'm <span class="text-neutral-900 font-medium">Liam</span>.<br><br>
                Welcome to my digital garden.
            </h1>
        </section>

        <div class="grid grid-cols-1 gap-4 sm:grid-flow-row-dense sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {all_cards_html}
        </div>

        <footer class="mt-32 mb-12 flex justify-center">
            <span class="text-sm tracking-tight text-neutral-400">Tended by Liam Campbell</span>
        </footer>

    </main>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    build_index()