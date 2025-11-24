---
layout: default
title: "Table of Contents"
permalink: /table-of-contents/
---

# Table of Contents

## Phoenix Rising

{% assign phoenix_chapters = site.pages | where: "book", "phoenix-rising" | sort: "chapter_number" %}
{% if phoenix_chapters.size > 0 %}
<div class="card-grid">
  {% for chapter in phoenix_chapters %}
  <a href="{{ chapter.url | relative_url }}" class="card">
    <h3>Chapter {{ chapter.chapter_number }}</h3>
    <p><strong>{{ chapter.title }}</strong></p>
    <p style="color: var(--muted); font-size: 0.9rem; margin-top: 0.5rem;">{{ chapter.content | strip_html | truncatewords: 25 }}</p>
  </a>
  {% endfor %}
</div>
{% else %}
<p>No Phoenix Rising chapters published yet. As soon as you add files inside `phoenix-rising/` with `layout: chapter` and `book: phoenix-rising`, they'll appear here.</p>
{% endif %}
