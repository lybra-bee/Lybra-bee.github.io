#!/usr/bin/env python3
"""
Генератор контента для Hugo блога с AI-статьями и изображениями
"""

import os
import requests
import random
from datetime import datetime, timezone
import re
import logging
import argparse
import time
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = "8006769060:AAEGAKhjUeuAXfnsQWtdLcKpAjkJrrGQ1Fk"
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')

# ======== Генерация темы ========
def generate_ai_trend_topic():
    """Генерация случайной темы про AI тренды"""
    current_trends_2025 = [
        "Multimodal AI интеграция текста изображений и аудио",
        "AI агенты автономные системы",
        "Квантовые вычисления и машинное обучение", 
        "Нейроморфные вычисления энергоэффективные архитектуры",
        "Generative AI создание контента",
        "Edge AI обработка данных на устройстве",
        "AI для кибербезопасности",
        "Этичный AI ответственное развитие",
        "AI в healthcare диагностика",
        "Автономные системы робототехника",
        "Нейросети для обработки естественного языка",
        "Компьютерное зрение и распознавание образов",
        "Генеративные состязательные сети",
        "Трансформеры и большие языковые модели",
        "Обучение с подкреплением в AI"
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
        "в образовательных технологиях и EdTech",
        "в робототехнике и автоматизации",
        "в компьютерной графике и играх",
        "в обработке естественного языка",
        "в рекомендательных системах",
        "в прогнозной аналитике"
    ]
    
    trend = random.choice(current_trends_2025)
    domain = random.choice(application_domains)
    
    topic_formats = [
        f"{trend} {domain} в 2025 году",
        f"Тенденции 2025: {trend} {domain}",
        f"{trend}: революционные изменения {domain}",
        f"Как {trend} трансформирует {domain} в 2025",
        f"Инновации 2025: {trend} для {domain}",
        f"{trend} - будущее {domain}",
        f"Практическое применение {trend} в {domain}"
    ]
    
    return random.choice(topic_formats)

# ======== Генерация текста статьи ========
def generate_article_content(topic):
    """Генерация текста статьи через AI API"""
    try:
        # Пробуем Groq API
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key and groq_key not in ['', 'your_groq_api_key_here']:
            try:
                logger.info("🔄 Пробуем Groq API...")
                content = generate_with_groq(groq_key, topic)
                if content and len(content.strip()) > 200:
                    logger.info("✅ Успешно через Groq API")
                    logger.info(f"📄 Длина контента: {len(content)} символов")
                    return content
            except Exception as e:
                logger.error(f"❌ Ошибка Groq: {e}")
        
        # Пробуем OpenRouter API
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key and openrouter_key not in ['', 'your_openrouter_api_key_here']:
            try:
                logger.info("🔄 Пробуем OpenRouter API...")
                content = generate_with_openrouter(openrouter_key, topic)
                if content and len(content.strip()) > 200:
                    logger.info("✅ Успешно через OpenRouter API")
                    logger.info(f"📄 Длина контента: {len(content)} символов")
                    return content
            except Exception as e:
                logger.error(f"❌ Ошибка OpenRouter: {e}")
                
    except Exception as e:
        logger.error(f"❌ Общая ошибка генерации: {e}")
    
    # Fallback
    logger.info("🔄 Используем fallback контент")
    return generate_fallback_content(topic)

def generate_with_groq(api_key, topic):
    """Генерация через Groq API"""
    prompt = f"""Напиши развернутую статью на тему: '{topic}' на русском языке.

Требования:
- Формат Markdown
- 500-800 слов
- Структура: введение, основные разделы, заключение
- Профессиональный стиль написания
- Конкретные примеры и кейсы использования
- Актуальная информация на 2025 год
- Используй подзаголовки ## и ###
- Практические рекомендации и выводы
- Технические детали реализации
"""
    
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}", 
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}], 
            "max_tokens": 2500,
            "temperature": 0.7,
            "top_p": 0.9
        },
        timeout=45
    )
    
    if resp.status_code == 200:
        data = resp.json()
        content = data['choices'][0]['message']['content'].strip()
        if not content:
            raise Exception("Пустой ответ от API")
        return content
    else:
        error_msg = f"HTTP error {resp.status_code}"
        try:
            error_data = resp.json()
            error_msg += f": {error_data.get('error', {}).get('message', 'Unknown error')}"
        except:
            error_msg += f": {resp.text}"
        raise Exception(error_msg)

def generate_with_openrouter(api_key, topic):
    """Генерация через OpenRouter API"""
    prompt = f"""Напиши развернутую статью на тему: '{topic}' на русском языке.

Требования:
- Формат Markdown
- 600-900 слов
- Структурированный контент с заголовками разных уровней
- Практические примеры и case studies
- Профессиональный тон написания
- Актуальные данные и статистика 2025 года
- Выводы и рекомендации для читателей
- Технические детали и особенности реализации
"""
    
    # Пробуем несколько раз из-за возможных DNS проблем
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://api.openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}", 
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://lybra-bee.github.io",
                    "X-Title": "AI Content Generator"
                },
                json={
                    "model": "anthropic/claude-3-sonnet", 
                    "messages": [{"role": "user", "content": prompt}], 
                    "max_tokens": 2500,
                    "temperature": 0.7,
                    "top_p": 0.9
                },
                timeout=45
            )
            
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content'].strip()
                if not content:
                    raise Exception("Пустой ответ от API")
                return content
            else:
                raise Exception(f"HTTP error {resp.status_code}: {resp.text}")
                
        except Exception as e:
            if attempt == 2:  # Последняя попытка
                raise e
            time.sleep(2)
            logger.warning(f"🔄 Повторная попытка {attempt + 1}/3 для OpenRouter")

def generate_fallback_content(topic):
    """Улучшенный fallback контент"""
    return f"""# {topic}

## Введение
{topic} представляет собой одну из наиболее перспективных технологий 2025 года. Искусственный интеллект продолжает революционизировать различные отрасли, предлагая инновационные решения для сложных задач современности.

## Основные тенденции и вызовы
- **Автоматизация бизнес-процессов** и оптимизация рабочих потоков
- **Интеграция AI в существующие IT-системы** и инфраструктуру
- **Улучшение качества данных** и аналитических возможностей
- **Персонализация пользовательского опыта** с помощью машинного обучения
- **Этические аспекты** и безопасность AI систем
- **Масштабируемость** и управление AI решениями

## Практическое применение
Компании по всему миру активно внедряют AI решения для оптимизации своих бизнес-процессов. От автоматизации рутинных задач до сложного анализа данных - искусственный интеллект находит применение в самых разных областях и отраслях промышленности.

Крупные технологические компании и стартапы предлагают инновационные решения для различных сфер деятельности, от healthcare до финансовых технологий, демонстрируя впечатляющие результаты в повышении эффективности и снижении затрат.

## Технические аспекты реализации
Современные AI системы требуют тщательного проектирования архитектуры, качественных данных для обучения и грамотной интеграции с существующей IT-инфраструктурой. Важную роль играет также мониторинг и обслуживание работающих моделей машинного обучения, включая их обновление и дообучение на новых данных.

Не менее важны вопросы безопасности и защиты данных, особенно в свете ужесточающихся регуляторных требований и растущих киберугроз.

## Будущие перспективы и развитие
С развитием технологий машинного обучения и увеличением вычислительных мощностей, мы можем ожидать появления еще более sophisticated алгоритмов. Интеграция AI с другими emerging technologies, такими как квантовые вычисления и blockchain, открывает новые горизонты для инноваций.

Эксперты прогнозируют, что к 2026-2027 годам AI станет неотъемлемой частью большинства бизнес-процессов, а к 2030 году коренным образом преобразует многие отрасли экономики.

## Заключение
Будущее выглядит многообещающим с развитием AI технологий. По мере того как алгоритмы становятся более сложными и эффективными, мы можем ожидать появления еще более инновационных решений, которые изменят нашу жизнь к лучшему.

Важно сохранять баланс между технологическим прогрессом и этическими considerations, обеспечивая ответственное развитие и использование искусственного интеллекта.

*Статья сгенерирована автоматически*  
*Тема: {topic}*  
*Дата генерации: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""

# ======== Генерация изображений ========
def generate_article_image(topic):
    """Генерация изображения через Telegram бота"""
    try:
        prompt = f"{topic}, digital art, futuristic, professional, 4k, ultra detailed, high quality"
        
        logger.info(f"🎨 Запрос генерации изображения: {prompt}")
        
        # Отправляем запрос боту
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"/generate {prompt}",
                "parse_mode": "Markdown"
            },
            timeout=20
        )
        
        logger.info(f"📤 Ответ Telegram: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("✅ Запрос отправлен боту")
            
            # Даем время на генерацию + ответ бота
            logger.info("⏳ Ожидаем генерацию изображения (40 секунд)...")
            time.sleep(40)
            
            logger.info("✅ Предполагаем, что изображение сгенерировано")
            return f"/images/posts/{generate_slug(topic)}.jpg"
        else:
            logger.error(f"❌ Ошибка отправки запроса: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка генерации изображения: {e}")
    
    # Fallback - возвращаем путь к default изображению
    return "/images/default.jpg"

def generate_slug(text):
    """Генерация slug"""
    text = text.lower().replace(' ', '-')
    text = re.sub(r'[^a-z0-9\-]', '', text)
    return re.sub(r'-+', '-', text)[:60]

def clean_old_articles(keep_last=5):
    """Очистка старых статей"""
    content_dir = "content/posts"
    images_dir = "static/images/posts"
    
    # Очистка старых статей
    if os.path.exists(content_dir):
        posts = sorted([f for f in os.listdir(content_dir) if f.endswith('.md')], reverse=True)
        for post in posts[keep_last:]:
            os.remove(os.path.join(content_dir, post))
            logger.info(f"🗑️ Удален старый пост: {post}")
            
            # Пробуем удалить соответствующее изображение
            image_name = os.path.splitext(post)[0] + '.jpg'
            image_path = os.path.join(images_dir, image_name)
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"🗑️ Удалено старое изображение: {image_name}")

def main():
    parser = argparse.ArgumentParser(description='Генератор AI контента')
    parser.add_argument('--count', type=int, default=1, help='Количество статей')
    parser.add_argument('--keep', type=int, default=5, help='Сколько статей оставлять')
    parser.add_argument('--debug', action='store_true', help='Режим отладки')
    args = parser.parse_args()
    
    # Включение debug режима
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔧 Режим отладки включен")
    
    # Проверка переменных окружения
    logger.info("🔍 Проверка переменных окружения:")
    env_vars = {
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID')
    }
    
    for var, value in env_vars.items():
        status = "установлен" if value and value not in ['', f'your_{var.lower()}_here'] else "не установлен"
        logger.info(f"   {var}: {status}")
    
    # Очистка старых статей
    clean_old_articles(args.keep)
    
    for i in range(args.count):
        topic = generate_ai_trend_topic()
        logger.info(f"📝 Генерация статьи {i+1}/{args.count}: {topic}")
        
        # Генерация контента
        content = generate_article_content(topic)
        image_path = generate_article_image(topic)
        
        # Сохранение статьи
        slug = generate_slug(topic)
        filename = f"content/posts/{slug}.md"
        
        os.makedirs("content/posts", exist_ok=True)
        os.makedirs("static/images/posts", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"""---
title: "{topic.replace('"', "'")}"
date: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
image: "{image_path}"
draft: false
tags: ["ai", "технологии", "2025", "нейросети"]
categories: ["Искусственный интеллект"]
summary: "Автоматически сгенерированная статья о тенденциях AI в 2025 году"
---

{content}
""")
        
        logger.info(f"✅ Статья сохранена: {filename}")
        
        if i < args.count - 1:
            time.sleep(3)

if __name__ == "__main__":
    main()
