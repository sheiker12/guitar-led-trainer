#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import sqlite3
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

DB_NAME = "idinaxui.db"

def init_db():
    """Создает базу данных если её нет и добавляет примеры"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица Произведения
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Произведения (
            id TEXT PRIMARY KEY,
            название TEXT,
            автор TEXT,
            bpm INTEGER
        )
    """)
    
    # Таблица Аккорды
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Аккорды (
            id TEXT PRIMARY KEY,
            название TEXT,
            аппликатура TEXT
        )
    """)
    
    # Таблица Квадраты
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Квадраты (
            id TEXT PRIMARY KEY,
            название TEXT,
            аккорд1_id TEXT,
            аккорд2_id TEXT,
            аккорд3_id TEXT,
            аккорд4_id TEXT
        )
    """)
    
    # Таблица Аппликатуры
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Аппликатуры (
            id TEXT PRIMARY KEY,
            произведение_id TEXT,
            квадрат1_id TEXT,
            квадрат2_id TEXT,
            квадрат3_id TEXT,
            квадрат4_id TEXT,
            квадрат5_id TEXT,
            квадрат6_id TEXT,
            квадрат7_id TEXT,
            квадрат8_id TEXT
        )
    """)
    
    # Проверяем есть ли данные, если нет - добавляем примеры
    cursor.execute("SELECT COUNT(*) FROM Произведения")
    if cursor.fetchone()[0] == 0:
        # Примеры произведений
        cursor.execute("INSERT INTO Произведения VALUES ('p1', 'Полонез Огинского', 'Огинский', 120)")
        cursor.execute("INSERT INTO Произведения VALUES ('p2', 'Вальс', 'Шопен', 140)")
        cursor.execute("INSERT INTO Произведения VALUES ('p3', 'В траве сидел кузнечик', 'Народная', 100)")
        
        # Примеры аккордов
        cursor.execute("INSERT INTO Аккорды VALUES ('am', 'Am', 'x02210')")
        cursor.execute("INSERT INTO Аккорды VALUES ('dm', 'Dm', 'xx0231')")
        cursor.execute("INSERT INTO Аккорды VALUES ('e7', 'E7', '020100')")
        cursor.execute("INSERT INTO Аккорды VALUES ('c', 'C', 'x32010')")
        cursor.execute("INSERT INTO Аккорды VALUES ('g', 'G', '320003')")
        
        # Примеры квадратов
        cursor.execute("INSERT INTO Квадраты VALUES ('intro1', 'Интро', 'am', NULL, NULL, NULL)")
        cursor.execute("INSERT INTO Квадраты VALUES ('verse1', 'Куплет', 'am', 'dm', 'e7', NULL)")
        cursor.execute("INSERT INTO Квадраты VALUES ('chorus1', 'Припев', 'c', 'g', 'am', NULL)")
        cursor.execute("INSERT INTO Квадраты VALUES ('outro1', 'Аутро', 'am', NULL, NULL, NULL)")
    
    conn.commit()
    conn.close()

class MusicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎸 LED-накладка - Управление базой")
        self.setGeometry(100, 100, 1000, 700)
        
        # Создаем базу если нет
        init_db()
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Вкладки
        self.setup_pieces_tab()
        self.setup_chords_tab()
        self.setup_squares_tab()
        self.setup_fingering_tab()
        self.setup_led_tab()
        
        # Статусбар
        self.statusBar().showMessage("Готов")
        
        # Обновляем данные
        self.refresh_all()
    
    # =============================================
    # ВКЛАДКА "ПРОИЗВЕДЕНИЯ"
    # =============================================
    def setup_pieces_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "📀 Произведения")
        layout = QVBoxLayout(tab)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_add_piece = QPushButton("➕ Добавить")
        self.btn_edit_piece = QPushButton("✏️ Редактировать")
        self.btn_del_piece = QPushButton("❌ Удалить")
        self.btn_refresh_pieces = QPushButton("🔄 Обновить")
        
        self.btn_add_piece.clicked.connect(self.add_piece)
        self.btn_edit_piece.clicked.connect(self.edit_piece)
        self.btn_del_piece.clicked.connect(self.delete_piece)
        self.btn_refresh_pieces.clicked.connect(self.refresh_pieces)
        
        btn_layout.addWidget(self.btn_add_piece)
        btn_layout.addWidget(self.btn_edit_piece)
        btn_layout.addWidget(self.btn_del_piece)
        btn_layout.addWidget(self.btn_refresh_pieces)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Таблица
        self.pieces_table = QTableWidget()
        self.pieces_table.setColumnCount(4)
        self.pieces_table.setHorizontalHeaderLabels(["ID", "Название", "Автор", "BPM"])
        self.pieces_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pieces_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pieces_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.pieces_table)
    
    def refresh_pieces(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, название, автор, bpm FROM Произведения ORDER BY название")
        data = cursor.fetchall()
        conn.close()
        
        self.pieces_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.pieces_table.setItem(i, j, QTableWidgetItem(str(val) if val else ""))
        
        self.statusBar().showMessage(f"Загружено {len(data)} произведений")
        self.refresh_piece_combos()
    
    def refresh_piece_combos(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, название FROM Произведения ORDER BY название")
        pieces = cursor.fetchall()
        conn.close()
        
        self.piece_ids = [p[0] for p in pieces]
        piece_names = [f"{p[0]} - {p[1]}" for p in pieces]
        
        if hasattr(self, 'piece_combo'):
            self.piece_combo.blockSignals(True)
            self.piece_combo.clear()
            self.piece_combo.addItems(piece_names)
            self.piece_combo.blockSignals(False)
        
        if hasattr(self, 'led_piece_combo'):
            self.led_piece_combo.blockSignals(True)
            self.led_piece_combo.clear()
            self.led_piece_combo.addItems(piece_names)
            self.led_piece_combo.blockSignals(False)
    
    def add_piece(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить произведение")
        dialog.setModal(True)
        layout = QFormLayout(dialog)
        
        id_edit = QLineEdit()
        name_edit = QLineEdit()
        author_edit = QLineEdit()
        bpm_edit = QLineEdit("120")
        
        layout.addRow("ID (например p4):", id_edit)
        layout.addRow("Название:", name_edit)
        layout.addRow("Автор:", author_edit)
        layout.addRow("BPM:", bpm_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(buttons)
        
        def save():
            piece_id = id_edit.text().strip()
            name = name_edit.text().strip()
            if not piece_id or not name:
                QMessageBox.warning(self, "Ошибка", "ID и Название обязательны!")
                return
            
            bpm = 120
            if bpm_edit.text().strip().isdigit():
                bpm = int(bpm_edit.text().strip())
            
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Произведения (id, название, автор, bpm) VALUES (?, ?, ?, ?)",
                    (piece_id, name, author_edit.text().strip(), bpm)
                )
                conn.commit()
                conn.close()
                self.refresh_pieces()
                dialog.accept()
                QMessageBox.information(self, "Успех", f"Произведение '{name}' добавлено!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
        
        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    
    def edit_piece(self):
        selected = self.pieces_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите произведение!")
            return
        
        piece_id = self.pieces_table.item(selected, 0).text()
        old_name = self.pieces_table.item(selected, 1).text()
        old_author = self.pieces_table.item(selected, 2).text()
        old_bpm = self.pieces_table.item(selected, 3).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать произведение")
        dialog.setModal(True)
        layout = QFormLayout(dialog)
        
        id_label = QLabel(piece_id)
        name_edit = QLineEdit(old_name)
        author_edit = QLineEdit(old_author)
        bpm_edit = QLineEdit(old_bpm)
        
        layout.addRow("ID:", id_label)
        layout.addRow("Название:", name_edit)
        layout.addRow("Автор:", author_edit)
        layout.addRow("BPM:", bpm_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(buttons)
        
        def save():
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            bpm = 120
            if bpm_edit.text().strip().isdigit():
                bpm = int(bpm_edit.text().strip())
            cursor.execute(
                "UPDATE Произведения SET название=?, автор=?, bpm=? WHERE id=?",
                (name_edit.text().strip(), author_edit.text().strip(), bpm, piece_id)
            )
            conn.commit()
            conn.close()
            self.refresh_pieces()
            dialog.accept()
            QMessageBox.information(self, "Успех", "Произведение обновлено!")
        
        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    
    def delete_piece(self):
        selected = self.pieces_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите произведение!")
            return
        
        piece_id = self.pieces_table.item(selected, 0).text()
        name = self.pieces_table.item(selected, 1).text()
        
        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить '{name}' и ВСЁ связанное?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Произведения WHERE id=?", (piece_id,))
            cursor.execute("DELETE FROM Аппликатуры WHERE произведение_id=?", (piece_id,))
            conn.commit()
            conn.close()
            self.refresh_all()
            QMessageBox.information(self, "Успех", "Произведение удалено!")
    
    # =============================================
    # ВКЛАДКА "АККОРДЫ"
    # =============================================
    def setup_chords_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "🎵 Аккорды")
        layout = QVBoxLayout(tab)
        
        btn_layout = QHBoxLayout()
        self.btn_add_chord = QPushButton("➕ Добавить")
        self.btn_edit_chord = QPushButton("✏️ Редактировать")
        self.btn_del_chord = QPushButton("❌ Удалить")
        self.btn_refresh_chords = QPushButton("🔄 Обновить")
        
        self.btn_add_chord.clicked.connect(self.add_chord)
        self.btn_edit_chord.clicked.connect(self.edit_chord)
        self.btn_del_chord.clicked.connect(self.delete_chord)
        self.btn_refresh_chords.clicked.connect(self.refresh_chords)
        
        btn_layout.addWidget(self.btn_add_chord)
        btn_layout.addWidget(self.btn_edit_chord)
        btn_layout.addWidget(self.btn_del_chord)
        btn_layout.addWidget(self.btn_refresh_chords)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.chords_table = QTableWidget()
        self.chords_table.setColumnCount(3)
        self.chords_table.setHorizontalHeaderLabels(["ID", "Название", "Аппликатура"])
        self.chords_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.chords_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.chords_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.chords_table)
    
    def refresh_chords(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, название, аппликатура FROM Аккорды ORDER BY название")
        data = cursor.fetchall()
        conn.close()
        
        self.chords_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.chords_table.setItem(i, j, QTableWidgetItem(str(val) if val else ""))
        
        self.statusBar().showMessage(f"Загружено {len(data)} аккордов")
        self.refresh_squares()
    
    def add_chord(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить аккорд")
        dialog.setModal(True)
        layout = QFormLayout(dialog)
        
        id_edit = QLineEdit()
        name_edit = QLineEdit()
        fingering_edit = QLineEdit()
        
        layout.addRow("ID (am, dm, e7):", id_edit)
        layout.addRow("Название (Am, Dm, E7):", name_edit)
        layout.addRow("Аппликатура (x02210):", fingering_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(buttons)
        
        def save():
            chord_id = id_edit.text().strip()
            name = name_edit.text().strip()
            if not chord_id or not name:
                QMessageBox.warning(self, "Ошибка", "ID и Название обязательны!")
                return
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO Аккорды (id, название, аппликатура) VALUES (?, ?, ?)",
                (chord_id, name, fingering_edit.text().strip())
            )
            conn.commit()
            conn.close()
            self.refresh_chords()
            dialog.accept()
            QMessageBox.information(self, "Успех", f"Аккорд '{name}' добавлен!")
        
        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    
    def edit_chord(self):
        selected = self.chords_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите аккорд!")
            return
        
        chord_id = self.chords_table.item(selected, 0).text()
        old_name = self.chords_table.item(selected, 1).text()
        old_fingering = self.chords_table.item(selected, 2).text() if self.chords_table.item(selected, 2) else ""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать аккорд")
        dialog.setModal(True)
        layout = QFormLayout(dialog)
        
        id_label = QLabel(chord_id)
        name_edit = QLineEdit(old_name)
        fingering_edit = QLineEdit(old_fingering)
        
        layout.addRow("ID:", id_label)
        layout.addRow("Название:", name_edit)
        layout.addRow("Аппликатура:", fingering_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(buttons)
        
        def save():
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Аккорды SET название=?, аппликатура=? WHERE id=?",
                (name_edit.text().strip(), fingering_edit.text().strip(), chord_id)
            )
            conn.commit()
            conn.close()
            self.refresh_chords()
            dialog.accept()
            QMessageBox.information(self, "Успех", "Аккорд обновлён!")
        
        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    
    def delete_chord(self):
        selected = self.chords_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите аккорд!")
            return
        
        chord_id = self.chords_table.item(selected, 0).text()
        name = self.chords_table.item(selected, 1).text()
        
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить аккорд '{name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Аккорды WHERE id=?", (chord_id,))
            conn.commit()
            conn.close()
            self.refresh_chords()
            QMessageBox.information(self, "Успех", "Аккорд удалён!")
    
    # =============================================
    # ВКЛАДКА "КВАДРАТЫ"
    # =============================================
    def setup_squares_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "📦 Квадраты")
        layout = QVBoxLayout(tab)
        
        btn_layout = QHBoxLayout()
        self.btn_add_square = QPushButton("➕ Добавить")
        self.btn_edit_square = QPushButton("✏️ Редактировать")
        self.btn_del_square = QPushButton("❌ Удалить")
        self.btn_refresh_squares = QPushButton("🔄 Обновить")
        
        self.btn_add_square.clicked.connect(self.add_square)
        self.btn_edit_square.clicked.connect(self.edit_square)
        self.btn_del_square.clicked.connect(self.delete_square)
        self.btn_refresh_squares.clicked.connect(self.refresh_squares)
        
        btn_layout.addWidget(self.btn_add_square)
        btn_layout.addWidget(self.btn_edit_square)
        btn_layout.addWidget(self.btn_del_square)
        btn_layout.addWidget(self.btn_refresh_squares)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.squares_table = QTableWidget()
        self.squares_table.setColumnCount(6)
        self.squares_table.setHorizontalHeaderLabels(["ID", "Название", "Аккорд1", "Аккорд2", "Аккорд3", "Аккорд4"])
        self.squares_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.squares_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.squares_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.squares_table)
    
    def refresh_squares(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, название, 
                   COALESCE(аккорд1_id, '-'), COALESCE(аккорд2_id, '-'), 
                   COALESCE(аккорд3_id, '-'), COALESCE(аккорд4_id, '-') 
            FROM Квадраты ORDER BY название
        """)
        data = cursor.fetchall()
        conn.close()
        
        self.squares_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.squares_table.setItem(i, j, QTableWidgetItem(str(val) if val else "-"))
        
        self.statusBar().showMessage(f"Загружено {len(data)} квадратов")
        self.refresh_squares_list()
    
    def refresh_squares_list(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, название FROM Квадраты ORDER BY название")
        squares = cursor.fetchall()
        conn.close()
        
        if hasattr(self, 'available_list'):
            self.available_list.clear()
            self.square_ids = [s[0] for s in squares]
            for s in squares:
                self.available_list.addItem(f"{s[0]} - {s[1]}")
    
    def add_square(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить квадрат")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        id_edit = QLineEdit()
        name_edit = QLineEdit()
        form_layout.addRow("ID квадрата:", id_edit)
        form_layout.addRow("Название:", name_edit)
        layout.addLayout(form_layout)
        
        # Получаем аккорды
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, название FROM Аккорды ORDER BY название")
        chords = cursor.fetchall()
        conn.close()
        
        chord_combos = []
        chord_layout = QFormLayout()
        chord_layout.addRow("Аккорды (до 4-х):")
        
        for i in range(4):
            combo = QComboBox()
            combo.addItem("(нет)")
            for c in chords:
                combo.addItem(f"{c[0]} - {c[1]}")
            chord_combos.append(combo)
            chord_layout.addRow(f"  Аккорд {i+1}:", combo)
        
        layout.addLayout(chord_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        
        def save():
            square_id = id_edit.text().strip()
            name = name_edit.text().strip()
            if not square_id or not name:
                QMessageBox.warning(self, "Ошибка", "ID и Название обязательны!")
                return
            
            selected = []
            for combo in chord_combos:
                val = combo.currentText()
                if val != "(нет)":
                    selected.append(val.split(" - ")[0])
                else:
                    selected.append(None)
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Квадраты (id, название, аккорд1_id, аккорд2_id, аккорд3_id, аккорд4_id) VALUES (?, ?, ?, ?, ?, ?)",
                (square_id, name, selected[0], selected[1], selected[2], selected[3])
            )
            conn.commit()
            conn.close()
            self.refresh_squares()
            dialog.accept()
            QMessageBox.information(self, "Успех", f"Квадрат '{name}' добавлен!")
        
        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    
    def edit_square(self):
        selected = self.squares_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите квадрат!")
            return
        
        square_id = self.squares_table.item(selected, 0).text()
        old_name = self.squares_table.item(selected, 1).text()
        old_chords = [
            self.squares_table.item(selected, 2).text(),
            self.squares_table.item(selected, 3).text(),
            self.squares_table.item(selected, 4).text(),
            self.squares_table.item(selected, 5).text()
        ]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать квадрат")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        id_label = QLabel(square_id)
        name_edit = QLineEdit(old_name)
        form_layout.addRow("ID:", id_label)
        form_layout.addRow("Название:", name_edit)
        layout.addLayout(form_layout)
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, название FROM Аккорды ORDER BY название")
        chords = cursor.fetchall()
        conn.close()
        
        chord_combos = []
        chord_layout = QFormLayout()
        chord_layout.addRow("Аккорды:")
        
        for i in range(4):
            combo = QComboBox()
            combo.addItem("(нет)")
            for c in chords:
                item_text = f"{c[0]} - {c[1]}"
                combo.addItem(item_text)
                if old_chords[i] != "-" and old_chords[i] == c[0]:
                    combo.setCurrentText(item_text)
            chord_combos.append(combo)
            chord_layout.addRow(f"  Аккорд {i+1}:", combo)
        
        layout.addLayout(chord_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        
        def save():
            new_name = name_edit.text().strip()
            selected_chords = []
            for combo in chord_combos:
                val = combo.currentText()
                if val != "(нет)":
                    selected_chords.append(val.split(" - ")[0])
                else:
                    selected_chords.append(None)
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Квадраты SET название=?, аккорд1_id=?, аккорд2_id=?, аккорд3_id=?, аккорд4_id=? WHERE id=?",
                (new_name, selected_chords[0], selected_chords[1], selected_chords[2], selected_chords[3], square_id)
            )
            conn.commit()
            conn.close()
            self.refresh_squares()
            dialog.accept()
            QMessageBox.information(self, "Успех", "Квадрат обновлён!")
        
        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    
    def delete_square(self):
        selected = self.squares_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Внимание", "Выберите квадрат!")
            return
        
        square_id = self.squares_table.item(selected, 0).text()
        name = self.squares_table.item(selected, 1).text()
        
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить квадрат '{name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Квадраты WHERE id=?", (square_id,))
            conn.commit()
            conn.close()
            self.refresh_squares()
            QMessageBox.information(self, "Успех", "Квадрат удалён!")
    
    # =============================================
    # ВКЛАДКА "АППЛИКАТУРЫ"
    # =============================================
    def setup_fingering_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "🔗 Порядок квадратов")
        layout = QVBoxLayout(tab)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Произведение:"))
        self.piece_combo = QComboBox()
        self.piece_combo.currentIndexChanged.connect(self.on_fingering_piece_change)
        top_layout.addWidget(self.piece_combo)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        layout.addWidget(QLabel("Доступные квадраты:"))
        self.available_list = QListWidget()
        self.available_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.available_list)
        
        btn_layout = QHBoxLayout()
        self.btn_add_to_order = QPushButton("→ Добавить в порядок →")
        self.btn_remove_from_order = QPushButton("← Убрать из порядка ←")
        self.btn_move_up = QPushButton("⬆ Вверх")
        self.btn_move_down = QPushButton("⬇ Вниз")
        self.btn_save_fingering = QPushButton("💾 Сохранить")
        
        self.btn_add_to_order.clicked.connect(self.add_to_order)
        self.btn_remove_from_order.clicked.connect(self.remove_from_order)
        self.btn_move_up.clicked.connect(self.move_up)
        self.btn_move_down.clicked.connect(self.move_down)
        self.btn_save_fingering.clicked.connect(self.save_fingering)
        
        btn_layout.addWidget(self.btn_add_to_order)
        btn_layout.addWidget(self.btn_remove_from_order)
        btn_layout.addWidget(self.btn_move_up)
        btn_layout.addWidget(self.btn_move_down)
        btn_layout.addWidget(self.btn_save_fingering)
        layout.addLayout(btn_layout)
        
        layout.addWidget(QLabel("Порядок квадратов (сверху вниз):"))
        self.order_list = QListWidget()
        layout.addWidget(self.order_list)
    
    def on_fingering_piece_change(self, index):
        if index >= 0 and hasattr(self, 'piece_ids') and index < len(self.piece_ids):
            self.refresh_fingering_for_piece(self.piece_ids[index])
    
    def refresh_fingering_for_piece(self, piece_id):
        self.order_list.clear()
        if not piece_id:
            return
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Аппликатуры WHERE произведение_id=?", (piece_id,))
        fingering = cursor.fetchone()
        
        if fingering:
            for i in range(1, 9):
                sq = fingering[i+1]
                if sq:
                    cursor.execute("SELECT название FROM Квадраты WHERE id=?", (sq,))
                    sq_name = cursor.fetchone()
                    if sq_name:
                        self.order_list.addItem(f"{sq} - {sq_name[0]}")
        conn.close()
    
    def add_to_order(self):
        for item in self.available_list.selectedItems():
            self.order_list.addItem(item.text())
    
    def remove_from_order(self):
        for item in self.order_list.selectedItems():
            self.order_list.takeItem(self.order_list.row(item))
    
    def move_up(self):
        row = self.order_list.currentRow()
        if row > 0:
            item = self.order_list.takeItem(row)
            self.order_list.insertItem(row - 1, item)
            self.order_list.setCurrentRow(row - 1)
    
    def move_down(self):
        row = self.order_list.currentRow()
        if row < self.order_list.count() - 1:
            item = self.order_list.takeItem(row)
            self.order_list.insertItem(row + 1, item)
            self.order_list.setCurrentRow(row + 1)
    
    def save_fingering(self):
        if self.piece_combo.currentIndex() < 0 or not hasattr(self, 'piece_ids'):
            QMessageBox.warning(self, "Внимание", "Выберите произведение!")
            return
        
        piece_id = self.piece_ids[self.piece_combo.currentIndex()]
        
        squares = []
        for i in range(self.order_list.count()):
            text = self.order_list.item(i).text()
            sq_id = text.split(" - ")[0]
            squares.append(sq_id)
        
        while len(squares) < 8:
            squares.append(None)
        
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
             squares[0], squares[1], squares[2], squares[3],
             squares[4], squares[5], squares[6], squares[7])
        )
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, "Успех", "Порядок квадратов сохранён!")
        self.refresh_fingering_for_piece(piece_id)
    
    # =============================================
    # ВКЛАДКА "LED"
    # =============================================
    def setup_led_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "💡 LED-раскладка")
        layout = QVBoxLayout(tab)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Произведение:"))
        self.led_piece_combo = QComboBox()
        self.led_piece_combo.currentIndexChanged.connect(self.show_led_preview)
        top_layout.addWidget(self.led_piece_combo)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        self.led_text = QTextEdit()
        self.led_text.setReadOnly(True)
        self.led_text.setFont(QFont("Monospace", 10))
        layout.addWidget(self.led_text)
    
    def show_led_preview(self):
        index = self.led_piece_combo.currentIndex()
        if index < 0 or not hasattr(self, 'piece_ids') or index >= len(self.piece_ids):
            self.led_text.setText("⚠️ Нет произведений в базе.\n\nДобавьте произведение на вкладке 'Произведения'.")
            return
        
        piece_id = self.piece_ids[index]
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT название, bpm FROM Произведения WHERE id=?", (piece_id,))
        piece = cursor.fetchone()
        if not piece:
            self.led_text.setText("⚠️ Произведение не найдено!")
            conn.close()
            return
        
        piece_name, bpm = piece
        beat_ms = 60000 / bpm if bpm and bpm > 0 else 500
        
        cursor.execute("SELECT * FROM Аппликатуры WHERE произведение_id=?", (piece_id,))
        fingering = cursor.fetchone()
        
        if not fingering:
            self.led_text.setText(f"⚠️ Для произведения '{piece_name}' не задан порядок квадратов!\n\nСначала настройте Аппликатуру на вкладке 'Порядок квадратов'.")
            conn.close()
            return
        
        text = f"🎵 {piece_name}  |  BPM: {bpm}  |  1 удар = {beat_ms:.0f} мс\n"
        text += "=" * 60 + "\n\n"
        
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
            
            text += f"📦 {square_name}:\n"
            
            for j, chord_id in enumerate(chords):
                if not chord_id:
                    continue
                
                cursor.execute("SELECT название, аппликатура FROM Аккорды WHERE id=?", (chord_id,))
                chord = cursor.fetchone()
                if chord:
                    chord_name = chord[0]
                    fingering_str = chord[1] if chord[1] else "???"
                    duration_beats = 4
                    duration_ms = duration_beats * beat_ms
                    text += f"      Аккорд {j+1}: {chord_name} ({fingering_str}) - {duration_beats} ударов = {duration_ms:.0f} мс\n"
                    total_time += duration_ms
            
            text += "\n"
        
        text += "=" * 60 + "\n"
        text += f"⏱️ Общая длительность: {total_time/1000:.1f} секунд\n"
        
        self.led_text.setText(text)
        conn.close()
    
    def refresh_all(self):
        self.refresh_pieces()
        self.refresh_chords()
        self.refresh_squares()
        self.refresh_squares_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicApp()
    window.show()
    sys.exit(app.exec_())
