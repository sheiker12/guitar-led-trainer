#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys

DB_NAME = "idinaxui.db"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header(title):
    clear_screen()
    print("=" * 60)
    print(f"     🎸  {title}  🎸")
    print("=" * 60)
    print()

def wait_enter():
    input("\nНажми Enter для продолжения...")

# =============================================
# РАБОТА С ПРОИЗВЕДЕНИЯМИ
# =============================================
def list_pieces():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, название, автор, bpm FROM Произведения ORDER BY название")
    pieces = cursor.fetchall()
    conn.close()
    
    print_header("СПИСОК ПРОИЗВЕДЕНИЙ")
    if not pieces:
        print("  📭 Нет произведений")
    else:
        print(f"  {'ID':<10} {'Название':<30} {'Автор':<20} {'BPM':<5}")
        print("  " + "-" * 70)
        for p in pieces:
            print(f"  {p[0]:<10} {p[1]:<30} {p[2] if p[2] else '-':<20} {p[3] if p[3] else '-':<5}")
    print()
    return pieces

def add_piece():
    print_header("ДОБАВЛЕНИЕ ПРОИЗВЕДЕНИЯ")
    
    piece_id = input("  ID произведения (например p4): ").strip()
    if not piece_id:
        print("  ❌ ID обязателен!")
        wait_enter()
        return
    
    name = input("  Название: ").strip()
    if not name:
        print("  ❌ Название обязательно!")
        wait_enter()
        return
    
    author = input("  Автор: ").strip()
    
    bpm_input = input("  BPM (темп, Enter = 120): ").strip()
    bpm = int(bpm_input) if bpm_input.isdigit() else 120
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Произведения (id, название, автор, bpm) VALUES (?, ?, ?, ?)",
            (piece_id, name, author, bpm)
        )
        conn.commit()
        conn.close()
        print(f"\n  ✅ Произведение '{name}' добавлено!")
    except Exception as e:
        print(f"\n  ❌ Ошибка: {e}")
    
    wait_enter()

def edit_piece():
    pieces = list_pieces()
    if not pieces:
        wait_enter()
        return
    
    piece_id = input("\n  Введите ID произведения для редактирования: ").strip()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, название, автор, bpm FROM Произведения WHERE id=?", (piece_id,))
    piece = cursor.fetchone()
    
    if not piece:
        print("  ❌ Произведение не найдено!")
        conn.close()
        wait_enter()
        return
    
    print(f"\n  Текущие данные: {piece[1]} | {piece[2]} | {piece[3]} BPM")
    print("  (Enter - оставить без изменений)")
    
    new_name = input(f"  Новое название [{piece[1]}]: ").strip()
    new_author = input(f"  Новый автор [{piece[2] if piece[2] else '-'}]: ").strip()
    new_bpm = input(f"  Новый BPM [{piece[3]}]: ").strip()
    
    new_name = new_name if new_name else piece[1]
    new_author = new_author if new_author else piece[2]
    new_bpm = int(new_bpm) if new_bpm.isdigit() else piece[3]
    
    cursor.execute(
        "UPDATE Произведения SET название=?, автор=?, bpm=? WHERE id=?",
        (new_name, new_author, new_bpm, piece_id)
    )
    conn.commit()
    conn.close()
    
    print(f"\n  ✅ Произведение обновлено!")
    wait_enter()

def delete_piece():
    pieces = list_pieces()
    if not pieces:
        wait_enter()
        return
    
    piece_id = input("\n  Введите ID произведения для удаления: ").strip()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT название FROM Произведения WHERE id=?", (piece_id,))
    piece = cursor.fetchone()
    
    if not piece:
        print("  ❌ Произведение не найдено!")
        conn.close()
        wait_enter()
        return
    
    confirm = input(f"\n  Удалить '{piece[0]}'? (y/n): ").strip().lower()
    if confirm == 'y':
        cursor.execute("DELETE FROM Произведения WHERE id=?", (piece_id,))
        conn.commit()
        print(f"\n  ✅ Произведение удалено!")
    else:
        print("\n  Отменено")
    
    conn.close()
    wait_enter()

# =============================================
# РАБОТА С АККОРДАМИ
# =============================================
def list_chords():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, название, аппликатура FROM Аккорды ORDER BY название")
    chords = cursor.fetchall()
    conn.close()
    
    print_header("СПИСОК АККОРДОВ")
    if not chords:
        print("  📭 Нет аккордов")
    else:
        print(f"  {'ID':<8} {'Название':<10} {'Аппликатура (x02210)':<20}")
        print("  " + "-" * 45)
        for c in chords:
            fing = c[2] if c[2] else '-'
            print(f"  {c[0]:<8} {c[1]:<10} {fing:<20}")
    print()

def add_chord():
    print_header("ДОБАВЛЕНИЕ АККОРДА")
    
    chord_id = input("  ID аккорда (например am, dm, e7): ").strip()
    if not chord_id:
        print("  ❌ ID обязателен!")
        wait_enter()
        return
    
    name = input("  Название (Am, Dm, E7): ").strip()
    if not name:
        print("  ❌ Название обязательно!")
        wait_enter()
        return
    
    fingering = input("  Аппликатура (6 струн, например x02210): ").strip()
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO Аккорды (id, название, аппликатура) VALUES (?, ?, ?)",
            (chord_id, name, fingering)
        )
        conn.commit()
        conn.close()
        print(f"\n  ✅ Аккорд '{name}' добавлен!")
    except Exception as e:
        print(f"\n  ❌ Ошибка: {e}")
    
    wait_enter()

def delete_chord():
    list_chords()
    
    chord_id = input("\n  Введите ID аккорда для удаления: ").strip()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT название FROM Аккорды WHERE id=?", (chord_id,))
    chord = cursor.fetchone()
    
    if not chord:
        print("  ❌ Аккорд не найден!")
        conn.close()
        wait_enter()
        return
    
    confirm = input(f"\n  Удалить аккорд '{chord[0]}'? (y/n): ").strip().lower()
    if confirm == 'y':
        cursor.execute("DELETE FROM Аккорды WHERE id=?", (chord_id,))
        conn.commit()
        print(f"\n  ✅ Аккорд удалён!")
    else:
        print("\n  Отменено")
    
    conn.close()
    wait_enter()

# =============================================
# РАБОТА С КВАДРАТАМИ
# =============================================
def list_squares():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, название, 
               COALESCE(аккорд1_id, '-'), COALESCE(аккорд2_id, '-'), 
               COALESCE(аккорд3_id, '-'), COALESCE(аккорд4_id, '-') 
        FROM Квадраты ORDER BY название
    """)
    squares = cursor.fetchall()
    conn.close()
    
    print_header("СПИСОК КВАДРАТОВ")
    if not squares:
        print("  📭 Нет квадратов")
    else:
        print(f"  {'ID':<12} {'Название':<15} {'Аккорды':<30}")
        print("  " + "-" * 60)
        for s in squares:
            chords = [s[2], s[3], s[4], s[5]]
            chords_str = " → ".join([c for c in chords if c != '-'])
            print(f"  {s[0]:<12} {s[1]:<15} {chords_str:<30}")
    print()

def add_square():
    print_header("ДОБАВЛЕНИЕ КВАДРАТА")
    
    # Получаем список аккордов
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, название FROM Аккорды ORDER BY название")
    chords = cursor.fetchall()
    conn.close()
    
    if not chords:
        print("  ⚠️ Сначала добавьте аккорды!")
        wait_enter()
        return
    
    square_id = input("  ID квадрата (например verse3): ").strip()
    if not square_id:
        print("  ❌ ID обязателен!")
        wait_enter()
        return
    
    name = input("  Название (Интро, Куплет, Припев...): ").strip()
    if not name:
        print("  ❌ Название обязательно!")
        wait_enter()
        return
    
    print("\n  Доступные аккорды:")
    for i, c in enumerate(chords):
        print(f"    {i+1}. {c[0]} - {c[1]}")
    
    selected = []
    for i in range(1, 5):
        choice = input(f"  Аккорд {i} (номер или Enter если нет): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(chords):
            selected.append(chords[int(choice)-1][0])
        else:
            selected.append(None)
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO Квадраты 
               (id, название, аккорд1_id, аккорд2_id, аккорд3_id, аккорд4_id) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (square_id, name, selected[0], selected[1], selected[2], selected[3])
        )
        conn.commit()
        conn.close()
        print(f"\n  ✅ Квадрат '{name}' добавлен!")
    except Exception as e:
        print(f"\n  ❌ Ошибка: {e}")
    
    wait_enter()

def delete_square():
    list_squares()
    
    square_id = input("\n  Введите ID квадрата для удаления: ").strip()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT название FROM Квадраты WHERE id=?", (square_id,))
    square = cursor.fetchone()
    
    if not square:
        print("  ❌ Квадрат не найден!")
        conn.close()
        wait_enter()
        return
    
    confirm = input(f"\n  Удалить квадрат '{square[0]}'? (y/n): ").strip().lower()
    if confirm == 'y':
        cursor.execute("DELETE FROM Квадраты WHERE id=?", (square_id,))
        conn.commit()
        print(f"\n  ✅ Квадрат удалён!")
    else:
        print("\n  Отменено")
    
    conn.close()
    wait_enter()

# =============================================
# АППЛИКАТУРЫ (порядок квадратов)
# =============================================
def manage_fingering():
    print_header("АППЛИКАТУРЫ - ПОРЯДОК КВАДРАТОВ")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, название FROM Произведения ORDER BY название")
    pieces = cursor.fetchall()
    conn.close()
    
    if not pieces:
        print("  📭 Нет произведений")
        wait_enter()
        return
    
    print("  Выберите произведение:")
    for i, p in enumerate(pieces):
        print(f"    {i+1}. {p[0]} - {p[1]}")
    
    choice = input("\n  Введите номер: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(pieces)):
        print("  ❌ Неверный выбор!")
        wait_enter()
        return
    
    piece_id = pieces[int(choice)-1][0]
    piece_name = pieces[int(choice)-1][1]
    
    # Получаем все квадраты
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, название FROM Квадраты ORDER BY название")
    all_squares = cursor.fetchall()
    
    # Получаем текущую аппликатуру
    cursor.execute("SELECT * FROM Аппликатуры WHERE произведение_id=?", (piece_id,))
    fingering = cursor.fetchone()
    conn.close()
    
    current_order = []
    if fingering:
        for i in range(1, 9):
            sq = fingering[i+1]
            if sq:
                for s in all_squares:
                    if s[0] == sq:
                        current_order.append(s)
                        break
    
    print(f"\n  Текущий порядок квадратов для '{piece_name}':")
    if not current_order:
        print("    (пусто)")
    else:
        for i, sq in enumerate(current_order):
            print(f"    {i+1}. {sq[0]} - {sq[1]}")
    
    print("\n  Доступные квадраты:")
    for i, sq in enumerate(all_squares):
        print(f"    {i+1}. {sq[0]} - {sq[1]}")
    
    print("\n  Введите номера квадратов в нужном порядке (через пробел)")
    print("  Например: 1 3 2  (Enter если не хотите менять)")
    
    order_input = input("  Порядок: ").strip()
    
    if order_input:
        indices = order_input.split()
        new_order = []
        for idx in indices:
            if idx.isdigit() and 1 <= int(idx) <= len(all_squares):
                new_order.append(all_squares[int(idx)-1][0])
        
        # Дополняем до 8
        while len(new_order) < 8:
            new_order.append(None)
        
        fingering_id = f"fing_{piece_id}"
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Аппликатуры WHERE произведение_id=?", (piece_id,))
        cursor.execute(
            """INSERT INTO Аппликатуры 
               (id, произведение_id, квадрат1_id, квадрат2_id, квадрат3_id, квадрат4_id,
                квадрат5_id, квадрат6_id, квадрат7_id, квадрат8_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (fingering_id, piece_id, 
             new_order[0], new_order[1], new_order[2], new_order[3],
             new_order[4], new_order[5], new_order[6], new_order[7])
        )
        conn.commit()
        conn.close()
        print(f"\n  ✅ Порядок квадратов сохранён!")
    else:
        print("\n  Изменений не внесено")
    
    wait_enter()

# =============================================
# ПОЛНАЯ КАРТИНА ДЛЯ LED
# =============================================
def show_led_view():
    print_header("LED-РАСКЛАДКА ДЛЯ ПРОИЗВЕДЕНИЯ")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, название FROM Произведения ORDER BY название")
    pieces = cursor.fetchall()
    conn.close()
    
    if not pieces:
        print("  📭 Нет произведений")
        wait_enter()
        return
    
    print("  Выберите произведение:")
    for i, p in enumerate(pieces):
        print(f"    {i+1}. {p[0]} - {p[1]}")
    
    choice = input("\n  Введите номер: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(pieces)):
        print("  ❌ Неверный выбор!")
        wait_enter()
        return
    
    piece_id = pieces[int(choice)-1][0]
    piece_name = pieces[int(choice)-1][1]
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Получаем BPM
    cursor.execute("SELECT bpm FROM Произведения WHERE id=?", (piece_id,))
    bpm_row = cursor.fetchone()
    bpm = bpm_row[0] if bpm_row and bpm_row[0] else 120
    
    # Получаем аппликатуру
    cursor.execute("SELECT * FROM Аппликатуры WHERE произведение_id=?", (piece_id,))
    fingering = cursor.fetchone()
    
    if not fingering:
        print(f"\n  ⚠️ Для произведения '{piece_name}' не задан порядок квадратов!")
        print("  Сначала настройте аппликатуру в меню 5")
        conn.close()
        wait_enter()
        return
    
    print(f"\n  🎵 {piece_name} | BPM: {bpm} | 1 удар = {60000/bpm:.0f} мс")
    print("  " + "=" * 60)
    
    beat_ms = 60000 / bpm
    total_time = 0
    
    for i in range(1, 9):
        sq_id = fingering[i+1]
        if not sq_id:
            continue
        
        cursor.execute("""
            SELECT название, аккорд1_id, аккорд2_id, аккорд3_id, аккорд4_id
            FROM Квадраты WHERE id=?
        """, (sq_id,))
        square = cursor.fetchone()
        
        if not square:
            continue
        
        square_name = square[0]
        chords = [square[1], square[2], square[3], square[4]]
        
        print(f"\n  📦 {square_name}:")
        
        for j, chord_id in enumerate(chords):
            if not chord_id:
                continue
            
            cursor.execute("SELECT название, аппликатура FROM Аккорды WHERE id=?", (chord_id,))
            chord = cursor.fetchone()
            if chord:
                chord_name = chord[0]
                fingering_str = chord[1] if chord[1] else "???"
                
                # Длительность по умолчанию 4 удара
                duration_beats = 4
                duration_ms = duration_beats * beat_ms
                
                print(f"      Аккорд {j+1}: {chord_name} ({fingering_str}) - {duration_beats} ударов = {duration_ms:.0f} мс")
                total_time += duration_ms
    
    print("\n  " + "=" * 60)
    print(f"  ⏱️ Общая длительность: {total_time/1000:.1f} секунд")
    
    conn.close()
    wait_enter()

# =============================================
# ГЛАВНОЕ МЕНЮ
# =============================================
def main():
    while True:
        clear_screen()
        print("=" * 50)
        print("     🎸  LED-НАКЛАДКА - УПРАВЛЕНИЕ БАЗОЙ  🎸")
        print("=" * 50)
        print()
        print("  1. 📀 Произведения (список/добавить/удалить)")
        print("  2. 🎵 Аккорды (список/добавить/удалить)")
        print("  3. 📦 Квадраты (список/добавить/удалить)")
        print("  4. 🔗 Аппликатуры (порядок квадратов)")
        print("  5. 💡 LED-раскладка (посмотреть тайминг)")
        print("  6. 📊 Показать всё")
        print("  0. 🚪 Выход")
        print()
        print("-" * 50)
        
        choice = input("  Выберите действие: ").strip()
        
        if choice == '1':
            submenu_pieces()
        elif choice == '2':
            submenu_chords()
        elif choice == '3':
            submenu_squares()
        elif choice == '4':
            manage_fingering()
        elif choice == '5':
            show_led_view()
        elif choice == '6':
            clear_screen()
            list_pieces()
            print()
            list_chords()
            print()
            list_squares()
            wait_enter()
        elif choice == '0':
            print("\n  До свидания! 🎸\n")
            sys.exit(0)
        else:
            print("  ❌ Неверный выбор!")
            wait_enter()

def submenu_pieces():
    while True:
        clear_screen()
        print_header("ПРОИЗВЕДЕНИЯ")
        print("  1. 📋 Список произведений")
        print("  2. ➕ Добавить произведение")
        print("  3. ✏️ Редактировать произведение")
        print("  4. ❌ Удалить произведение")
        print("  0. 🔙 Назад")
        print()
        
        choice = input("  Выберите действие: ").strip()
        
        if choice == '1':
            list_pieces()
            wait_enter()
        elif choice == '2':
            add_piece()
        elif choice == '3':
            edit_piece()
        elif choice == '4':
            delete_piece()
        elif choice == '0':
            break
        else:
            print("  ❌ Неверный выбор!")
            wait_enter()

def submenu_chords():
    while True:
        clear_screen()
        print_header("АККОРДЫ")
        print("  1. 📋 Список аккордов")
        print("  2. ➕ Добавить аккорд")
        print("  3. ❌ Удалить аккорд")
        print("  0. 🔙 Назад")
        print()
        
        choice = input("  Выберите действие: ").strip()
        
        if choice == '1':
            list_chords()
            wait_enter()
        elif choice == '2':
            add_chord()
        elif choice == '3':
            delete_chord()
        elif choice == '0':
            break
        else:
            print("  ❌ Неверный выбор!")
            wait_enter()

def submenu_squares():
    while True:
        clear_screen()
        print_header("КВАДРАТЫ")
        print("  1. 📋 Список квадратов")
        print("  2. ➕ Добавить квадрат")
        print("  3. ❌ Удалить квадрат")
        print("  0. 🔙 Назад")
        print()
        
        choice = input("  Выберите действие: ").strip()
        
        if choice == '1':
            list_squares()
            wait_enter()
        elif choice == '2':
            add_square()
        elif choice == '3':
            delete_square()
        elif choice == '0':
            break
        else:
            print("  ❌ Неверный выбор!")
            wait_enter()

if __name__ == "__main__":
    main()
