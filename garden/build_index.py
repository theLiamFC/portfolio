import os
import re
import random

def build_index():
    pages_dir = 'pages'
    
    if not os.path.exists(pages_dir):
        print(f"Error: '{pages_dir}' directory not found.")
        return

    generated_cards = []

    # 1. Loop through all page folders in the /pages/ directory
    for folder_name in os.listdir(pages_dir):
        folder_path = os.path.join(pages_dir, folder_name)
        md_filepath = os.path.join(folder_path, 'content.md')
        
        # Skip if it's not a folder or doesn't have a content.md
        if not os.path.isdir(folder_path) or not os.path.exists(md_filepath):
            continue

        with open(md_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. Extract YAML Frontmatter
        meta_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not meta_match:
            continue
        frontmatter = meta_match.group(1)

        # 3. Extract Specific Fields from YAML
        title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled Page"

        desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
        description = desc_match.group(1).strip() if desc_match else ""

        tags_match = re.search(r'^tags:\s*(.+)$', frontmatter, re.MULTILINE)
        tag_html = ""
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split(',') if t.strip()]
            if tags:
                tag_html = f"<span>{tags[0]}</span>"

        # Check for a cover image
        image_match = re.search(r'^image:\s*(.+)$', frontmatter, re.MULTILINE)
        image_filename = image_match.group(1).strip() if image_match else None

        # 4. Generate the HTML for this specific card
        if image_filename:
            # Render an Image Card
            image_path = f"pages/{folder_name}/{image_filename}"
            card_html = f"""
            <div class="aspect-square p-2">
                <a href="pages/{folder_name}/index.html" class="group relative block h-full w-full overflow-hidden rounded-xl bg-neutral-100">
                    <img src="{image_path}" alt="{title}" class="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
                    <div class="relative flex h-full flex-col justify-between p-6 z-10">
                        <div class="flex items-center justify-between text-sm tracking-tight text-white/90">
                            {tag_html}
                        </div>
                        <div>
                            <h3 class="font-serif-custom text-3xl font-light text-white">{title}</h3>
                            <p class="mt-2 text-sm text-white/80 line-clamp-2">{description}</p>
                        </div>
                    </div>
                </a>
            </div>"""
        else:
            # Render a Standard Text Card
            card_html = f"""
            <div class="aspect-square p-2">
                <a href="pages/{folder_name}/index.html" class="group block h-full w-full overflow-hidden rounded-xl bg-neutral-50 transition-colors hover:bg-neutral-100 border border-transparent hover:border-neutral-200">
                    <div class="flex h-full flex-col justify-between p-6">
                        <div class="flex items-center justify-between text-sm tracking-tight text-neutral-400">
                            {tag_html}
                        </div>
                        <div>
                            <h3 class="font-serif-custom text-3xl font-light text-neutral-900">{title}</h3>
                            <p class="mt-2 text-sm text-neutral-500 line-clamp-3">{description}</p>
                        </div>
                    </div>
                </a>
            </div>"""
            
        generated_cards.append(card_html)

    # 5. Algorithmically randomize the output
    random.shuffle(generated_cards)
    
    # Combine all cards into one string
    all_cards_html = "\n".join(generated_cards)

    # 6. Inject into the main Garden Index Template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <title>Liam's Garden</title>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    
    <!-- Animated Red Circle Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='%23ef4444'><animate attributeName='fill' values='%23ef4444;%233b82f6;%2310b981;%23ef4444' dur='6s' repeatCount='indefinite'/></circle></svg>">
    
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
                <a href="https://github.com/" class="text-sm tracking-tight text-neutral-400 hover:text-neutral-900 transition-colors underline decoration-wavy underline-offset-4">GitHub</a>
                <a href="#" class="text-sm tracking-tight text-neutral-400 hover:text-neutral-900 transition-colors underline decoration-wavy underline-offset-4">Resume</a>
            </div>
        </nav>

        <div class="mt-8 grid grid-cols-1 gap-4 sm:grid-flow-row-dense sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            
            <!-- Hero / Intro Section -->
            <div class="row-span-2 sm:col-span-2 lg:aspect-square p-2">
                <div class="h-full w-full p-6 sm:p-8 rounded-xl bg-neutral-50">
                    <h1 class="font-serif-custom text-3xl font-light leading-snug text-neutral-500 sm:text-4xl lg:text-5xl">
                        Hey there, I’m <span class="text-neutral-900 font-medium">Liam</span> 👋 <br><br>
                        Welcome to my digital garden 🌱. <br><br>
                        I'm a robotics engineer currently building at <a href="#" class="text-red-500 hover:text-red-600 transition-colors underline decoration-wavy underline-offset-4">EraDrive</a>. <br><br>
                        In my free time, I enjoy dialing in my <a href="#" class="text-red-500 hover:text-red-600 transition-colors underline decoration-wavy underline-offset-4">espresso</a> setup, shooting <a href="#" class="text-red-500 hover:text-red-600 transition-colors underline decoration-wavy underline-offset-4">B&W film</a>, and spending time <a href="#" class="text-red-500 hover:text-red-600 transition-colors underline decoration-wavy underline-offset-4">outdoors</a> surfing and skiing.
                    </h1>
                </div>
            </div>

            <!-- Dynamically Populated Cards -->
            {all_cards_html}

        </div>

        <footer class="mt-24 mb-12 flex justify-center">
            <span class="text-sm tracking-tight text-neutral-400">Tended by Liam Campbell</span>
        </footer>

    </main>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Success! Built garden index.html with {len(generated_cards)} cards.")

if __name__ == "__main__":
    build_index()