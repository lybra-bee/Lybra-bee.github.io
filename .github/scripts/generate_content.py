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
        'EDENAI_API_KEY': os.getenv('EDENAI_API_KEY'),
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY')
    }
    
    logger.info("🔍 Проверка переменных окружения:")
    for var_name, var_value in env_vars.items():
        status = "✅ установлен" if var_value else "❌ отсутствует"
        logger.info(f"   {var_name}: {status}")
        
        if not var_value and var_name == 'EDENAI_API_KEY':
            logger.warning("⚠️  EDENAI_API_KEY не установлен! Генерация изображений будет через placeholder")

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

# ======== Eden AI генерация изображения ========
EDENAI_KEY = os.getenv('EDENAI_API_KEY')

# Актуальные провайдеры Eden AI (проверенные)
EDENAI_PROVIDERS = [
    "openai",  # OpenAI DALL-E
    "stability",  # Stability AI
    "leonardo",  # Leonardo AI
    "deepai",  # DeepAI
    "replicate"  # Replicate
]

def generate_article_image(topic):
    logger.info(f"🎨 Генерация изображения через Eden AI по промпту: {topic}")
    prompt = topic[:150]  # укоротим промпт
    
    if not EDENAI_KEY:
        logger.error("❌ EDENAI_API_KEY не установлен в переменных окружения")
        return generate_placeholder_image(topic)
    
    logger.info(f"🔑 Токен Eden AI: {EDENAI_KEY[:8]}...{EDENAI_KEY[-4:]}")
    
    # Сначала проверяем статус аккаунта
    if not check_edenai_account_status():
        logger.warning("⚠️ Проблема с аккаунтом Eden AI, используем placeholder")
        return generate_placeholder_image(topic)
    
    for provider in EDENAI_PROVIDERS:
        try:
            logger.info(f"🔄 Пробуем провайдер: {provider}")
            
            # Базовые настройки
            resolution = "512x512"
            if provider in ["openai", "leonardo", "stability"]:
                resolution = "1024x1024"
            
            payload = {
                "providers": provider, 
                "text": prompt, 
                "resolution": resolution,
                "num_images": 1
            }
            
            # Специфичные настройки для провайдеров
            provider_settings = {}
            if provider == "openai":
                provider_settings = {"model": "dall-e-2"}  # dall-e-3 может требовать больше кредитов
            elif provider == "stability":
                provider_settings = {"style_preset": "digital-art"}
            elif provider == "leonardo":
                provider_settings = {"model": "leonardo-creative"}
            
            if provider_settings:
                payload["settings"] = {provider: provider_settings}
            
            start_time = time.time()
            
            resp = requests.post(
                "https://api.edenai.run/v2/image/generation",
                headers={
                    "Authorization": f"Bearer {EDENAI_KEY}", 
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json=payload,
                timeout=60
            )
            
            response_time = time.time() - start_time
            logger.info(f"⏱️ Время ответа {provider}: {response_time:.2f} сек")
            logger.info(f"📊 Статус код: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                logger.debug(f"📋 Ответ от {provider}: {json.dumps(data, ensure_ascii=False)[:500]}...")
                
                if data and isinstance(data, dict):
                    if "error" in data:
                        logger.error(f"❌ {provider} error: {data['error']}")
                        continue
                    
                    if provider in data and isinstance(data[provider], dict):
                        provider_data = data[provider]
                        if "status" in provider_data and provider_data["status"] == "success":
                            image_url = provider_data.get("url")
                            if image_url:
                                logger.info(f"✅ Получен URL изображения от {provider}")
                                filename = save_image_from_url(image_url, topic)
                                if filename:
                                    return filename
                        else:
                            error_msg = provider_data.get("error", {}).get("message", "Unknown error")
                            logger.error(f"❌ {provider} failed: {error_msg}")
                    else:
                        logger.warning(f"⚠️ Неожиданный формат ответа от {provider}")
            
            elif resp.status_code == 400:
                logger.error(f"❌ {provider}: Bad Request - проверьте параметры запроса")
                logger.debug(f"📋 Ответ 400: {resp.text[:200]}...")
            elif resp.status_code == 402:
                logger.error(f"❌ {provider}: Недостаточно средств на счете")
            elif resp.status_code == 401:
                logger.error(f"❌ {provider}: Неверный API ключ")
            elif resp.status_code == 403:
                logger.error(f"❌ {provider}: Доступ запрещен")
            elif resp.status_code == 429:
                logger.error(f"❌ {provider}: Слишком много запросов")
            else:
                logger.error(f"❌ {provider}: Неожиданный статус код {resp.status_code}")
                logger.debug(f"📋 Ответ: {resp.text[:200]}...")
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ {provider}: Таймаут запроса")
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ {provider}: Ошибка соединения")
        except Exception as e:
            logger.error(f"❌ Исключение с {provider}: {str(e)}")
        
        # Пауза между запросами
        time.sleep(3)
    
    logger.warning("✅ Все провайдеры Eden AI не сработали, используем placeholder")
    return generate_placeholder_image(topic)

def check_edenai_account_status():
    """Проверка статуса аккаунта Eden AI"""
    try:
        resp = requests.get(
            "https://api.edenai.run/v1/account",
            headers={"Authorization": f"Bearer {EDENAI_KEY}"},
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"📊 Баланс Eden AI: {data.get('credit_balance', 'N/A')}")
            logger.info(f"📊 Статус аккаунта: {data.get('status', 'N/A')}")
            return True
        else:
            logger.error(f"❌ Ошибка проверки аккаунта: {resp.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка проверки статуса аккаунта: {e}")
        return False

def save_image_from_url(url, topic):
    try:
        logger.info(f"📥 Загрузка изображения из: {url[:100]}...")
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            os.makedirs("assets/images/posts", exist_ok=True)
            filename = f"assets/images/posts/{generate_slug(topic)}.png"
            
            with open(filename, "wb") as f:
                f.write(resp.content)
            
            logger.info(f"✅ Изображение сохранено: {filename}")
            return filename
        else:
            logger.error(f"❌ Ошибка загрузки изображения: статус {resp.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении изображения: {e}")
        return None

def generate_placeholder_image(topic):
    """Создание placeholder изображения с градиентом и текстом"""
    try:
        os.makedirs("assets/images/posts", exist_ok=True)
        filename = f"assets/images/posts/{generate_slug(topic)}.png"
        width, height = 800, 400
        
        # Создаем градиентный фон
        img = Image.new('RGB', (width, height), color='#0f172a')
        draw = ImageDraw.Draw(img)
        
        # Создаем градиент
        for i in range(height):
            r = int(15 + (i/height)*30)
            g = int(23 + (i/height)*42)
            b = int(42 + (i/height)*74)
            draw.line([(0,i), (width,i)], fill=(r,g,b))
        
        # Добавляем текст
        wrapped_text = textwrap.fill(topic, width=30)
        
        # Пробуем разные шрифты
        font = None
        font_sizes = [24, 22, 20, 18]
        
        for font_size in font_sizes:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
                break
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # Рассчитываем позицию текста
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        # Тень текста
        draw.text((x+2, y+2), wrapped_text, font=font, fill="#000000", align="center")
        # Основной текст
        draw.text((x, y), wrapped_text, font=font, fill="#6366f1", align="center")
        
        # Добавляем watermark
        watermark = "AI Generated"
        draw.text((10, height - 25), watermark, font=ImageFont.load_default(), fill="#ffffff")
        
        img.save(filename)
        logger.info(f"✅ Placeholder изображение создано: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания placeholder: {e}")
        # Fallback - простейшее изображение
        try:
            filename = f"assets/images/posts/{generate_slug(topic)}.png"
            img = Image.new('RGB', (100, 100), color='blue')
            img.save(filename)
            return filename
        except:
            return "assets/images/default.png"

# ======== Вспомогательные функции ========
def generate_slug(text):
    text = text.lower()
    text = text.replace(' ', '-')
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text)  # Удаляем повторяющиеся дефисы
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
        logger.debug("🔧 Debug режим включен")
    
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
                print("⏳ Пауза между статьями...")
                time.sleep(5)
                
        print("\n🎉 Все статьи успешно сгенерированы!")
        
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
