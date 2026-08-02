#!/bin/bash

# Check if a folder name was provided
if [ -z "$1" ]; then
  echo "Error: Please provide a folder name."
  echo "Usage: ./plant.sh <folder_name> [type]"
  exit 1
fi

TODAY=$(date +'%Y-%m-%d')
TYPE=${2:-blog}

# NEW: The folder path now nests inside the TYPE category
FOLDER="pages/${TYPE}/$1"
FILE="$FOLDER/content.md"
TEMPLATE="templates/${TYPE}.md"

# Check if the requested template actually exists
if [ ! -f "$TEMPLATE" ]; then
  echo "❌ Error: Template file '$TEMPLATE' does not exist."
  echo "Please create it or specify a valid type."
  exit 1
fi

# Creates the category folder and the page folder simultaneously
mkdir -p "$FOLDER"

# Copy the template and swap the {{TODAY}} placeholder with the actual date
sed "s/{{TODAY}}/$TODAY/g" "$TEMPLATE" > "$FILE"

echo "🌱 Successfully planted a new $TYPE page at: $FILE"