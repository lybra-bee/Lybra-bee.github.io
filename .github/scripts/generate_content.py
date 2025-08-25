#!/usr/bin/env python3
import os
import json
import requests
import random
from datetime import datetime
import glob

def generate_content():
    # Конфигурация - сколько статей оставлять
    KEEP_LAST_ARTICLES = 3
    
    # Сначала почистим старые статьи
    clean_old_articles(KEEP_LAST_ARTICLES)
    
    # Конфигурация тем
    topics = [
        "Веб-фреймворки 2024: React, Vue, Svelte",
        "Serverless архитектура для веб-приложений", 
        "Искусственный интеллект в веб-разработке",
        "Прогрессивные веб-приложения (PWA)",
        "Кибербезопасность веб-приложений",
        "WebAssembly и высокопроизводительные веб-приложения",
        "JAMstack архитектура и статические генераторы",
        "Микросервисы vs монолиты в веб-разработке",
        "TypeScript vs JavaScript в современной разработке",
        "GraphQL vs REST API: что выбрать в 2024"
    ]
    
    selected_topic = random.choice(topics)
    print(f"📝 Тема: {selected_topic}")
    
    # Попытка генерации через OpenRouter
    api_key = os.getenv('OPENROUTER_API_KEY')
    content = ""
    model_used = "Локальная генерация"
    api_success = False
    
    if api_key and api_key != "":
        # ПРОВЕРЕННЫЕ РАБОЧИЕ МОДЕЛИ (в приоритетном порядке)
        working_models = [
            "mistralai/mistral-7b-instruct",      # ✅ ПРОВЕРЕНА - РАБОТАЕТ
            "google/gemini-pro",                  # ✅ Высокий приоритет
            "anthropic/claude-3-haiku",           # ✅ Качественная модель
            "meta-llama/llama-3-8b-instruct",     # ✅ Популярная модель
            "huggingfaceh4/zephyr-7b-beta",       # ✅ Бесплатная
            "openchat/openchat-7b",               # ⚠️ Может не работать
            "google/palm-2-chat-bison-32k"        # ⚠️ Может не работать
        ]
        
        # Перебираем модели пока не найдем рабочую
        for selected_model in working_models:
            try:
                print(f"🔄 Пробуем модель: {selected_model}")
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                        "HTTP-Referer": "https://github.com",
                        "X-Title": "AI Blog Generator"
                    },
                    json={
                        "model": selected_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Напиши техническую статью на тему: {selected_topic}. Используй Markdown форматирование с подзаголовками ##, **жирным шрифтом** для ключевых терминов и нумерованными списками. Ответ на русском языке, объем 200-300 слов. Сделай статью информативной и полезной для разработчиков."
                            }
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7,
                        "top_p": 0.9
                    },
                    timeout=15
                )
                
                print(f"📊 Статус ответа: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        model_used = selected_model
                        api_success = True
                        print(f"✅ Успешная генерация через {selected_model}")
                        
                        # Очистка контента от лишних кавычек
                        content = content.replace('"""', '').replace("'''", "").strip()
                        break  # Выходим из цикла при успехе
                    else:
                        print(f"⚠️ Нет choices в ответе от {selected_model}")
                else:
                    error_msg = response.text[:100] if response.text else "No error message"
                    print(f"❌ Ошибка {response.status_code} от {selected_model}: {error_msg}")
                    
            except Exception as e:
                print(f"⚠️ Исключение с {selected_model}: {e}")
                continue  # Пробуем следующую модель
        
        if not api_success:
            print("❌ Все модели не сработали, используем fallback")
            content = generate_fallback_content(selected_topic)
    else:
        print("⚠️ API ключ не найден или пустой")
        content = generate_fallback_content(selected_topic)
    
    # Создаем новую статью
    date = datetime.now().strftime("%Y-%m-%d")
    slug = generate_slug(selected_topic)
    filename = f"content/posts/{date}-{slug}.md"
    
    frontmatter = generate_frontmatter(selected_topic, content, model_used, api_success)
    
    os.makedirs("content/posts", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    print(f"✅ Файл создан: {filename}")
    
    # Покажем начало файла для проверки
    with open(filename, 'r', encoding='utf-8') as f:
        preview = f.read(400)
    print(f"📄 Предпросмотр:\n{preview}...")
    
    return filename

def clean_old_articles(keep_last=3):
    """Оставляет только последние N статей, удаляет остальные"""
    print(f"🧹 Очистка старых статей, оставляем {keep_last} последних...")
    
    # Получаем все md файлы в папке posts
    articles = glob.glob("content/posts/*.md")
    
    if not articles:
        print("📁 Нет статей для очистки")
        return
    
    # Сортируем по дате изменения (сначала старые)
    articles.sort(key=os.path.getmtime)
    
    # Оставляем только последние N статей
    articles_to_keep = articles[-keep_last:]
    articles_to_delete = articles[:-keep_last]
    
    print(f"📊 Всего статей: {len(articles)}")
    print(f"💾 Сохраняем: {len(articles_to_keep)}")
    print(f"🗑️ Удаляем: {len(articles_to_delete)}")
    
    # Удаляем старые статьи
    for article_path in articles_to_delete:
        try:
            os.remove(article_path)
            print(f"❌ Удалено: {os.path.basename(article_path)}")
        except Exception as e:
            print(f"⚠️ Ошибка удаления {article_path}: {e}")
    
    # Покажем какие статьи остались
    remaining_articles = glob.glob("content/posts/*.md")
    remaining_articles.sort(key=os.path.getmtime, reverse=True)
    
    print("📋 Оставшиеся статьи (новые сверху):")
    for i, article in enumerate(remaining_articles[:5], 1):
        print(f"   {i}. {os.path.basename(article)}")

def generate_fallback_content(topic):
    """Генерация fallback контента"""
    return f"""## {topic}

В 2024 году **{topic.split(':')[0]}** продолжает активно развиваться и трансформировать индустрию веб-разработки.

### Ключевые тенденции

- **Инновационные подходы** к проектированию и разработке
- **Улучшенная производительность** и оптимизация систем
- **Интеграция с современными cloud-технологиями**
- **Повышенная безопасность** и отказоустойчивость
- **Автоматизация** процессов разработки и deployment

### Технологический стек

Современные разработчики используют передовые инструменты и фреймворки для создания масштабируемых и эффективных решений. Экосистема продолжает развиваться, предлагая новые возможности для оптимизации workflow и улучшения пользовательского опыта.

Технологический ландшафт постоянно эволюционирует, требуя от специалистов непрерывного обучения и адаптации к новым вызовам."""

def generate_slug(topic):
    """Генерация slug из названия темы"""
    slug = topic.lower()
    # Заменяем специальные символы
    replacements = {
        ' ': '-',
        ':': '',
        '(': '',
        ')': '',
        '/': '-',
        '\\': '-',
        '.': '',
        ',': ''
    }
    
    for old, new in replacements.items():
        slug = slug.replace(old, new)
    
    # Удаляем все не-ASCII символы кроме дефиса
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    
    # Убираем множественные дефисы
    while '--' in slug:
        slug = slug.replace('--', '-')
    
    # Обрезаем до 40 символов
    return slug[:40]

def generate_frontmatter(topic, content, model_used, api_success):
    """Генерация frontmatter и содержимого"""
    current_time = datetime.now()
    status = "✅ API генерация" if api_success else "⚠️ Локальная генерация"
    
    return f"""---
title: "{topic}"
date: {datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
draft: false
description: "Автоматически сгенерированная статья о {topic}"
tags: ["веб-разработка", "технологии", "2024"]
categories: ["Разработка"]
---

# {topic}

{content}

---

### 🔧 Технические детали

- **Модель AI:** {model_used}
- **Дата генерации:** {current_time.strftime("%d.%m.%Y %H:%M UTC")}
- **Тема:** {topic}
- **Статус:** {status}
- **Уникальность:** Сохраняются только 3 последние статьи

> *Сгенерировано автоматически через GitHub Actions + OpenRouter*
"""

if __name__ == "__main__":
    generate_content()
