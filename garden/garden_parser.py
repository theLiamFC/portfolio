import sys
import os
import re
from datetime import datetime, timedelta
import markdown

def process_folder(folder_path):
    if folder_path.startswith('/') or folder_path.startswith('\\'):
        folder_path = '.' + folder_path

    md_filepath = os.path.join(folder_path, 'content.md')
    html_filepath = os.path.join(folder_path, 'index.html')

    if not os.path.exists(md_filepath):
        print(f"  -> Error: 'content.md' not found in directory '{folder_path}'.")
        return False

    with open(md_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Isolate the YAML Frontmatter (---) and the Markdown body
    meta_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not meta_match:
        print(f"  -> Error: YAML Frontmatter (---) not found at top of '{md_filepath}'.")
        return False
    
    frontmatter = meta_match.group(1)
    body = content[meta_match.end():].strip()

    # 2. Extract standard fields
    title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled Page"

    tags_match = re.search(r'^tags:\s*(.+)$', frontmatter, re.MULTILINE)
    tags_html = ""
    if tags_match:
        tags = [t.strip() for t in tags_match.group(1).split(',')]
        tag_spans = [f'<span class="bg-neutral-100 text-neutral-600 border border-neutral-200 px-2.5 py-1 rounded-md text-xs tracking-tight font-mono inline-block">{tag}</span>' for tag in tags]
        tags_html = f'<div class="flex flex-wrap gap-2 mb-4">{"".join(tag_spans)}</div>'

    # STRICT IMAGE CHECK: Verify the file actually exists before generating the <img> tag
    image_match = re.search(r'^image:\s*(.+)$', frontmatter, re.MULTILINE)
    image_html = ""
    if image_match:
        image_filename = image_match.group(1).strip(' "\'')
        if image_filename and image_filename.lower() not in ["", "none", "null"]:
            image_path = os.path.join(folder_path, image_filename)
            if os.path.exists(image_path):
                image_html = f'<img src="{image_filename}" alt="{title}" class="w-full h-64 md:h-96 object-cover rounded-xl mb-10 shadow-sm">'

    # 3. Handle 'Type' branching logic
    type_match = re.search(r'^type:\s*(.+)$', frontmatter, re.MULTILINE)
    page_type = type_match.group(1).strip() if type_match else "blog"

    type_specific_html = ""
    if page_type == "institution":
        # Extract institution-specific metadata
        location_match = re.search(r'^location:\s*(.+)$', frontmatter, re.MULTILINE)
        location = location_match.group(1).strip() if location_match else "Not specified"
        
        rating_match = re.search(r'^rating:\s*(.+)$', frontmatter, re.MULTILINE)
        rating = rating_match.group(1).strip() if rating_match else "Unrated"

        type_specific_html = f"""
        <div class="bg-neutral-100 border border-neutral-200 rounded-lg p-5 mb-8 flex flex-col sm:flex-row gap-4 sm:gap-8 text-sm">
            <div>
                <span class="text-neutral-500 uppercase tracking-wider text-xs block mb-1">Location</span>
                <span class="font-medium text-neutral-900">{location}</span>
            </div>
            <div>
                <span class="text-neutral-500 uppercase tracking-wider text-xs block mb-1">Rating</span>
                <span class="font-medium text-neutral-900">{rating}</span>
            </div>
        </div>
        """

    # 4. Handle Date Logic
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_date = datetime.strptime(today_str, '%Y-%m-%d')
    
    created_match = re.search(r'^created:\s*(\d{4}-\d{2}-\d{2})', frontmatter, re.MULTILINE)
    created_str = created_match.group(1) if created_match else today_str
    created_date = datetime.strptime(created_str, '%Y-%m-%d')

    revised_matches = re.findall(r'^revised:\s*(\d{4}-\d{2}-\d{2})', frontmatter, re.MULTILINE)
    
    if not revised_matches and (today_date - created_date) > timedelta(days=7):
        frontmatter += f"\nrevised: {today_str}"
        revised_matches.append(today_str)
    elif revised_matches:
        latest_revised = datetime.strptime(revised_matches[-1], '%Y-%m-%d')
        if (today_date - latest_revised) > timedelta(days=7):
            frontmatter += f"\nrevised: {today_str}"
            revised_matches.append(today_str)

    if revised_matches:
        most_recent = revised_matches[-1]
        older_revisions = list(reversed(revised_matches[:-1]))
        
        history_lines = [f"<li>Tended: <span class='text-neutral-600'>{d}</span></li>" for d in older_revisions]
        history_lines.append(f"<li>Planted: <span class='text-neutral-600'>{created_str}</span></li>")
        history_html = "\n                            ".join(history_lines)
        
        date_html = f"""
            <div class="group inline-flex flex-col cursor-help">
                <div class="relative z-10 bg-neutral-50 pr-4">
                    <span class="group-hover:text-neutral-600 transition-colors duration-300">Tended: {most_recent}</span>
                </div>
                <div class="grid grid-rows-[0fr] group-hover:grid-rows-[1fr] transition-[grid-template-rows] duration-500 ease-out">
                    <div class="overflow-hidden">
                        <ul class="flex flex-col gap-1.5 pt-3 pb-2 text-neutral-400 opacity-0 -translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-500 ease-out">
                            {history_html}
                        </ul>
                    </div>
                </div>
            </div>"""
    else:
        date_html = f"<span>Planted: {created_str}</span>"

    # 5. Overwrite the original .md file to lock in any new revision dates
    new_md_content = f"---\n{frontmatter}\n---\n\n{body}\n"
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(new_md_content)

    # 6. Pre-process Custom Garden Links `[display]((folder-name))`
    body = re.sub(r'\[(.*?)\]\(\((.*?)\)\)', r'[\1](../\2/index.html)', body)

    # 7. Convert Markdown to HTML
    final_html_body = markdown.markdown(body)

    # 8. Inject into the final HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='%23ef4444'><animate attributeName='fill' values='%23ef4444;%233b82f6;%2310b981;%23ef4444' dur='15s' repeatCount='indefinite'/></circle></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <link rel="stylesheet" href="../../style.css">
</head>
<body class="bg-neutral-50 text-neutral-900 selection:bg-red-200">
    <main class="mx-auto w-full max-w-screen-md px-8 py-12 md:py-20">
        <nav class="mb-12 flex items-center justify-between">
            <a href="../../index.html" class="text-sm font-medium text-neutral-400 hover:text-red-500 transition-colors">← Back to Garden</a>
        </nav>
        
        <header class="mb-10">
            <h1 class="text-4xl md:text-5xl font-light text-neutral-900 mb-6">{title}</h1>
            {tags_html}
            <div class="font-mono text-xs text-neutral-400 mt-4 tracking-tight">
                {date_html}
            </div>
        </header>

        {image_html}
        
        <hr class="border-neutral-200 mb-10">
        
        {type_specific_html}

        <article class="prose prose-neutral prose-h1:text-4xl prose-h1:font-light lg:prose-lg prose-a:text-red-500 prose-a:hover:text-red-600 prose-a:transition-colors prose-a:no-underline">
            {final_html_body}
        </article>
        
    </main>
</body>
</html>"""

    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    return True

def process_all_pages(base_dir='pages'):
    if not os.path.exists(base_dir):
        print(f"Error: Directory '{base_dir}' not found.")
        return

    updated_count = 0
    
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        
        if not os.path.isdir(folder_path):
            continue
            
        md_filepath = os.path.join(folder_path, 'content.md')
        html_filepath = os.path.join(folder_path, 'index.html')
        
        if not os.path.exists(md_filepath):
            continue
            
        needs_update = False
        
        if not os.path.exists(html_filepath):
            needs_update = True
        elif os.path.getmtime(md_filepath) > os.path.getmtime(html_filepath):
            needs_update = True
            
        if needs_update:
            print(f"Parsing updated page: {folder_name}...")
            if process_folder(folder_path):
                updated_count += 1
                
    if updated_count == 0:
        print("All pages are up to date! No changes made.")
    else:
        print(f"Finished! Successfully parsed {updated_count} page(s).")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_to_process = sys.argv[1]
        print(f"Forcing parse on: {folder_to_process}...")
        process_folder(folder_to_process)
        print("Done!")
    else:
        print("Scanning garden for updates...")
        process_all_pages()