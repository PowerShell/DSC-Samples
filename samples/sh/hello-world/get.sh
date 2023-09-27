# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#!/usr/bin/env bash

[ -f "$path" ] || _exists=false && match=$(grep "$contentMatch" "$path")
printf "{\"contentMatch\":\"$match\",\"path\":\"$path\",\"_exists\":$_exists}"
