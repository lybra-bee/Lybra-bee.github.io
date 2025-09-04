---
title: "Главная"
date: 2024-01-01
draft: false
---

## 🚀 Добро пожаловать в AI Blog!

Самые свежие статьи об искусственном интеллекте и технологиях 2025 года. Весь контент генерируется автоматически с помощью современных AI-моделей.

### 📖 Последние статьи:

<div class="recent-posts">
{{ range first 3 (where .Site.RegularPages "Type" "posts") }}
<div class="post-preview">
    <h3><a href="{{ .Permalink }}">{{ .Title }}</a></h3>
    <p class="date">{{ .Date.Format "2 January 2006" }}</p>
    {{ if .Params.image }}
    <img src="{{ .Params.image }}" alt="{{ .Title }}" class="post-image">
    {{ end }}
    <p>{{ .Summary | truncate 150 }}...</p>
    <a href="{{ .Permalink }}" class="read-more">Читать статью →</a>
</div>
{{ end }}
</div>

### 🎯 Быстрые ссылки:
- 🖼️ [Галерея AI-изображений](/gallery/)
- 📚 [Все статьи](/posts/)
- 🏷️ [Теги](/tags/)
- 👤 [О проекте](/about/)

---

*🤖 Весь контент создается автоматически с помощью искусственного интеллекта. Обновляется ежедневно через GitHub Actions.*
