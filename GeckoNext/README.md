# Gecko Next

**Веб-платформа для разметки аудио- и видеоданных**  
MVP для студенческого хакатона Gecko Next

---

## О проекте

Gecko Next — это современный инструмент для разметки речевых данных.  
Позволяет загружать аудио и предразметку (JSON), редактировать сегменты, текст, работать с ролями разметчика и верификатора.

**Основные возможности:**
- Интерактивный waveform-редактор
- Создание, редактирование и удаление сегментов
- Автосохранение изменений
- Работа с ролями (Разметчик / Верификатор)
- Чек-лист перед отправкой на проверку
- Экспорт результата в JSON

---

## Как запустить проект

### Вариант 1: Через Docker Compose (рекомендуется)

git clone https://github.com/NotWeisai/GeckoNext.git
cd GeckoNext

docker compose up --build 


**После запуска:**

Backend: http://localhost:8000/docs
Frontend: откройте файл frontend/index.html в браузере (или через Live Server)

### Вариант 2: Ручной запуск (для разработки)

**База данных:** 
docker compose up db

**Backend:** 
cd backend
#Активируй окружение
venv\Scripts\activate    # Windows
#или source venv/bin/activate  # Linux/Mac

uvicorn app.main:app --reload --port 8000

**Frontend:**
Откройте index.html в браузере или через Live Server (VS Code).

### Стек технологий

**Frontend:**
HTML5 + Tailwind CSS
Vanilla JavaScript
WaveSurfer.js v7 + Regions plugin

**Backend:**
FastAPI (Python)
Uvicorn
SQLAlchemy + PostgreSQL

**База данных:**
PostgreSQL 16 (в Docker)

**Хранение:**
Метаданные — PostgreSQL
Аудиофайлы — папка uploads/
Кэш — localStorage (браузер)

## Реализованный функционал (полный)

- Авторизация и регистрация
- Загрузка аудио + JSON предразметки
- Интерактивный waveform с зумом
- Создание, редактирование, удаление сегментов
- Редактирование текста с автосохранением
- Play / Play Segment + New Segment
- Чек-лист перед отправкой
- Workflow: Разметчик → Верификатор (принять / вернуть)
- Экспорт JSON
- Журнал действий


## План развития

- Поддержка видео + синхронизация
- Терминологический модуль
- AI-подсказки по сегментам
- Горячие клавиши
- Больше ролей
- Версионирование разметки
