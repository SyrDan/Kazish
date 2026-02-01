from flask import Flask, render_template, request, jsonify
import os
import json
import re
from collections import Counter

app = Flask(__name__)  # FIXED: was "name" (undefined variable)

class EducationalTextAnalyzer:
    """Анализатор учебных текстов с использованием эвристических подходов"""
    
    def __init__(self):
        self.difficulty_keywords = {
            'начальный': ['основы', 'введение', 'начало', 'простой', 'базовый', 'первый'],
            'средний': ['применение', 'практика', 'использование', 'работа с', 'создание'],
            'продвинутый': ['оптимизация', 'архитектура', 'сложный', 'продвинутый', 'глубокое']
        }

    def extract_keywords(self, text, top_n=10):
        """Извлекает ключевые слова из текста"""
        words = re.findall(r'\b[а-яёa-z]{3,}\b', text.lower())  # FIXED: added ё
        
        stop_words = {
            'это', 'как', 'что', 'для', 'или', 'который', 'быть', 
            'весь', 'мочь', 'один', 'свой', 'она', 'так', 'же', 
            'the', 'is', 'in', 'and', 'or', 'to', 'a', 'of'  # FIXED: 'o f' → 'of'
        }
        
        filtered_words = [w for w in words if w not in stop_words]
        word_freq = Counter(filtered_words)
        return [word for word, _ in word_freq.most_common(top_n)]

    def determine_difficulty(self, text):
        """Определяет уровень сложности текста"""
        text_lower = text.lower()  # FIXED: was "text_l ower"
        scores = {}
        
        for level, keywords in self.difficulty_keywords.items():
            scores[level] = sum(1 for kw in keywords if kw in text_lower)
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if avg_len > 20:
            scores['продвинутый'] += 2
        elif avg_len > 12:
            scores['средний'] += 2
        else:
            scores['начальный'] += 2
        
        return max(scores, key=scores.get)

    def estimate_reading_time(self, text):
        """Оценивает время на изучение (200 слов/мин + практика)"""
        word_count = len(text.split())
        total_minutes = (word_count / 200) * 3  # FIXED: was "t otal_minutes"
        
        return f"{int(total_minutes)} минут" if total_minutes < 60 else f"{total_minutes/60:.1f} часов"

    def generate_study_plan(self, text, keywords):
        """Генерирует план обучения на основе текста"""
        difficulty = self.determine_difficulty(text)
        plan = {'approach': '', 'prerequisites': [], 'exercises': [], 'resources': []}  # FIXED: "resou rces"
        
        if difficulty == 'начальный':
            plan['approach'] = "Начните с изучения основных концепций. Делайте заметки и повторяйте ключевые моменты."
            plan['prerequisites'] = ['Базовая грамотность в теме', 'Желание учиться']
            plan['exercises'] = [
                'Перескажите основные идеи своими словами',
                'Создайте mindmap основных концепций',
                'Выполните простые практические задания'
            ]
        elif difficulty == 'средний':
            plan['approach'] = "Изучайте материал поэтапно, сочетая теорию с практикой."
            plan['prerequisites'] = ['Базовое понимание темы', 'Опыт работы с похожими концепциями']
            plan['exercises'] = [
                'Решите задачи средней сложности',
                'Создайте мини-проект',
                'Объясните концепции другому человеку'
            ]
        else:
            plan['approach'] = "Глубоко анализируйте материал. Изучайте дополнительные источники и кейсы."
            plan['prerequisites'] = ['Прочные знания основ', 'Опыт работы в области']
            plan['exercises'] = [
                'Решайте сложные практические задачи',  # FIXED: "Ан ализируйте" → "Анализируйте"
                'Анализируйте реальные кейсы',
                'Оптимизируйте существующие решения'
            ]
        
        plan['resources'] = [
            f'Онлайн-курсы по: {", ".join(keywords[:3])}',
            'Официальная документация',
            'Практические туториалы',
            'Сообщества и форумы'
        ]
        return plan

    def analyze(self, text):
        """Полный анализ учебного текста"""
        keywords = self.extract_keywords(text)
        difficulty = self.determine_difficulty(text)
        estimated_time = self.estimate_reading_time(text)
        learning_plan = self.generate_study_plan(text, keywords)
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        summary = '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else text[:200] + '...'
        
        return {
            'summary': summary,
            'key_concepts': keywords,
            'difficulty_level': difficulty,
            'learning_recommendations': learning_plan,  # FIXED: extra space
            'estimated_time': estimated_time,
            'related_topics': [f"Продвинутые аспекты {kw}" for kw in keywords[:3]]
        }

analyzer = EducationalTextAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'Текст не может быть пустым'}), 400
    if len(text) < 50:
        return jsonify({'error': 'Текст слишком короткий (минимум 50 символов)'}), 400
    
    try:
        analysis = analyzer.analyze(text)
        return jsonify({
            'analysis': analysis,
            'statistics': {
                'text_length': len(text),
                'word_count': len(text.split()),
                'sentence_count': len([s for s in text.split('.') if s.strip()])
            }
        })
    except Exception as e:
        return jsonify({'error': f'Ошибка анализа: {str(e)}'}), 500

@app.route('/suggest-plan', methods=['POST'])
def suggest_plan():
    data = request.get_json() or {}
    topic = data.get('topic', '').strip()
    if not topic:
        return jsonify({'error': 'Тема не может быть пустой'}), 400
    
    # FIXED: Removed broken strings/spaces in keys and values
    return jsonify({
        'topic': topic,
        'total_duration': '4-8 недель',
        'phases': [
            {
                'phase': 1,
                'title': 'Основы и теория',
                'duration': '1-2 недели',
                'goals': ['Понять базовые концепции', 'Изучить терминологию'],
                'activities': ['Чтение документации', 'Просмотр видео для начинающих', 'Ведение конспектов']
            },
            {
                'phase': 2,
                'title': 'Практическое применение',
                'duration': '2-3 недели',
                'goals': ['Применить теорию', 'Выполнить базовые задачи'],
                'activities': ['Упражнения', 'Учебные проекты', 'Анализ примеров']
            },
            {
                'phase': 3,
                'title': 'Углубление знаний',
                'duration': '2-4 недели',
                'goals': ['Освоить продвинутые техники', 'Создать проект'],
                'activities': ['Продвинутые концепции', 'Реальный проект', 'Оптимизация решений']
            },
            {
                'phase': 4,
                'title': 'Мастерство и закрепление',
                'duration': '1-2 недели',
                'goals': ['Закрепить знания', 'Создать портфолио'],
                'activities': ['Финальный проект', 'Повторение сложных тем', 'Презентация работы']
            }
        ],
        'daily_routine': {
            'theory': '30-45 минут',
            'practice': '1-2 часа',
            'review': '15-30 минут'
        },
        'resources': [
            f'Курсы по "{topic}"',
            'Документация',
            'YouTube-каналы',
            'Книги и задачи (LeetCode, HackerRank)',
            'Сообщества: Stack Overflow, Reddit'
        ],
        'tips': [
            'Учитесь ежедневно понемногу',
            'Делайте заметки и повторяйте',
            'Практика важнее теории',
            'Объясняйте изученное другим'
        ]
    })

@app.route('/quick-tips', methods=['POST'])
def quick_tips():
    return jsonify({
        'general': [
            'Начните с основ — не перепрыгивайте темы',
            'Практикуйтесь ежедневно (минимум 30 минут)',
            'Ведите конспекты ключевых моментов',
            'Присоединитесь к сообществу',
            'Ставьте конкретные цели на неделю'
        ],
        'learning_methods': [
            'Метод Фейнмана: объясните тему простыми словами',
            'Активное повторение: тестируйте себя',
            'Интервальное повторение: 1/3/7/14 дней',
            'Ошибки — часть обучения. Анализируйте их!'
        ],
        'productivity': [
            'Техника Pomodoro: 25 мин работа / 5 мин отдых',
            'Уберите отвлекающие факторы',
            'Найдите своё продуктивное время',
            'Делайте перерывы — мозгу нужен отдых'
        ]
    })

if __name__ == '__main__':  # FIXED: was "name"
    app.run(debug=True, host='0.0.0.0', port=5000)