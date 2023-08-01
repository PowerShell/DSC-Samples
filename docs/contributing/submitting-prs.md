---
title:     How to submit a PR
linktitle: Submitting PRs
weight:    20
---

To make changes to content, submit a pull request (PR) from your fork. A pull request must be
reviewed before it can be merged.

## Using git branches

The default branch for the DSC samples is the `main` branch. Changes made in working branches are
merged into the `main`` branch, which automatically publishes the website.

Before starting any changes, create a working branch in your local copy of the DSC samples
repository. When working locally, be sure to synchronize your local repository before creating your
working branch. The working branch should be created from an update-to-date copy of the main
branch.

All pull requests should target the `main` branch.

## Improve the pull request process for everyone { toc_md="Best Practices" }

The simpler and more focused you can make your PR, the faster it can be reviewed and merged.

### Avoid pull requests that contain unrelated changes { toc_md="Avoid unrelated changes" }

Avoid creating PRs that contain unrelated changes. Separate minor updates to existing articles from
new articles or major rewrites. Work on these changes in separate working branches.

### Avoid editing repository configuration files { toc_md="Don't change configuration" }

Avoid modifying repository. Limit your changes where possible to the Markdown content files,
supporting image files, and the `sample` folder.

Incorrect modifications to repository configuration files can break the build, introduce
vulnerabilities or accessibility issues, or violate organizational standards. Repository
configuration files are any files that match one or more of these patterns:

- `_site/**`
- `.github/**`
- `.gitattributes`
- `LICENSE`
- `.markdownlint*`

<!-- Not yet implemented. As repo automation catches up, these sections should be documented.

### Use the pull request template { toc_md="Use the PR template" }

### Read the expectations comment { toc_md="Read expectations comment" }

## Netlify build service

## Github Actions

### Checklist Verification

### Authorization verification

### Sample code tests

### Markdown syntax linting

### Vale prose linting

-->
