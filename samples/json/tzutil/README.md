# Microsoft/tzutil

## Introduction
The `Microsoft/tzutil` resource is a sample resources which allows you to manage time zone settings on Windows machines using DSC v3. This resource demonstrates that a resource may be made with a native binary that does not understand or outputs JSON. The JSON is merely made by wraping the command's input and output in PowerShell's `ConvertFrom-Json` and `ConvertTo-Json`. 

---
***Note:***  
This methodology is not extremely extensible and should be avoided for most dsc resources. This example exists as a simple way to understand how the `*.dsc.resource.json` manifest interacts with a binary to create a dsc resource. DSC Resources should be either a native binary which understands and outputs json or a common tool which has a `-input json` or `-output json` flag (or something similar).

---

## Prerequisites

Before using the `Microsoft/tzutil` file, make sure you have the following prerequisites in place:
- DSC version 3 or later
- Windows Desktop or Server

## Usage
To use the Microsoft/tzutil resource, follow these steps:

1. Download the `Microsoft/tzutil` file from the official repository and save in the resource path for DSCv3

2. Create a yaml config called `tzutil.dsc.config.yaml` for the resource:
   ```yaml
   $schema: https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2023/10/config/document.json
    resources:
    - name: Desired TimeZone
    type: Microsoft/tzutil
    properties:
        timezone: UTC
        dstoff: false
   ```

3. Call the resource by piping the content to dsc:
   ```powershell
   cat .\tzutil.dsc.config.yaml | dsc config set
   ```
   See the results:
   ```yaml
   results:
   - name: Desired TimeZone
   type: Microsoft/tzutil
   result:
      beforeState:
         timezone: Pacific Standard Time
         dstoff: false
      afterState:
         timezone: UTC
         dstoff: false
      changedProperties:
      - timezone
   messages: []
   hadErrors: false
   ```
