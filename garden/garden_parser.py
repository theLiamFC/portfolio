import sys
import os
import re
from datetime import datetime, timedelta

def process_folder(folder_path):
    if folder_path.startswith('/') or folder_path.startswith('\\'):
        folder_path = '.' + folder_path

    txt_filepath = os.path.join(folder_path, 'content.txt')
    html_filepath = os.path.join(folder_path, 'index.html')

    if not os.path.exists(txt_filepath):
        print(f"  -> Error: 'content.txt' not found in directory '{folder_path}'.")
        return False

    with open(txt_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Isolate the metadata block and the content body
    meta_match = re.search(r'/\*(.*?)\*/', content, re.DOTALL)
    if not meta_match:
        print(f"  -> Error: Metadata block /* ... */ not found at the top of '{txt_filepath}'.")
        return False
    
    meta_block = meta_match.group(1)
    body = content[meta_match.end():].strip()

    # 2. Extract the main title and remove it from the body
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled Page"
    body = re.sub(r'^#\s+(.+)$', '', body, count=1, flags=re.MULTILINE).strip()

    # 3. Update the title in the metadata block
    meta_block = re.sub(r'(title:)[^\n]*', rf'\1 {title}', meta_block)

    # 4. Handle the Date Logic & History Extraction
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_date = datetime.strptime(today_str, '%Y-%m-%d')

    def update_dates(date_match):
        date_content = date_match.group(1)
        
        dates_found = re.findall(r'\d{4}-\d{2}-\d{2}', date_content)
        
        if not dates_found:
            return f"date:{{\n        created: {today_str}\n    }}"
        
        latest_date_str = max(dates_found)
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
        
        new_date_content = date_content
        
        if (today_date - latest_date) > timedelta(days=7):
            new_date_content = new_date_content.rstrip() + f"\n        revised: {today_str}\n    "
            
        return f"date:{{{new_date_content}}}"

    meta_block = re.sub(r'date:\s*\{(.*?)\}', update_dates, meta_block, flags=re.DOTALL)

    created_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', meta_block)
    revised_matches = re.findall(r'revised:\s*(\d{4}-\d{2}-\d{2})', meta_block)
    
    created_date = created_match.group(1) if created_match else today_str
    
    if revised_matches:
        most_recent = revised_matches[-1]
        older_revisions = list(reversed(revised_matches[:-1]))
        
        history_lines = []
        for d in older_revisions:
            history_lines.append(f"<li>Revised: <span class='text-neutral-600'>{d}</span></li>")
        history_lines.append(f"<li>Created: <span class='text-neutral-600'>{created_date}</span></li>")
            
        history_html = "\n                            ".join(history_lines)
        
        # This block contains the Tailwind sliding accordion animation
        date_html = f"""
            <div class="group inline-flex flex-col cursor-help">
                <div class="relative z-10 bg-neutral-50 pr-4">
                    <span class="pb-[1px] group-hover:text-neutral-600 transition-colors duration-300">Revised: {most_recent}</span>
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
        date_html = f"<span>Planted: {created_date}</span>"

    # 5. Extract Tags for the HTML Header
    tags_match = re.search(r'tags:\s*\{(.*?)\}', meta_block, re.DOTALL)
    tags_html = ""
    if tags_match:
        tags = [t.strip() for t in tags_match.group(1).split('\n') if t.strip()]
        tag_spans = [f'<span class="bg-neutral-100 text-neutral-600 border border-neutral-200 px-2.5 py-1 rounded-md text-xs tracking-tight font-mono inline-block">{tag}</span>' for tag in tags]
        tags_html = f'<div class="flex flex-wrap gap-2 mb-4">{"".join(tag_spans)}</div>'

    # 6. Overwrite the original content.txt
    new_txt_content = f"/*{meta_block}*/\n\n# {title}\n\n{body}\n"
    with open(txt_filepath, 'w', encoding='utf-8') as f:
        f.write(new_txt_content)

    # 7. Generate the HTML Body
    body = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', body, flags=re.MULTILINE)
    body = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', body, flags=re.MULTILINE)
    body = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', body, flags=re.MULTILINE)
    
    paragraphs = body.split('\n\n')
    html_blocks = []
    
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
            
        if p.startswith('<h1') or p.startswith('<h2') or p.startswith('<h3'):
            html_blocks.append(p)
            continue
            
        lines = p.split('\n')
        block_html = []
        
        in_ul = False
        in_ol = False
        text_buffer = []

        def flush_text():
            if text_buffer:
                block_html.append("<p>" + " ".join(text_buffer) + "</p>")
                text_buffer.clear()

        for line in lines:
            ul_match = re.match(r'^-\s+(.*)', line)
            ol_match = re.match(r'^\d+\.\s+(.*)', line)

            if ul_match:
                flush_text()
                if in_ol:
                    block_html.append("</ol>")
                    in_ol = False
                if not in_ul:
                    block_html.append("<ul>")
                    in_ul = True
                block_html.append(f"  <li>{ul_match.group(1)}</li>")
            elif ol_match:
                flush_text()
                if in_ul:
                    block_html.append("</ul>")
                    in_ul = False
                if not in_ol:
                    block_html.append("<ol>")
                    in_ol = True
                block_html.append(f"  <li>{ol_match.group(1)}</li>")
            else:
                if in_ul:
                    block_html.append("</ul>")
                    in_ul = False
                if in_ol:
                    block_html.append("</ol>")
                    in_ol = False
                text_buffer.append(line)
        
        flush_text()
        if in_ul: block_html.append("</ul>")
        if in_ol: block_html.append("</ol>")

        html_blocks.append('\n'.join(block_html))
    
    final_html_body = '\n'.join(html_blocks)

    # 8. Inject into the final HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <link rel="stylesheet" href="../../style.css">
</head>
<body class="bg-neutral-50 text-neutral-900 selection:bg-blue-200">
    <main class="mx-auto w-full max-w-screen-md px-8 py-12 md:py-20">
        <nav class="mb-12 flex items-center justify-between">
            <a href="../../index.html" class="text-sm font-medium text-neutral-400 hover:text-neutral-900 transition-colors">← Back to Garden</a>
        </nav>
        <header class="mb-10">
            <h1 class="font-serif-custom text-4xl md:text-5xl font-light text-neutral-900 mb-6">{title}</h1>
            {tags_html}
            <div class="font-mono text-xs text-neutral-400 mt-4 tracking-tight">
                {date_html}
            </div>
        </header>
        <hr class="border-neutral-200 mb-10">
        <article class="prose prose-neutral prose-headings:font-serif-custom prose-h1:text-4xl prose-h1:font-light lg:prose-lg">
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
            
        txt_filepath = os.path.join(folder_path, 'content.txt')
        html_filepath = os.path.join(folder_path, 'index.html')
        
        if not os.path.exists(txt_filepath):
            continue
            
        needs_update = False
        
        if not os.path.exists(html_filepath):
            needs_update = True
        elif os.path.getmtime(txt_filepath) > os.path.getmtime(html_filepath):
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