# Books

This repo hosts the GitHub Pages version of the Phoenix Rising project.

## Structure

- `_layouts/` – shared HTML shells for regular pages (`default.html`) and chapters (`chapter.html`).
- `_config.yml` – site metadata plus GitHub Pages settings (`baseurl`, Markdown engine, etc.).
- `phoenix-rising/` – the first book, keeping every chapter (`chapter-1.md`, `chapter-2.md`, `chapter-3.md`, …) and a landing page (`index.md`).
- `table-of-contents.md` – auto-lists Phoenix Rising chapters using the `book: phoenix-rising` front matter flag.
- `SCP-5437.md` – bonus lore rendered with the site layout.

When you add a new chapter, drop it inside `phoenix-rising/` with:

```yaml
---
layout: chapter
book: phoenix-rising
chapter_number: <next number>
title: "Chapter Title"
prev_url: /phoenix-rising/chapter-<prev>/
next_url: /phoenix-rising/chapter-<next>/   # omit for the last chapter
---
```

The Table of Contents and the `[Previous]/[Next]` buttons update automatically once those values are set.