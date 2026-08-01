#!/bin/bash

# Check if a folder name was provided
if [ -z "$1" ]; then
  echo "Error: Please provide a folder name."
  echo "Usage: ./plant.sh <folder_name> [type]"
  exit 1
fi

FOLDER="pages/$1"
FILE="$FOLDER/content.md"
TODAY=$(date +'%Y-%m-%d')

# Read the second argument as the type, default to 'blog' if missing
TYPE=${2:-blog}

mkdir -p "$FOLDER"

# Generate different markdown templates based on the type
if [ "$TYPE" = "institution" ]; then
cat <<EOF > "$FILE"
---
title: 
description: 
created: $TODAY
tags: 
image: 
type: institution
location: 
rating: 
---

## The Vibe


## What to Order


EOF
else
cat <<EOF > "$FILE"
---
title: 
description: 
created: $TODAY
tags: 
image: 
type: blog
---

Write your new thoughts here...
EOF
fi

echo "🌱 Successfully planted a new $TYPE page at: $FILE"