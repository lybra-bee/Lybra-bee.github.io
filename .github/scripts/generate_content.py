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

# ======== Генерация текста статьи ========
def generate_article_content(topic):
    """Генерация текста статьи через AI API"""
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    
    logger.info(f"🔍 Проверка API ключей: Groq={bool(groq_key)}, OpenRouter={bool(openrouter_key)}")
    
    # Пробуем Groq API
    if groq_key and groq_key not in ['your_groq_api_key_here', '']:
        try:
            logger.info("🔄 Пробуем Groq API...")
            content = generate_with_groq(groq_key, "llama-3.1-70b-versatile", topic)
            if content and len(content.strip()) > 200:
                logger.info("✅ Успешно через Groq API")
                return content
            else:
                logger.warning("⚠️ Слишком короткий ответ от Groq")
        except Exception as e:
            logger.error(f"❌ Ошибка Groq API: {str(e)}")
    
    # Пробуем OpenRouter API
    if openrouter_key and openrouter_key not in ['your_openrouter_api_key_here', '']:
        try:
            logger.info("🔄 Пробуем OpenRouter API...")
            content = generate_with_openrouter(openrouter_key, "anthropic/claude-3-sonnet", topic)
            if content and len(content.strip()) > 200:
                logger.info("✅ Успешно через OpenRouter API")
                return content
            else:
                logger.warning("⚠️ Слишком короткий ответ от OpenRouter")
        except Exception as e:
            logger.error(f"❌ Ошибка OpenRouter API: {str(e)}")
    
    # Fallback
    logger.info("🔄 Используем fallback контент")
    return generate_fallback_content(topic)

def generate_with_groq(api_key, model_name, topic):
    """Генерация через Groq API"""
    prompt = f"""Напиши развернутую статью на тему: '{topic}' на русском языке.

Требования:
- Формат Markdown
- 400-600 слов
- Структура: введение, основные разделы, заключение
- Профессиональный стиль написания
- Конкретные примеры и кейсы использования
- Актуальная информация на 2025 год
- Используй подзаголовки ## и ###
- Практические рекомендации и выводы
"""
    
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}", 
            "Content-Type": "application/json"
        },
        json={
            "model": model_name, 
            "messages": [{"role": "user", "content": prompt}], 
            "max_tokens": 2500,
            "temperature": 0.7,
            "top_p": 0.9
        },
        timeout=60
    )
    
    if resp.status_code == 200:
        data = resp.json()
        content = data['choices'][0]['message']['content'].strip()
        if not content:
            raise Exception("Пустой ответ от API")
        return content
    else:
        raise Exception(f"HTTP error {resp.status_code}: {resp.text}")

def generate_with_openrouter(api_key, model_name, topic):
    """Генерация через OpenRouter API"""
    prompt = f"""Напиши развернутую статью на тему: '{topic}' на русском языке.

Требования:
- Формат Markdown
- 500-800 слов
- Структурированный контент с заголовками разных уровней
- Практические примеры и case studies
- Профессиональный тон написания
- Актуальные данные и статистика 2025 года
- Выводы и рекомендации для читателей
- Технические детали и особенности реализации
"""
    
    resp = requests.post(
        "https://api.openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}", 
            "Content-Type": "application/json",
            "HTTP-Referer": "https://lybra-bee.github.io",
            "X-Title": "AI Content Generator"
        },
        json={
            "model": model_name, 
            "messages": [{"role": "user", "content": prompt}], 
            "max_tokens": 2500,
            "temperature": 0.7,
            "top_p": 0.9
        },
        timeout=60
    )
    
    if resp.status_code == 200:
        data = resp.json()
        content = data['choices'][0]['message']['content'].strip()
        if not content:
            raise Exception("Пустой ответ от API")
        return content
    else:
        raise Exception(f"HTTP error {resp.status_code}: {resp.text}")

def generate_fallback_content(topic):
    """Улучшенный fallback контент"""
    sections = [
        f"# {topic}",
        "",
        "## Введение",
        f"Тема \"{topic}\" становится одной из самых актуальных в 2025 году. ",
        "Искусственный интеллект продолжает трансформировать различные отрасли, ",
        "предлагая инновационные решения для сложных задач и вызовов современности.",
        "",
        "## Основные тенденции и вызовы",
        "- Автоматизация бизнес-процессов и рабочих потоков",
        "- Интеграция AI в существующие IT-системы и инфраструктуру",  
        "- Улучшение качества данных и аналитических возможностей",
        "- Персонализация пользовательского опыта с помощью машинного обучения",
        "- Этические аспекты и безопасность AI систем",
        "- Масштабируемость и управление AI решениями",
        "",
        "## Практическое применение и кейсы",
        "Компании по всему миру активно внедряют AI решения для оптимизации ",
        "своих бизнес-процессов. От автоматизации рутинных задач до сложного ",
        "анализа данных - искусственный интеллект находит применение в самых ",
        "разных областях и отраслях промышленности. Крупные технологические ",
        "компании и стартапы предлагают инновационные решения для различных ",
        "сфер деятельности, от healthcare до финансовых технологий.",
        "",
        "## Технические аспекты реализации",
        "Современные AI системы требуют тщательного проектирования архитектуры, ",
        "качественных данных для обучения и грамотной интеграции с существующей ",
        "IT-инфраструктурой. Важную роль играет также мониторинг и обслуживание ",
        "работающих моделей машинного обучения, включая их обновление и дообучение ",
        "на новых данных. Не менее важны вопросы безопасности и защиты данных.",
        "",
        "## Будущие перспективы и развитие",
        "С развитием технологий машинного обучения и увеличения вычислительных ",
        "мощностей, мы можем ожидать появления еще более sophisticated алгоритмов. ",
        "Интеграция AI с другими emerging technologies, такими как квантовые вычисления ",
        "и blockchain, открывает новые горизонты для инноваций.",
        "",
        "## Заключение",
        "Будущее выглядит многообещающим с развитием AI технологий. По мере того как ",
        "алгоритмы становятся более сложными и эффективными, мы можем ожидать появления ",
        "еще более инновационных решений, которые изменят нашу жизнь к лучшему. ",
        "Важно сохранять баланс между технологическим прогрессом и этическими considerations.",
        "",
        "---",
        f"*Статья сгенерирована автоматически*  \n",
        f"*Тема: {topic}*  \n",
        f"*Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
    ]
    return "\n".join(sections)

# ======== Генерация изображений ========
def generate_article_image(topic):
    """Генерация изображения через Telegram бота"""
    try:
        prompt = f"{topic}, digital art, futuristic, professional, 4k, high quality, trending"
        
        logger.info(f"🎨 Запрос генерации изображения: {prompt}")
        
        # Отправляем запрос боту на генерацию
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"/generate {prompt}",
                "parse_mode": "Markdown"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Запрос на генерацию отправлен боту")
            
            # Даем время на генерацию изображения
            time.sleep(40)
            
            return f"/images/posts/{generate_slug(topic)}.jpg"
        else:
            logger.error(f"❌ Ошибка отправки запроса: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка генерации изображения: {e}")
    
    # Fallback - возвращаем путь к default изображению
    return "/images/default.jpg"

def generate_slug(text):
    """Генерация SEO-friendly slug"""
    text = text.lower().replace(' ', '-')
    text = re.sub(r'[^a-z0-9\-]', '', text)
    return re.sub(r'-+', '-', text)[:50]

def clean_old_articles(keep_last=5):
    """Очистка старых статей"""
    content_dir = "content/posts"
    if os.path.exists(content_dir):
        posts = sorted([f for f in os.listdir(content_dir) if f.endswith('.md')], reverse=True)
        for post in posts[keep_last:]:
            os.remove(os.path.join(content_dir, post))
            logger.info(f"🗑️ Удален старый пост: {post}")

def main():
    parser = argparse.ArgumentParser(description='Генератор AI контента')
    parser.add_argument('--count', type=int, default=1, help='Количество статей')
    parser.add_argument('--keep', type=int, default=5, help='Сколько статей оставлять')
    parser.add_argument('--debug', action='store_true', help='Режим отладки')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Проверка переменных окружения
    logger.info("🔍 Проверка переменных окружения:")
    logger.info(f"   OPENROUTER_API_KEY: {'установлен' if os.getenv('OPENROUTER_API_KEY') else 'не установлен'}")
    logger.info(f"   GROQ_API_KEY: {'установлен' if os.getenv('GROQ_API_KEY') else 'не установлен'}")
    logger.info(f"   TELEGRAM_BOT_TOKEN: {'установлен' if os.getenv('TELEGRAM_BOT_TOKEN') else 'не установлен'}")
    logger.info(f"   TELEGRAM_CHAT_ID: {'установлен' if os.getenv('TELEGRAM_CHAT_ID') else 'не установлен'}")
    
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
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"""---
title: "{topic.replace('"', "'")}"
date: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
image: "{image_path}"
draft: false
tags: ["ai", "технологии", "2025"]
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
