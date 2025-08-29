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

# -----------------------------
# Генерация темы статьи
# -----------------------------
def generate_ai_trend_topic():
    """Генерирует актуальную тему на основе реальных трендов AI 2025"""
    
    current_trends_2025 = [
        "Multimodal AI - интеграция текста, изображений и аудио в единых моделях",
        "AI агенты - автономные системы способные выполнять сложные задачи",
        "Квантовые вычисления и машинное обучение - прорыв в производительности",
        "Нейроморфные вычисления - энергоэффективные архитектуры нейросетей",
        "Generative AI - создание контента, кода и дизайнов искусственным интеллектом",
        "Edge AI - обработка данных на устройстве без облачной зависимости",
        "AI для кибербезопасности - предиктивная защита от угроз",
        "Этичный AI - ответственное развитие и использование искусственного интеллекта",
        "AI в healthcare - диагностика, разработка лекарств и персонализированная медицина",
        "Автономные системы - беспилотный транспорт и робототехника",
        "AI оптимизация - сжатие моделей и ускорение inference",
        "Доверенный AI - объяснимые и прозрачные алгоритмы",
        "AI для климата - оптимизация энергопотребления и экологические решения",
        "Персональные AI ассистенты - индивидуализированные цифровые помощники",
        "AI в образовании - адаптивное обучение и персонализированные учебные планы"
    ]
    
    application_domains = [
        "в веб-разработке и cloud-native приложениях",
        "в мобильных приложениях и IoT экосистемах",
        "в облачных сервисах и распределенных системах",
        "в анализе больших данных и бизнес-аналитике",
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
        f"Тенденции 2025: {trend} {domain}",
        f"{trend} - революционные изменения {domain} в 2025",
        f"Как {trend} трансформирует {domain} в 2025 году",
        f"Инновации 2025: {trend} для {domain}",
        f"{trend} - будущее {domain} в 2025 году",
        f"Практическое применение {trend} в {domain} 2025"
    ]
    
    return random.choice(topic_formats)

# -----------------------------
# Генерация статьи
# -----------------------------
def generate_content():
    """Генерирует контент статьи через AI API"""
    print("🚀 Запуск генерации контента...")
    
    KEEP_LAST_ARTICLES = 3
    clean_old_articles(KEEP_LAST_ARTICLES)
    
    selected_topic = generate_ai_trend_topic()
    print(f"📝 Актуальная тема 2025: {selected_topic}")
    
    # Генерируем текст статьи
    content, model_used = generate_article_content(selected_topic)
    
    # Генерируем изображение
    image_path = generate_image_with_groq(selected_topic)
    
    # Создаем файл статьи
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = generate_slug(selected_topic)
    filename = f"content/posts/{date}-{slug}.md"
    
    frontmatter = generate_frontmatter(selected_topic, content, model_used, image_path)
    
    os.makedirs("content/posts", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    print(f"✅ Статья создана: {filename}")
    return filename

# -----------------------------
# Текст через Groq/OpenRouter
# -----------------------------
def generate_article_content(topic):
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    
    models_to_try = []
    
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
    
    print("⚠️ Все API недоступны, fallback")
    fallback_content = f"# {topic}\n\nИИ развивается очень быстро. Эта статья — заглушка."
    return fallback_content, "fallback-generator"

def generate_with_groq(api_key, model_name, topic):
    prompt = f"""Напиши развернутую техническую статью на тему: "{topic}".
Формат: Markdown, язык: русский, аудитория: разработчики, год: 2025."""
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model_name, "messages": [{"role": "user", "content": prompt}]},
        timeout=30
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]

def generate_with_openrouter(api_key, model_name, topic):
    prompt = f"""Напиши техническую статью на тему: "{topic}".
Формат: Markdown, язык: русский, аудитория: разработчики, год: 2025."""
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model_name, "messages": [{"role": "user", "content": prompt}]},
        timeout=30
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]

# -----------------------------
# Изображения через Groq
# -----------------------------
def generate_image_with_groq(prompt):
    """Генерация изображения через Groq"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️ Нет GROQ_API_KEY, пропускаем генерацию изображений")
        return None

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "flux-schnell",   # Groq поддерживает flux/sd3
                "prompt": prompt,
                "size": "1024x1024"
            },
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                img_b64 = data["data"][0]["b64_json"]
                img_bytes = base64.b64decode(img_b64)
                os.makedirs("static/images/posts", exist_ok=True)
                filename = f"static/images/posts/{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
                with open(filename, "wb") as f:
                    f.write(img_bytes)
                print(f"🖼️ Изображение сохранено: {filename}")
                return "/" + filename  # путь для Hugo
        print(f"⚠️ Ошибка генерации изображения {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"⚠️ Ошибка Groq Image API: {e}")
    return None

# -----------------------------
# Вспомогательные функции
# -----------------------------
def generate_slug(text):
    text = text.lower()
    text = ''.join(c for c in text if c.isalnum() or c in ' -')
    text = text.replace(' ', '-')
    text = text.replace('--', '-')
    return text[:100]

def generate_frontmatter(title, content, model_used, image_path):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    image_block = f'\nimage: "{image_path}"' if image_path else ""
    frontmatter = f"""---
title: "{title}"
date: {now}
draft: false
tags: ["AI", "машинное обучение", "технологии", "2025"]
categories: ["Искусственный интеллект"]
summary: "Автоматически сгенерированная статья об искусственном интеллекте"
model: "{model_used}"{image_block}
---
{content}
"""
    return frontmatter

def clean_old_articles(keep_last=3):
    print(f"🧹 Очистка старых статей, оставляем {keep_last} последних...")
    articles = glob.glob("content/posts/*.md")
    if not articles:
        return
    articles.sort(key=os.path.getmtime, reverse=True)
    for article_path in articles[keep_last:]:
        try:
            os.remove(article_path)
            print(f"❌ Удалено: {article_path}")
        except Exception as e:
            print(f"⚠️ Ошибка удаления {article_path}: {e}")

# -----------------------------
if __name__ == "__main__":
    generate_content()
