#!/bin/bash

echo "🌱 Parsing markdown files..."
python garden_parser.py

echo "🏗️ Building the garden grid..."
python build_index.py

# Check if the 'local' flag was passed
if [ "$1" = "local" ]; then
  echo "🛑 Local flag detected. Skipping Git commit and push."
  echo "🌻 Local garden built successfully!"
  exit 0
fi

echo "📦 Adding files to Git..."
git add .

# Uses the current date and time as the commit message
echo "📝 Committing changes..."
git commit -m "Tended garden on $(date +'%Y-%m-%d %H:%M')"

echo "🚀 Pushing to GitHub..."
git push

echo "🌻 Garden published successfully!"