---
layout: default
title: "Table of Contents"
permalink: /table-of-contents/
---

# Table of Contents

{% assign chapters = site.pages | where: "layout", "chapter" | sort: "chapter_number" %}
{% if chapters.size > 0 %}
<ol>
  {% for chapter in chapters %}
  <li>
    <a href="{{ chapter.url | relative_url }}">
      Chapter {{ chapter.chapter_number }}: {{ chapter.title }}
    </a>
  </li>
  {% endfor %}
</ol>
{% else %}
<p>No chapters published yet. Once you add chapter files with the `chapter` layout they'll show up here automatically.</p>
{% endif %}
