#!/usr/bin/env python3
import os
import json
import requests
import random
from datetime import datetime, timezone
import shutil
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont
import time
import logging
import argparse
import base64
import io

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ======== Генерация темы ========
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

# ======== Очистка старых статей ========
def clean_old_articles(keep_last=3):
    logger.info(f"🧹 Очистка старых статей, оставляем {keep_last} последних...")
    content_dir = "content"
    if os.path.exists(content_dir):
        # Удаляем только старые файлы, оставляя последние keep_last
        posts_dir = os.path.join(content_dir, "posts")
        if os.path.exists(posts_dir):
            posts = sorted([f for f in os.listdir(posts_dir) if f.endswith('.md')], 
                          reverse=True)
            for post in posts[keep_last:]:
                os.remove(os.path.join(posts_dir, post))
                logger.info(f"🗑️ Удален старый пост: {post}")
    else:
        os.makedirs("content/posts", exist_ok=True)
        with open("content/_index.md", "w", encoding="utf-8") as f:
            f.write("---\ntitle: \"Главная\"\n---")
        with open("content/posts/_index.md", "w", encoding="utf-8") as f:
            f.write("---\ntitle: \"Статьи\"\n---")
        logger.info("✅ Создана структура content")

# ======== Генерация статьи ========
def generate_content():
    logger.info("🚀 Запуск генерации контента...")
    
    # Проверка переменных окружения
    check_environment_variables()
    
    clean_old_articles()
    
    topic = generate_ai_trend_topic()
    logger.info(f"📝 Тема статьи: {topic}")
    
    image_filename = generate_article_image(topic)
    content, model_used = generate_article_content(topic)
    
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = generate_slug(topic)
    filename = f"content/posts/{date}-{slug}.md"
    
    frontmatter = generate_frontmatter(topic, content, model_used, image_filename)
    
    os.makedirs("content/posts", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    logger.info(f"✅ Статья создана: {filename}")
    return filename

def check_environment_variables():
    """Проверка всех необходимых переменных окружения"""
    env_vars = {
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY')
    }
    
    logger.info("🔍 Проверка переменных окружения:")
    for var_name, var_value in env_vars.items():
        status = "✅ установлен" if var_value else "❌ отсутствует"
        logger.info(f"   {var_name}: {status}")

# ======== Генерация текста через OpenRouter/Groq ========
def generate_article_content(topic):
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    models_to_try = []

    if groq_key:
        groq_models = ["llama-3.1-8b-instant", "llama-3.2-1b-preview", "llama-3.1-70b-versatile"]
        for model_name in groq_models:
            models_to_try.append((f"Groq-{model_name}", lambda m=model_name: generate_with_groq(groq_key, m, topic)))
    if openrouter_key:
        openrouter_models = ["anthropic/claude-3-haiku", "anthropic/claude-3-sonnet", "google/gemini-pro-1.5"]
        for model_name in openrouter_models:
            models_to_try.append((model_name, lambda m=model_name: generate_with_openrouter(openrouter_key, m, topic)))

    # Если нет API ключей, используем fallback
    if not models_to_try:
        logger.warning("⚠️ Нет доступных API ключей для генерации текста")
        fallback = generate_fallback_content(topic)
        return fallback, "fallback-generator"

    for model_name, generate_func in models_to_try:
        try:
            logger.info(f"🔄 Пробуем генерацию текста: {model_name}")
            result = generate_func()
            if result and len(result.strip()) > 100:
                logger.info(f"✅ Успешно через {model_name}")
                return result, model_name
            else:
                logger.warning(f"⚠️ Пустой ответ от {model_name}")
        except Exception as e:
            logger.error(f"❌ Ошибка {model_name}: {e}")
            continue

    logger.warning("⚠️ Все модели не сработали, используем fallback")
    fallback = generate_fallback_content(topic)
    return fallback, "fallback-generator"

def generate_fallback_content(topic):
    """Fallback контент если все API не работают"""
    sections = [
        f"# {topic}",
        "",
        "## Введение",
        f"Тема '{topic}' становится increasingly important в 2025 году. ",
        "",
        "## Основные тенденции",
        "- Автоматизация процессов разработки",
        "- Интеграция AI в существующие workflow",
        "- Улучшение качества и скорости разработки",
        "",
        "## Практическое применение",
        "Компании внедряют AI решения для оптимизации своих процессов.",
        "",
        "## Заключение",
        "Будущее выглядит promising с развитием AI технологий.",
        "",
        "*Статья сгенерирована автоматически*"
    ]
    return "\n".join(sections)

def generate_with_groq(api_key, model_name, topic):
    prompt = f"""Напиши развернутую статью на тему: '{topic}' на русском языке.

Требования:
- Формат Markdown
- 400-600 слов
- Структура: введение, основные разделы, заключение
- Профессиональный стиль
- Конкретные примеры и кейсы
"""
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model_name, 
            "messages":[{"role":"user","content":prompt}], 
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.9
        },
        timeout=30
    )
    
    if resp.status_code == 200:
        data = resp.json()
        return data['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"Groq API error {resp.status_code}: {resp.text}")

def generate_with_openrouter(api_key, model_name, topic):
    prompt = f"""Напиши развернутую статью на тему: '{topic}' на русском языке.

Требования:
- Формат Markdown
- 400-600 слов
- Структурированный контент с заголовками
- Практические примеры
- Профессиональный тон
"""
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}", 
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-content-generator.com",
            "X-Title": "AI Content Generator"
        },
        json={
            "model": model_name, 
            "messages":[{"role":"user","content":prompt}], 
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.9
        },
        timeout=30
    )
    
    if resp.status_code == 200:
        data = resp.json()
        return data['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"OpenRouter API error {resp.status_code}: {resp.text}")

# ======== БЕСПЛАТНАЯ Генерация изображений ========
def generate_article_image(topic):
    """Генерация изображения через бесплатные API без токенов"""
    logger.info(f"🎨 Генерация изображения по промпту: {topic}")
    
    prompt = f"{topic}, digital art, futuristic, AI technology, 4k, high quality, trending"
    
    # Список бесплатных API (без токенов)
    free_apis = [
        try_proxyfusion,         # Бесплатный прокси-API
        try_huggingface_public,  # Публичные модели HF
        try_deepai_public,       # DeepAI без ключа
        try_quickai,             # QuickAI API
        try_openart,             # OpenArt API
        try_aiimagery,           # AI Imagery
        try_fusionbrain_public,  # FusionBrain публичный
        try_stablediffusionapi,  # Stable Diffusion API
        try_craiyon,             # Craiyon (DALL-E mini)
        try_leonardo_public,     # Leonardo публичный
        try_nightcafe_public,    # NightCafe публичный
        try_artbreeder,          # ArtBreeder
        try_getimg,              # GetImg.ai
        try_ai21,                # AI21 Studio
        try_deepdreamgenerator   # Deep Dream Generator
    ]
    
    # Перемешиваем порядок для балансировки нагрузки
    random.shuffle(free_apis)
    
    for api_func in free_apis:
        try:
            logger.info(f"🔄 Пробуем {api_func.__name__}")
            result = api_func(prompt[:180], topic)  # Ограничиваем длину промпта
            if result:
                logger.info(f"✅ Успешно через {api_func.__name__}")
                return result
            time.sleep(1)  # Пауза между запросами
        except Exception as e:
            logger.error(f"❌ Ошибка в {api_func.__name__}: {e}")
            continue
    
    # Если все API не сработали, используем placeholder
    logger.warning("✅ Все бесплатные API не сработали, используем placeholder")
    return generate_placeholder_image(topic)

def try_proxyfusion(prompt, topic):
    """ProxyFusion API - бесплатный прокси для Stable Diffusion"""
    try:
        response = requests.post(
            "https://api.proxyfusion.ai/generate",
            json={"prompt": prompt, "width": 512, "height": 512},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("image_url"):
                return save_image_from_url(data["image_url"], topic)
    except:
        pass
    return None

def try_huggingface_public(prompt, topic):
    """Hugging Face публичные модели без токена"""
    try:
        # Пробуем разные публичные модели
        models = [
            "runwayml/stable-diffusion-v1-5",
            "stabilityai/stable-diffusion-2-1",
            "prompthero/openjourney"
        ]
        
        for model in models:
            try:
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    json={"inputs": prompt},
                    timeout=25
                )
                if response.status_code == 200:
                    filename = save_image_bytes(response.content, topic)
                    if filename:
                        return filename
            except:
                continue
    except:
        pass
    return None

def try_deepai_public(prompt, topic):
    """DeepAI API с публичным ключом"""
    try:
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            headers={'api-key': 'quickstart-credential'},
            data={'text': prompt},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('output_url'):
                return save_image_from_url(data['output_url'], topic)
    except:
        pass
    return None

def try_quickai(prompt, topic):
    """QuickAI API - бесплатный сервис"""
    try:
        response = requests.post(
            "https://api.quickai.io/generate",
            json={"prompt": prompt, "size": "512x512"},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("image"):
                # Декодируем base64
                image_data = base64.b64decode(data["image"])
                return save_image_bytes(image_data, topic)
    except:
        pass
    return None

def try_openart(prompt, topic):
    """OpenArt API - бесплатные генерации"""
    try:
        response = requests.post(
            "https://api.openart.ai/v1/generate",
            json={"prompt": prompt, "width": 512, "height": 512},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("image_url"):
                return save_image_from_url(data["image_url"], topic)
    except:
        pass
    return None

def try_aiimagery(prompt, topic):
    """AI Imagery API"""
    try:
        response = requests.post(
            "https://api.aiimagery.io/generate",
            json={"prompt": prompt, "size": "512x512"},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("url"):
                return save_image_from_url(data["url"], topic)
    except:
        pass
    return None

def try_fusionbrain_public(prompt, topic):
    """FusionBrain публичный API"""
    try:
        response = requests.post(
            "https://api.fusionbrain.ai/generate",
            json={"prompt": prompt, "style": "digital-art"},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("image"):
                image_data = base64.b64decode(data["image"])
                return save_image_bytes(image_data, topic)
    except:
        pass
    return None

def try_stablediffusionapi(prompt, topic):
    """Stable Diffusion API"""
    try:
        response = requests.post(
            "https://api.stablediffusionapi.com/generate",
            json={"prompt": prompt, "width": 512, "height": 512},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("output"):
                return save_image_from_url(data["output"][0], topic)
    except:
        pass
    return None

def try_craiyon(prompt, topic):
    """Craiyon (бывший DALL-E mini)"""
    try:
        response = requests.post(
            "https://api.craiyon.com/generate",
            json={"prompt": prompt},
            timeout=25
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("images"):
                # Берем первую картинку из base64
                image_data = base64.b64decode(data["images"][0])
                return save_image_bytes(image_data, topic)
    except:
        pass
    return None

def try_leonardo_public(prompt, topic):
    """Leonardo AI публичный доступ"""
    try:
        response = requests.post(
            "https://api.leonardo.ai/public/generate",
            json={"prompt": prompt, "model": "creative"},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("image_url"):
                return save_image_from_url(data["image_url"], topic)
    except:
        pass
    return None

def try_nightcafe_public(prompt, topic):
    """NightCafe Studio публичный API"""
    try:
        response = requests.post(
            "https://api.nightcafe.studio/v1/public/generate",
            json={"prompt": prompt, "style": "digital-art"},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("url"):
                return save_image_from_url(data["url"], topic)
    except:
        pass
    return None

def try_artbreeder(prompt, topic):
    """ArtBreeder API"""
    try:
        response = requests.post(
            "https://api.artbreeder.com/generate",
            json={"prompt": prompt},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("imageUrl"):
                return save_image_from_url(data["imageUrl"], topic)
    except:
        pass
    return None

def try_getimg(prompt, topic):
    """GetImg.ai API"""
    try:
        response = requests.post(
            "https://api.getimg.ai/generate",
            json={"prompt": prompt, "width": 512, "height": 512},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("image"):
                image_data = base64.b64decode(data["image"])
                return save_image_bytes(image_data, topic)
    except:
        pass
    return None

def try_ai21(prompt, topic):
    """AI21 Studio API"""
    try:
        response = requests.post(
            "https://api.ai21.com/studio/v1/image/generate",
            json={"prompt": prompt, "size": "512x512"},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("image"):
                image_data = base64.b64decode(data["image"])
                return save_image_bytes(image_data, topic)
    except:
        pass
    return None

def try_deepdreamgenerator(prompt, topic):
    """Deep Dream Generator API"""
    try:
        response = requests.post(
            "https://api.deepdreamgenerator.com/generate",
            json={"prompt": prompt},
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("image_url"):
                return save_image_from_url(data["image_url"], topic)
    except:
        pass
    return None

def save_image_bytes(image_data, topic):
    """Сохранение изображения из bytes"""
    try:
        os.makedirs("assets/images/posts", exist_ok=True)
        filename = f"assets/images/posts/{generate_slug(topic)}.png"
        
        with open(filename, "wb") as f:
            f.write(image_data)
        
        return filename
    except:
        return None

def save_image_from_url(url, topic):
    """Сохранение изображения из URL"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return save_image_bytes(response.content, topic)
    except:
        return None

def generate_placeholder_image(topic):
    """Создание placeholder изображения"""
    try:
        os.makedirs("assets/images/posts", exist_ok=True)
        filename = f"assets/images/posts/{generate_slug(topic)}.png"
        width, height = 800, 400
        
        img = Image.new('RGB', (width, height), color='#0f172a')
        draw = ImageDraw.Draw(img)
        
        # Градиент
        for i in range(height):
            r = int(15 + (i/height)*30)
            g = int(23 + (i/height)*42)
            b = int(42 + (i/height)*74)
            draw.line([(0,i), (width,i)], fill=(r,g,b))
        
        # Текст
        wrapped_text = textwrap.fill(topic, width=30)
        try:
            font = ImageFont.truetype("Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        x = (width - (bbox[2] - bbox[0])) / 2
        y = (height - (bbox[3] - bbox[1])) / 2
        
        draw.text((x+2, y+2), wrapped_text, font=font, fill="#000000")
        draw.text((x, y), wrapped_text, font=font, fill="#6366f1")
        
        img.save(filename)
        return filename
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания placeholder: {e}")
        return "assets/images/default.png"

# ======== Вспомогательные функции ========
def generate_slug(text):
    text = text.lower()
    text = text.replace(' ', '-')
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text)
    return text[:60]

def generate_frontmatter(title, content, model_used, image_url):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    escaped_title = title.replace(':', ' -').replace('"', "'")
    
    frontmatter = f"""---
title: "{escaped_title}"
date: {now}
draft: false
image: "{image_url}"
ai_model: "{model_used}"
tags: ["ai", "технологии", "2025"]
categories: ["Искусственный интеллект"]
summary: "Автоматически сгенерированная статья о тенденциях AI в 2025 году"
---

{content}
"""
    return frontmatter

# ======== Запуск ========
def main():
    parser = argparse.ArgumentParser(description='Генератор AI контента')
    parser.add_argument('--debug', action='store_true', help='Включить debug режим')
    parser.add_argument('--count', type=int, default=1, help='Количество статей для генерации')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🚀 Запуск генератора контента...")
    print("=" * 50)
    
    check_environment_variables()
    print("=" * 50)
    
    try:
        for i in range(args.count):
            print(f"\n📄 Генерация статьи {i+1}/{args.count}...")
            filename = generate_content()
            print(f"✅ Статья создана: {filename}")
            
            if i < args.count - 1:
                time.sleep(2)
                
        print("\n🎉 Все статьи успешно сгенерированы!")
        
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
