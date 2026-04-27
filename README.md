# Guitar LED Trainer

Обучение игре на гитаре с LED-подсветкой на грифе.

## Технологии

- Flutter (Dart) - мобильное приложение
- SQLite - локальная база данных
- 1С:Предприятие - бэкенд и API
- Python + PyQt5 - GUI для управления

## Скрипты

- music_gui_working.py - GUI программа
- add_song.sh - добавление произведений
- quick_add.sh - быстрое добавление

## Быстрый старт

1. Создание базы:
   sqlite3 guitar.db < init_db.sql

2. Запуск GUI:
   python3 music_gui_working.py

## Структура БД

Произведения -> Аппликатуры -> Квадраты -> Аккорды

## Автор

sheiker12
