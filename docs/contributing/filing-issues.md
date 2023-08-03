---
title:     How to file an issue
linktitle: Filing Issues
weight:    10
---

This project supports filing three kinds of issues: bug reports, new tutorial requests, and new
tutorial implementation requests.

Before you file any issue, make sure to follow these steps:

1. Search the existing issues for this repository. If there is an issue that fits your needs, don't
   file a new one. Subscribe, react, or comment on that issue instead.
1. Think of a descriptive title. Issue titles should be a short synopsis of the problem or request
   to help people orient themselves when looking at the issue list.
1. If you're requesting a new tutorial or a new implementation of an existing tutorial, read the
   information about [contributing a tutorial][01]

## Bug reports { .text-center toc_md="Report a bug" }

``````columns { #bug-report-info }
```column { grow=2 }
To report issues with a tutorial or code sample, like typos, technical and
factual errors, and grammar, use the following button:
```

```column { .flex .align-center .justify-center .text-center }
![button:File a bug report][br]
{ variant="danger" prefix_icon="bug-fill" pill=true  }

[br]: https://github.com/PowerShell/DSC-Samples/issues/new?assignees=&labels=bug&projects=&template=00-bug.yml
```
``````

## Requesting a new tutorial { .text-center toc_md="New tutorial" }

``````columns { #new-tutorial-info }
```column { grow=2 }
To request a new tutorial, consider the learning goals for the tutorial. Why is
it needed? What gap will it fill? Who is the intended audience? What scenario
will it address?

When you have a concrete idea for the new tutorial, use the following button
to submit your request:
```

```column { .flex .align-center .justify-center .text-center }
![button:Request a new tutorial][br]
{ variant="success" prefix_icon="file-plus-fill" pill=true }

[br]: https://github.com/PowerShell/DSC-Samples/issues/new?assignees=&labels=request-tutorial%20needs-triage&projects=&template=01-new-tutorial.yml
```
``````

## Requesting a new tutorial implementation { .text-center toc_md="New implementation" }

``````columns { #new-implementation-info }
```column { grow=2 }
To request a new language implementation for an existing tutorial, use the
following button to submit your request:
```

```column { .flex .align-center .justify-center .text-center }
![button:Request a new implementation][br]
{ variant="primary" prefix_icon="file-earmark-code-fill" pill=true }

[br]: https://github.com/PowerShell/DSC-Samples/issues/new?assignees=&labels=request-tutorial%20needs-triage&projects=&template=01-new-tutorial.yml
```
``````

[01]: tutorials/_index.md
