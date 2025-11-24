---
layout: default
title: "Table of Contents"
permalink: /table-of-contents/
---

# Table of Contents

## Phoenix Rising

{% assign phoenix_chapters = site.pages | where: "book", "phoenix-rising" | sort: "chapter_number" %}
{% if phoenix_chapters.size > 0 %}
<ol>
  {% for chapter in phoenix_chapters %}
  <li>
    <a href="{{ chapter.url | relative_url }}">
      Chapter {{ chapter.chapter_number }}: {{ chapter.title }}
    </a>
  </li>
  {% endfor %}
</ol>
{% else %}
<p>No Phoenix Rising chapters published yet. As soon as you add files inside `phoenix-rising/` with `layout: chapter` and `book: phoenix-rising`, they’ll appear here.</p>
{% endif %}
