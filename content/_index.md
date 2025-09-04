---
title: "Главная"
date: 2024-01-01
draft: false
---

## 🚀 Добро пожаловать!

Этот сайт автоматически генерирует контент с помощью искусственного интеллекта. Каждый день AI создает новые статьи и изображения.

### 📖 Последние статьи:

<div class="recent-posts">
{{ range first 3 (where .Site.RegularPages "Type" "posts") }}
<div class="post-preview">
    <h3><a href="{{ .Permalink }}">{{ .Title }}</a></h3>
    <p class="date">{{ .Date.Format "2 January 2006" }}</p>
    {{ if .Params.image }}
    <img src="{{ .Params.image }}" alt="{{ .Title }}" class="post-image">
    {{ end }}
    <p>{{ .Summary }}...</p>
    <a href="{{ .Permalink }}" class="read-more">Читать далее →</a>
</div>
{{ end }}
</div>

### 🖼️ [Галерея изображений](/gallery/)

### 👤 [Обо мне](/about/)

---

*Весь контент генерируется автоматически с помощью AI*
