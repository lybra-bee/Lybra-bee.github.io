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
    
    # Генерируем актуальную тему на основе трендов AI и технологий
    selected_topic = generate_ai_trend_topic()
    print(f"📝 Актуальная тема: {selected_topic}")
    
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
                                "content": f"Напиши техническую статью на тему: {selected_topic}. Используй Markdown форматирование с подзаголовками ##, **жирным шрифтом** для ключевых терминов и нумерованными списками. Ответ на русском языке, объем 300-400 слов. Сделай статью информативной, технически точной и полезной для разработчиков. Освещи последние тренды 2024-2025 года."
                            }
                        ],
                        "max_tokens": 600,
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

def generate_ai_trend_topic():
    """Генерирует актуальную тему на основе трендов AI и технологий 2024-2025"""
    
    # Базовые категории технологических трендов
    tech_domains = [
        "искусственный интеллект",
        "машинное обучение", 
        "генеративные AI",
        "компьютерное зрение",
        "обработка естественного языка",
        "большие языковые модели",
        "нейросетевые архитектуры",
        "робототехника",
        "интернет вещей",
        "блокчейн и Web3",
        "кибербезопасность",
        "облачные вычисления",
        "квантовые вычисления",
        "дополненная реальность",
        "виртуальная реальность",
        "беспилотные транспортные средства",
        "биотехнологии",
        "зеленые технологии"
    ]
    
    # Актуальные тренды 2024-2025
    current_trends = [
        "трансформеры и attention механизмы",
        "мультимодальные AI системы",
        "few-shot и zero-shot обучение",
        "нейросети с памятью",
        "обучение с подкреплением",
        "генеративно-состязательные сети",
        "диффузионные модели",
        "энергоэффективные AI",
        "федеративное обучение",
        "объяснимый AI",
        "AI этика и безопасность",
        "персонализированные AI ассистенты",
        "автономные агенты",
        "AI для научных открытий",
        "нейроморфные вычисления",
        "квантовые нейросети",
        "AI в медицине и здравоохранении",
        "умные города и IoT",
        "устойчивые технологии",
        "метавселенные и цифровые двойники"
    ]
    
    # Приложения и отрасли
    applications = [
        "в веб-разработке",
        "в мобильных приложениях", 
        "в облачных сервисах",
        "в анализе данных",
        "в компьютерной безопасности",
        "в образовательных технологиях",
        "в финансовых технологиях",
        "в healthcare технологиях",
        "в умном доме",
        "в промышленной автоматизации",
        "в сельском хозяйстве",
        "в транспортных системах",
        "в развлечениях и играх",
        "в социальных сетях",
        "в электронной коммерции",
        "в государственном управлении",
        "в экологическом мониторинге",
        "в космических технологиях"
    ]
    
    # Генерируем комбинацию из разных категорий
    domain = random.choice(tech_domains)
    trend = random.choice(current_trends)
    application = random.choice(applications)
    
    # Разные форматы тем для разнообразия
    topic_formats = [
        f"{trend}: новые возможности в {domain} {application}",
        f"{domain} 2025: как {trend} меняют {application}",
        f"{trend} в {domain} - перспективы {application}",
        f"Будущее {domain}: {trend} и их impact на {application}",
        f"{trend} революция в {domain} для {application}",
        f"Как {trend} трансформируют {domain} в {application}",
        f"{domain} следующего поколения: {trend} {application}",
        f"{trend} и их применение в {domain} для {application}",
        f"Инновации в {domain}: {trend} меняющие {application}",
        f"{trend} - новый стандарт в {domain} для {application}"
    ]
    
    selected_topic = random.choice(topic_formats)
    
    # Добавляем год для актуальности
    if random.random() > 0.5:
        selected_topic = f"{selected_topic} в 2024-2025"
    
    return selected_topic

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
    """Генерация fallback контента на основе актуальной темы"""
    return f"""## {topic}

В 2024-2025 годах **{topic.split(':')[0]}** продолжает активно развиваться и трансформировать технологический ландшафт.

### Ключевые тенденции и инновации

- **Передовые алгоритмы** и архитектуры нейросетей
- **Улучшенная эффективность** и оптимизация вычислений
- **Интеграция с облачными платформами** и распределенными системами
- **Повышенная безопасность** и этические considerations
- **Автоматизация** сложных задач и процессов

### Технологический impact

Современные разработчики и исследователи используют cutting-edge инструменты и методологии для создания инновационных решений. Экосистема быстро эволюционирует, предлагая новые возможности для оптимизации workflow, улучшения пользовательского опыта и решения complex problems.

Технологический ландшафт требует continuous learning и адаптации к emerging challenges и opportunities."""

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
        ',': '',
        '&': 'and'
    }
    
    for old, new in replacements.items():
        slug = slug.replace(old, new)
    
    # Удаляем все не-ASCII символы кроме дефиса
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    
    # Убираем множественные дефисы
    while '--' in slug:
        slug = slug.replace('--', '-')
    
    # Обрезаем до 50 символов
    return slug[:50]

def generate_frontmatter(topic, content, model_used, api_success):
    """Генерация frontmatter и содержимого"""
    current_time = datetime.now()
    status = "✅ API генерация" if api_success else "⚠️ Локальная генерация"
    
    # Определяем теги на основе темы
    tags = ["искусственный-интеллект", "технологии", "инновации", "2024-2025"]
    if "веб" in topic.lower() or "web" in topic.lower():
        tags.append("веб-разработка")
    if "безопасность" in topic.lower() or "security" in topic.lower():
        tags.append("кибербезопасность")
    if "облако" in topic.lower() or "cloud" in topic.lower():
        tags.append("облачные-вычисления")
    if "данн" in topic.lower() or "data" in topic.lower():
        tags.append("анализ-данных")
    
    return f"""---
title: "{topic}"
date: {datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
draft: false
description: "Автоматически сгенерированная статья о {topic}"
tags: {json.dumps(tags, ensure_ascii=False)}
categories: ["Технологии"]
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
- **Актуальность:** Тренды 2024-2025

> *Сгенерировано автоматически через GitHub Actions + OpenRouter*
"""

if __name__ == "__main__":
    generate_content()
