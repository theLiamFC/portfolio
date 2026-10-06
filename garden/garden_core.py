"""Reusable operations for maintaining a Garden project."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import subprocess

from build_index import build_index
from garden_parser import process_all_pages, process_folder


class GardenError(Exception):
    """An actionable error while operating on a Garden project."""


@dataclass(frozen=True)
class BuildResult:
    updated_pages: int
    index_path: Path


def resolve_root(root_dir=None):
    root = Path(root_dir) if root_dir is not None else Path(__file__).resolve().parent
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise GardenError(f"Garden root is not a directory: {root}")
    return root


def available_page_types(root_dir=None):
    root = resolve_root(root_dir)
    templates_dir = root / "templates"
    if not templates_dir.is_dir():
        raise GardenError(f"templates directory not found in '{root}'")
    return sorted(path.stem for path in templates_dir.glob("*.md"))


def plant_page(name, page_type="blog", root_dir=None, force=False):
    root = resolve_root(root_dir)
    if not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", name):
        raise GardenError("page name must be a slug containing letters, numbers, and single hyphens")

    page_types = available_page_types(root)
    if page_type not in page_types:
        choices = ", ".join(page_types)
        raise GardenError(f"unknown page type '{page_type}'. Available types: {choices}")

    template_path = root / "templates" / f"{page_type}.md"
    page_dir = root / "pages" / page_type / name
    content_path = page_dir / "content.md"
    if content_path.exists() and not force:
        raise GardenError(f"page already exists: {content_path} (use --force to replace it)")

    template = template_path.read_text(encoding="utf-8")
    content_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_text(template.replace("{{TODAY}}", date.today().isoformat()), encoding="utf-8")
    return content_path


def build_site(root_dir=None, page=None):
    root = resolve_root(root_dir)
    if page:
        page_parts = Path(page).parts
        if len(page_parts) != 2 or any(part in (".", "..") for part in page_parts):
            raise GardenError("--page must use the form <type>/<page-name>")
        page_path = root / "pages" / page_parts[0] / page_parts[1]
        if not (page_path / "content.md").is_file():
            raise GardenError(f"Garden page not found: {page}")
        process_folder(page_path, root_dir=root)
        updated_pages = 1
    else:
        updated_pages = process_all_pages(root_dir=root)

    index_path = build_index(root_dir=root)
    return BuildResult(updated_pages=updated_pages, index_path=index_path)


def deploy_site(root_dir=None):
    root = resolve_root(root_dir)
    result = build_site(root)
    try:
        repository_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        commit_message = f"Tended garden on {date.today().isoformat()}"
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(["git", "push"], cwd=repository_root, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        command = " ".join(error.cmd) if isinstance(error.cmd, list) else error.cmd
        message = f"command failed: {command}"
        if detail:
            message = f"{message}\n{detail}"
        raise GardenError(message) from error
    return result