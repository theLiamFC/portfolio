"""Command-line interface for the Garden project."""

import argparse
from pathlib import Path
import sys

from garden_core import GardenError, available_page_types, build_site, deploy_site, plant_page, resolve_root


def create_parser():
    parser = argparse.ArgumentParser(prog="garden", add_help=False)
    parser.add_argument("-h", "--help", "-help", action="help", help="show this help message and exit")
    parser.add_argument("--root", type=Path, help="Garden project directory (defaults to this installation)")
    commands = parser.add_subparsers(dest="command", required=True)

    plant = commands.add_parser("plant", help="create a page from a template")
    plant.add_argument("name", help="new page slug, for example my-field-note")
    plant.add_argument("--type", default="blog", help="page template type (default: blog)")
    plant.add_argument("--force", action="store_true", help="replace an existing page content file")

    build = commands.add_parser("build", help="generate Garden pages and the homepage")
    build.add_argument("--page", help="rebuild one page using <type>/<page-name>")

    commands.add_parser("deploy", help="build, commit Garden changes, and push them")
    return parser


def main(argv=None):
    parser = create_parser()
    args = parser.parse_args(argv)
    try:
        root = resolve_root(args.root)
        if args.command == "plant":
            page_types = available_page_types(root)
            if args.type not in page_types:
                raise GardenError(f"unknown page type '{args.type}'. Available types: {', '.join(page_types)}")
            content_path = plant_page(args.name, args.type, root_dir=root, force=args.force)
            print(f"Planted page: {content_path.relative_to(root)}")
        elif args.command == "build":
            result = build_site(root, page=args.page)
            print(f"Built Garden: {result.updated_pages} page(s) updated; homepage: {result.index_path}")
        else:
            result = deploy_site(root)
            print(f"Deployed Garden: homepage generated at {result.index_path}")
    except (GardenError, OSError, ValueError) as error:
        print(f"garden: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())