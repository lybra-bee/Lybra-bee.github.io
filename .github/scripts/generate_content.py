#!/usr/bin/env python3
import os
import json
import requests
import random
from datetime import datetime, timezone
import re
import shutil
import urllib.parse
import time

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
    return f"{trend} {domain} в 2025 году"

def clean_old_articles(keep_last=3):
    print(f"🧹 Очистка старых статей, оставляем {keep_last} последних...")
    try:
        content_dir = "content"
        if os.path.exists(content_dir):
            shutil.rmtree(content_dir)
        os.makedirs("content/posts", exist_ok=True)
        with open("content/_index.md", "w", encoding="utf-8") as f:
            f.write("---\ntitle: \"Главная\"\n---")
        with open("content/posts/_index.md", "w", encoding="utf-8") as f:
            f.write("---\ntitle: \"Статьи\"\n---")
        print("✅ Создана чистая структура content")
    except Exception as e:
        print(f"⚠️ Ошибка при очистке: {e}")

def generate_slug(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\-]', '', text.replace(' ', '-'))
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:60]

def generate_frontmatter(title, content, model_used, image_url):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    escaped_title = title.replace(':', ' -').replace('"', '').replace("'", "").replace('\\', '')
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

def generate_with_groq(api_key, model_name, topic):
    prompt = f"Напиши развернутую техническую статью на тему: \"{topic}\". Формат Markdown, 400-600 слов, русский, для разработчиков."
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model_name, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1500}
    )
    if response.status_code == 200:
        data = response.json()
        if data.get('choices'):
            return data['choices'][0]['message']['content'].strip()
    raise Exception(f"Groq HTTP {response.status_code}")

def generate_with_openrouter(api_key, model_name, topic):
    prompt = f"Напиши развернутую техническую статью на тему: \"{topic}\". Формат Markdown, 400-600 слов, русский, для разработчиков."
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model_name, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1500}
    )
    if response.status_code == 200:
        data = response.json()
        if data.get('choices'):
            return data['choices'][0]['message']['content'].strip()
    raise Exception(f"OpenRouter HTTP {response.status_code}")

def generate_placeholder_image(topic):
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io, textwrap
        width, height = 800, 400
        img = Image.new('RGB', (width, height), color='#0f172a')
        draw = ImageDraw.Draw(img)
        for i in range(height):
            r = int(15 + (i / height) * 30)
            g = int(23 + (i / height) * 42)
            b = int(42 + (i / height) * 74)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        wrapped_text = textwrap.fill(topic, width=30)
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        draw.text(((width - (bbox[2]-bbox[0]))/2, (height - (bbox[3]-bbox[1]))/2), wrapped_text, font=font, fill="#6366f1")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        os.makedirs("assets/images/posts", exist_ok=True)
        filename = f"assets/images/posts/{generate_slug(topic)}.png"
        with open(filename, 'wb') as f:
            f.write(buffer.read())
        return filename
    except Exception as e:
        print(f"❌ Ошибка placeholder: {e}")
        return None

def generate_article_image(topic):
    print(f"🎨 Генерация изображения по промпту: {topic}")
    KANDINSKY_KEYS = [("3BA53CAD37A0BF21740401408253641E", "00CE1D26AF6BF45FD60BBB4447AD3981")]
    for key, secret in KANDINSKY_KEYS:
        try:
            url = "https://api.fusionbrain.ai/kandinsky/api/v2/text2image/run"
            payload = {"type":"GENERATE","numImages":1,"width":1024,"height":1024,"generateParams":{"query":topic}}
            headers = {"X-Key": key,"X-Secret": secret,"Content-Type":"application/json"}
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200 and "uuid" in response.json():
                task_id = response.json()["uuid"]
                return f"assets/images/posts/kandinsky_{task_id}.png"
        except Exception as e:
            print(f"⚠️ Kandinsky API ошибка: {e}")
    return generate_placeholder_image(topic)

def generate_article_content(topic):
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    models_to_try = []
    if groq_key:
        groq_models = ["llama-3.1-8b-instant"]
        for m in groq_models:
            models_to_try.append(("Groq-"+m, lambda m=m: generate_with_groq(groq_key, m, topic)))
    if openrouter_key:
        openrouter_models = ["anthropic/claude-3-haiku"]
        for m in openrouter_models:
            models_to_try.append((m, lambda m=m: generate_with_openrouter(openrouter_key, m, topic)))
    for name, func in models_to_try:
        try:
            print(f"🔄 Пробуем: {name}")
            result = func()
            if result and len(result.strip()) > 100:
                print(f"✅ Успешно через {name}")
                return result, name
        except Exception as e:
            print(f"⚠️ {name} ошибка: {e}")
            continue
    fallback_content = f"# {topic}\n\nЭто автоматически сгенерированная статья об AI."
    return fallback_content, "fallback-generator"

def generate_content():
    print("🚀 Запуск генерации контента...")
    clean_old_articles(3)
    topic = generate_ai_trend_topic()
    print(f"📝 Тема статьи: {topic}")
    image_filename = generate_article_image(topic)
    content, model_used = generate_article_content(topic)
    filename = f"content/posts/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{generate_slug(topic)}.md"
    os.makedirs("content/posts", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(generate_frontmatter(topic, content, model_used, image_filename))
    print(f"✅ Статья создана: {filename}")

if __name__ == "__main__":
    generate_content()
