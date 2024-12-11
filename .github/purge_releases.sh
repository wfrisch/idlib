#!/bin/bash
set -euo pipefail

release_count=$(gh release list | wc -l)

if (( release_count > 5 )); then
    for tag in $(gh release list | tail -n +6 | grep -Po 'db_release-\d+'); do
        echo Deleting release $tag
        gh release delete -y "$tag"
    done
else
    echo "Not enough releases to delete. There are only $release_count releases."
fi
