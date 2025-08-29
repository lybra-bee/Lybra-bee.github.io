#!/usr/bin/env python3
import os
import json
import requests
import random
from datetime import datetime, timezone
import glob
import base64
import time
import urllib.parse
import re

# ---------------------------
# 1. Генерация темы статьи
# ---------------------------
def generate_ai_trend_topic():
    current_trends_2025 = [
        "Multimodal AI интеграция текста изображений и аудио в единых моделях",
        "AI агенты автономные системы способные выполнять сложные задачи",
        "Квантовые вычисления и машинное обучение прорыв в производительности",
        "Нейроморфные вычисления энергоэффективные архитектуры нейросетей",
        "Generative AI создание контента кода и дизайнов искусственным интеллектом",
        "Edge AI обработка данных на устройстве без облачной зависимости",
        "AI для кибербезопасности предиктивная защита от угроз",
        "Этичный AI ответственное развитие и использование искусственного интеллекта",
        "AI в healthcare диагностика разработка лекарств и персонализированная медицина",
        "Автономные системы беспилотный транспорт и робототехника",
        "AI оптимизация сжатие моделей и ускорение inference",
        "Доверенный AI объяснимые и прозрачные алгоритмы",
        "AI для климата оптимизация энергопотребления и экологические решения",
        "Персональные AI ассистенты индивидуализированные цифровые помощники",
        "AI в образовании адаптивное обучение и персонализированные учебные планы"
    ]
    application_domains = [
        "в веб разработке и cloud native приложениях",
        "в мобильных приложениях и IoT экосистемах",
        "в облачных сервисах и распределенных системах",
        "в анализе больших данных и бизнес аналитике",
        "в компьютерной безопасности и киберзащите",
        "в медицинской диагностике и биотехнологиях",
        "в финансовых технологиях и финтехе",
        "в автономных транспортных системах",
        "в smart city и умной инфраструктуре",
        "в образовательных технологиях и EdTech"
    ]
    trend = random.choice(current_trends_2025)
    domain = random.choice(application_domains)
    topic_formats = [
        f"{trend} {domain} в 2025 году",
        f"Тенденции 2025 {trend} {domain}",
        f"{trend} революционные изменения {domain} в 2025",
        f"Как {trend} трансформирует {domain} в 2025 году",
        f"Инновации 2025 {trend} для {domain}",
        f"{trend} будущее {domain} в 2025 году",
        f"Практическое применение {trend} в {domain} 2025"
    ]
    return random.choice(topic_formats)

# ---------------------------
# 2. Основная функция генерации статьи
# ---------------------------
def generate_content():
    print("🚀 Запуск генерации контента...")
    KEEP_LAST_ARTICLES = 3
    clean_old_articles(KEEP_LAST_ARTICLES)
    
    selected_topic = generate_ai_trend_topic()
    print(f"📝 Актуальная тема 2025: {selected_topic}")

    # Генерация изображения
    image_filename = generate_article_image(selected_topic)

    # Генерация текста статьи
    content, model_used = generate_article_content(selected_topic)

    # Создание файла статьи
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = generate_slug(selected_topic)
    filename = f"content/posts/{date}-{slug}.md"

    frontmatter = generate_frontmatter(selected_topic, content, model_used, image_filename)

    os.makedirs("content/posts", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"✅ Статья создана: {filename}")
    return filename

# ---------------------------
# 3. Генерация текста статьи
# OpenRouter в приоритете, Groq запасной
# ---------------------------
def generate_article_content(topic):
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')

    models_to_try = []

    # OpenRouter модели — приоритет
    if openrouter_key:
        print("🔑 OpenRouter API ключ найден")
        openrouter_models = [
            "anthropic/claude-3-haiku",
            "google/gemini-pro",
            "mistralai/mistral-7b-instruct",
            "meta-llama/llama-3-8b-instruct",
        ]
        for model_name in openrouter_models:
            models_to_try.append((model_name, lambda m=model_name: generate_with_openrouter(openrouter_key, m, topic)))

    # Groq модели — запасные
    if groq_key:
        print("🔑 Groq API ключ найден")
        groq_models = [
            "llama-3.1-8b-instant",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        for model_name in groq_models:
            models_to_try.append((f"Groq-{model_name}", lambda m=model_name: generate_with_groq(groq_key, m, topic)))

    # Пробуем все доступные модели
    for model_name, generate_func in models_to_try:
        try:
            print(f"🔄 Пробуем: {model_name}")
            result = generate_func()
            if result and len(result.strip()) > 100:
                print(f"✅ Успешно через {model_name}")
                return result, model_name
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Ошибка {model_name}: {str(e)[:100]}")
            continue

    # Fallback - заглушка
    print("⚠️ Все API недоступны, создаем заглушку")
    fallback_content = f"""# {topic}

## Введение
{topic} - это важное направление в развитии искусственного интеллекта на 2025 год.

## Основные аспекты
- **Технологические инновации**: {topic} включает передовые разработки в области AI
- **Практическое применение**: Технология находит применение в различных отраслях
- **Перспективы развития**: Ожидается значительный рост в ближайшие годы

## Технические детали
Модели искусственного интеллекта для {topic} используют современные архитектуры нейросетей.

## Заключение
{topic} представляет собой ключевое направление развития искусственного интеллекта.
"""
    return fallback_content, "fallback-generator"

# ---------------------------
# 4. API генерации текста
# ---------------------------
def generate_with_openrouter(api_key, model_name, topic):
    prompt = f"""Напиши развернутую техническую статью на тему: "{topic}".
- Формат: Markdown
- Язык: русский
- Стиль: технический, для разработчиков
- Фокус на 2025 год"""
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,
            "temperature": 0.7
        },
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        if data.get('choices'):
            return data['choices'][0]['message']['content'].strip()
    raise Exception(f"HTTP {response.status_code}")

def generate_with_groq(api_key, model_name, topic):
    prompt = f"""Напиши развернутую техническую статью на тему: "{topic}".
- Формат: Markdown
- Язык: русский
- Стиль: технический, для разработчиков
- Фокус на 2025 год"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,
            "temperature": 0.7
        },
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        if data.get('choices'):
            return data['choices'][0]['message']['content'].strip()
    raise Exception(f"HTTP {response.status_code}")

# ---------------------------
# 5. Генерация изображений
# ---------------------------
def generate_article_image(topic):
    print("🎨 Генерация изображения...")

    stability_key = os.getenv('STABILITYAI_KEY')
    deepai_key = os.getenv('DEEPAI_KEY', '98c841c4')

    generators = [
        ("StabilityAI", lambda: generate_image_stabilityai(topic, stability_key) if stability_key else None),
        ("DeepAI", lambda: generate_image_deepai(topic, deepai_key) if deepai_key else None),
        ("Craiyon", lambda: generate_image_craiyon(topic)),
        ("Lexica", lambda: generate_image_lexica(topic)),
        ("Artbreeder", lambda: generate_image_artbreeder(topic)),
        ("Picsum", lambda: generate_image_picsum(topic)),
        ("LoremFlickr", lambda: generate_image_loremflickr(topic)),
        ("Placeholder", lambda: generate_image_placeholder(topic))
    ]

    for name, func in generators:
        try:
            print(f"🔄 Пробуем генератор: {name}")
            image_url = func()
            if image_url:
                print(f"✅ Успешно сгенерировано изображение через {name}")
                return image_url
            else:
                print(f"⚠️ {name} вернул None")
        except Exception as e:
            print(f"⚠️ Ошибка генератора {name}: {e}")

    print("⚠️ Все генераторы не сработали, продолжаем без изображения")
    return None

# ---------------------------
# 6. Fallback генераторы изображений
# ---------------------------
def generate_image_picsum(topic):
    w, h = 1024, 1024
    return f"https://picsum.photos/{w}/{h}?random={random.randint(1,10000)}"

def generate_image_loremflickr(topic):
    w, h = 1024, 1024
    tag = urllib.parse.quote(topic.split()[0])
    return f"https://loremflickr.com/{w}/{h}/{tag}"

def generate_image_placeholder(topic):
    w, h = 1024, 1024
    text = urllib.parse.quote("AI 2025")
    return f"https://via.placeholder.com/{w}x{h}?text={text}"

# ---------------------------
# TODO: Реализовать генераторы: generate_image_stabilityai, generate_image_deepai, generate_image_craiyon, generate_image_lexica, generate_image_artbreeder
# Они уже есть в твоем старом коде

# ---------------------------
# 7. Utility функции
# ---------------------------
def generate_slug(text):
    text = text.lower()
    text = text.replace(' ', '-')
    text = text.replace('--', '-')
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text[:60]

def generate_frontmatter(title, content, model_used, image_url):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    escaped_title = title.replace(':', ' -').replace('"','').replace("'",'').replace('\\','')
    frontmatter_lines = [
        "---",
        f'title: "{escaped_title}"',
        f"date: {now}",
        "draft: false",
        'tags: ["AI", "машинное обучение", "технологии", "2025"]',
        'categories: ["Искусственный интеллект"]',
        'summary: "Автоматически сгенерированная статья об искусственном интеллекте"'
    ]
    if image_url:
        frontmatter_lines.append(f'image: "{image_url}"')
    frontmatter_lines.append("---")
    frontmatter_lines.append(content)
    return "\n".join(frontmatter_lines)

def clean_old_articles(keep_last=3):
    print(f"🧹 Очистка старых статей, оставляем {keep_last} последних...")
    try:
        articles = glob.glob("content/posts/*.md")
        if not articles: return
        articles.sort(key=os.path.getmtime, reverse=True)
        articles_to_keep = articles[:keep_last]
        articles_to_delete = articles[keep_last:]
        for article_path in articles_to_delete:
            os.remove(article_path)
            slug = os.path.basename(article_path).replace('.md','')
            image_path = f"assets/images/posts/{slug}.png"
            if os.path.exists(image_path):
                os.remove(image_path)
    except Exception as e:
        print(f"⚠️ Ошибка при очистке статей: {e}")

# ---------------------------
# 8. Запуск
# ---------------------------
if __name__ == "__main__":
    generate_content()
