#!/usr/bin/env python3
import os
import json
import requests
import random
from datetime import datetime, timezone
import glob
import base64
import time
import re

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
        "в медицинской диагностике и биотехнологиях"
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

def generate_content():
    print("🚀 Запуск генерации контента...")
    KEEP_LAST_ARTICLES = 3
    clean_old_articles(KEEP_LAST_ARTICLES)
    
    selected_topic = generate_ai_trend_topic()
    print(f"📝 Актуальная тема 2025: {selected_topic}")
    
    image_filename = generate_article_image(selected_topic)
    
    content, model_used = generate_article_content(selected_topic)
    
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = generate_slug(selected_topic)
    filename = f"content/posts/{date}-{slug}.md"
    
    frontmatter = generate_frontmatter(selected_topic, content, model_used, image_filename)
    
    os.makedirs("content/posts", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    print(f"✅ Статья создана: {filename}")
    return filename

def generate_article_content(topic):
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    
    models_to_try = []
    
    # OpenRouter первичный
    if openrouter_key:
        openrouter_models = [
            "anthropic/claude-3-haiku",
            "google/gemini-pro",
            "mistralai/mistral-7b-instruct",
            "meta-llama/llama-3-8b-instruct",
        ]
        for model_name in openrouter_models:
            models_to_try.append((model_name, lambda m=model_name: generate_with_openrouter(openrouter_key, m, topic)))
    
    # Groq запасной
    if groq_key:
        groq_models = [
            "llama-3.1-8b-instant",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        for model_name in groq_models:
            models_to_try.append((f"Groq-{model_name}", lambda m=model_name: generate_with_groq(groq_key, m, topic)))
    
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

def generate_with_groq(api_key, model_name, topic):
    prompt = f"""Напиши развернутую техническую статью на тему: "{topic}".
Объем: 400-600 слов. Формат: Markdown. Язык: русский. Стиль: технический."""
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model_name, "messages":[{"role":"user","content":prompt}],"max_tokens":1500},
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    raise Exception(f"HTTP {response.status_code}")

def generate_with_openrouter(api_key, model_name, topic):
    prompt = f"""Напиши развернутую техническую статью на тему: "{topic}".
Объем: 400-600 слов. Формат: Markdown. Язык: русский. Стиль: технический."""
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model_name, "messages":[{"role":"user","content":prompt}],"max_tokens":1500},
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    raise Exception(f"HTTP {response.status_code}")

def generate_article_image(topic):
    print("🎨 Генерация изображения...")
    
    generators = [
        ("StabilityAI", generate_image_stabilityai),
        ("DeepAI", generate_image_deepai),
        ("Craiyon", generate_image_craiyon),
        ("Lexica", generate_image_lexica),
        ("Artbreeder", generate_image_artbreeder),
        ("Picsum", generate_image_picsum),
        ("HuggingFace", generate_image_huggingface)
    ]
    
    for name, func in generators:
        try:
            print(f"🔄 Пробуем генератор: {name}")
            img = func(topic)
            if img:
                print(f"✅ Успешно сгенерировано изображение через {name}")
                return img
            else:
                print(f"⚠️ {name} вернул None")
        except Exception as e:
            print(f"⚠️ Ошибка {name}: {e}")
    print("⚠️ Не удалось сгенерировать изображение ни одним генератором")
    return None

# --- Ниже пример функций для HuggingFace и Picsum ---
def generate_image_huggingface(topic):
    hf_token = "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"
    model_name = "stabilityai/stable-diffusion-xl-base-1.0"
    prompts = [
        f"Futuristic AI concept for {topic}. Digital brain, glowing interfaces, sci-fi style",
        f"Technology illustration for {topic}. Modern futuristic style, abstract, professional digital art"
    ]
    prompt = random.choice(prompts)
    headers = {"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    response = requests.post(f"https://api-inference.huggingface.co/models/{model_name}", headers=headers, json=payload, timeout=60)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and "image_base64" in data[0]:
            image_data = base64.b64decode(data[0]["image_base64"])
            return save_article_image(image_data, topic)
    return None

def generate_image_picsum(topic):
    url = f"https://picsum.photos/1024/1024?random={random.randint(1,10000)}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return save_article_image(r.content, topic)
    except:
        return None
    return None

def save_article_image(image_data, topic):
    try:
        os.makedirs("assets/images/posts", exist_ok=True)
        slug = topic.lower().replace(" ", "-")[:60]
        filename = f"posts/{slug}.png"
        full_path = f"assets/images/{filename}"
        with open(full_path, "wb") as f:
            f.write(image_data)
        return f"/images/{filename}"
    except:
        return None

def generate_slug(text):
    text = text.lower()
    text = text.replace(' ', '-')
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:60]

def generate_frontmatter(title, content, model_used, image_url):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    escaped_title = title.replace(':', ' -').replace('"','').replace("'",'').replace('\\','')
    frontmatter_lines = [
        "---",
        f'title: "{escaped_title}"',
        f"date: {now}",
        "draft: false",
        'tags: ["AI","машинное обучение","технологии","2025"]',
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
    articles = glob.glob("content/posts/*.md")
    if not articles:
        return
    articles.sort(key=os.path.getmtime, reverse=True)
    articles_to_keep = articles[:keep_last]
    articles_to_delete = articles[keep_last:]
    for article_path in articles_to_delete:
        try:
            os.remove(article_path)
            slug = os.path.basename(article_path).replace('.md','')
            img_path = f"assets/images/posts/{slug}.png"
            if os.path.exists(img_path):
                os.remove(img_path)
        except:
            pass

if __name__ == "__main__":
    generate_content()
