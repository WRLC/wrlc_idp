#!/bin/bash

# Ensure you are on the correct branch or create one
# For example:
BRANCH_NAME="update/$(date +%Y-%m-%d)"
if git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
  echo "Switching to existing branch $BRANCH_NAME."
  git checkout "$BRANCH_NAME"
else
  echo "Creating and switching to new branch $BRANCH_NAME."
  git checkout -b "$BRANCH_NAME"
fi

# Get outdated packages.
# This awk command is more robust:
# - NF > 0: Skips empty lines.
# - $1 !~ /Package|----/: Skips lines where the first field looks like a typical header (e.g., "Package") or a separator (e.g., "----").
# This should correctly extract package names whether a simple header is present or not.
outdated_packages=$(poetry show --outdated | awk 'NF > 0 && $1 !~ /^[Pp]ackage$|^---|Fetching/ {print $1}')

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
  # Consider using 'poetry export' for generating requirements.txt, as it's more idiomatic with Poetry:
  # poetry export -f requirements.txt --output requirements.txt --without-hashes
  # If you need dev dependencies:
  # poetry export -f requirements.txt --output requirements.txt --with dev --without-hashes
  poetry run pip freeze > requirements.txt

  echo "Staging changes for $package_name..."
  # Ensure poetry.lock is always added, as 'poetry update' modifies it.
  # pyproject.toml might not change if only lock file is updated.
  git add pyproject.toml poetry.lock requirements.txt

  # Check if there are any staged changes before committing
  # Specifically check poetry.lock as it's the primary indicator of a successful poetry update
  if ! git diff --staged --quiet poetry.lock; then
    echo "Committing changes for $package_name..."
    git commit -m "Update $package_name"

    if [ $? -ne 0 ]; then
      echo "Error committing changes for $package_name. Please check git status."
      # It might be better to not exit here, but to collect errors and report at the end,
      # or allow the script to continue with other packages.
      # For now, keeping original behavior of exiting on commit error.
      exit 1
    fi
    echo "$package_name updated and committed."
  else
    echo "No changes to commit for $package_name (poetry.lock unchanged)."
  fi
  echo ""
done

echo "All packages processed."
# You can add your git push command here if desired
# Ensure you are pushing the correct branch name
# git push -u origin "$BRANCH_NAME"
