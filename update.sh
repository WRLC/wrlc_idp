#!/bin/bash

# Ensure you are on the correct branch or create one
# For example:
git checkout -b update/$(date +%Y-%m-%d)

# Get outdated packages, excluding the header and formatting lines
outdated_packages=$(poetry show --outdated | awk 'NR > 2 && NF > 0 {print $1}')

if [ -z "$outdated_packages" ]; then
  echo "No packages to update."
  exit 0
fi

echo "The following packages will be updated:"
echo "$outdated_packages"
echo ""

# Loop through each outdated package and update it
for package_name in $outdated_packages; do
  echo "Updating $package_name..."
  poetry update "$package_name"

  if [ $? -ne 0 ]; then
    echo "Error updating $package_name. Skipping."
    continue
  fi

  echo "Updating requirements.txt..."
  poetry run pip freeze > requirements.txt

  echo "Committing changes for $package_name..."
  git add pyproject.toml poetry.lock requirements.txt
  git commit -m "Update $package_name"

  if [ $? -ne 0 ]; then
    echo "Error committing changes for $package_name. Please check git status."
    exit 1
  fi

  echo "$package_name updated and committed."
  echo ""
done

echo "All packages updated."
# You can add your git push command here if desired
git push -u origin update/$(date +%Y-%m-%d)