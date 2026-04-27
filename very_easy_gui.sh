#!/bin/bash

DB="idinaxui.db"

# Функция добавления аккорда в справочник
add_chord() {
    local chord_id="$1"
    local chord_name="$2"
    local fingering="$3"
    
    sqlite3 "$DB" "INSERT OR IGNORE INTO Аккорды (id, название, аппликатура) VALUES ('$chord_id', '$chord_name', '$fingering');"
    echo "  ✅ Аккорд $chord_name добавлен"
}

# Функция добавления квадрата (секции)
add_square() {
    local square_id="$1"
    local square_name="$2"
    local chord1="$3"
    local chord2="$4"
    local chord3="$5"
    local chord4="$6"
    
    sqlite3 "$DB" "INSERT OR REPLACE INTO Квадраты (
        id, название, аккорд1_id, аккорд2_id, аккорд3_id, аккорд4_id
    ) VALUES (
        '$square_id', '$square_name', '$chord1', '$chord2', '$chord3', '$chord4'
    );"
    echo "  📦 Квадрат '$square_name' добавлен"
}

# Функция создания аппликатуры (связки квадратов)
add_fingering() {
    local fingering_id="$1"
    local piece_id="$2"
    local sq1="$3"; local sq2="$4"; local sq3="$5"; local sq4="$6"
    local sq5="$7"; local sq6="$8"; local sq7="$9"; local sq8="${10}"
    
    sqlite3 "$DB" "INSERT OR REPLACE INTO Аппликатуры (
        id, произведение_id, квадрат1_id, квадрат2_id, квадрат3_id, квадрат4_id,
        квадрат5_id, квадрат6_id, квадрат7_id, квадрат8_id
    ) VALUES (
        '$fingering_id', '$piece_id', '$sq1', '$sq2', '$sq3', '$sq4',
        '$sq5', '$sq6', '$sq7', '$sq8'
    );"
    echo "  🔗 Аппликатура создана"
}

# Функция добавления произведения
add_piece() {
    local piece_id="$1"
    local piece_name="$2"
    local author="$3"
    local bpm="$4"
    
    sqlite3 "$DB" "INSERT OR REPLACE INTO Произведения (id, название, автор, bpm) VALUES ('$piece_id', '$piece_name', '$author', $bpm);"
    echo "🎵 Произведение '$piece_name' добавлено (BPM: $bpm)"
}

# =============================================
# ИНТЕРАКТИВНЫЙ РЕЖИМ
# =============================================

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "     🎸  ДОБАВЛЕНИЕ ПРОИЗВЕДЕНИЯ В БАЗУ LED-НАКЛАДКИ  🎸"
echo "═══════════════════════════════════════════════════════════"
echo ""

read -p "📝 ID произведения (например p4): " piece_id
read -p "📝 Название произведения: " piece_name
read -p "👤 Автор: " author
read -p "🎚️  BPM (темп): " bpm

add_piece "$piece_id" "$piece_name" "$author" "$bpm"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "     🎼  ДОБАВЛЕНИЕ АККОРДОВ В СПРАВОЧНИК"
echo "═══════════════════════════════════════════════════════════"
echo ""

while true; do
    read -p "Добавить аккорд? (y/n): " add_ch
    if [ "$add_ch" != "y" ]; then break; fi
    
    read -p "  ID аккорда (например fm): " chord_id
    read -p "  Название (например Fm): " chord_name
    read -p "  Аппликатура (6 струн, например x02210): " fingering
    add_chord "$chord_id" "$chord_name" "$fingering"
    echo ""
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "     📦  ДОБАВЛЕНИЕ КВАДРАТОВ (секций)"
echo "═══════════════════════════════════════════════════════════"
echo ""

declare -a square_ids
declare -a square_names

square_count=0
while true; do
    read -p "Добавить квадрат? (y/n): " add_sq
    if [ "$add_sq" != "y" ]; then break; fi
    
    square_count=$((square_count + 1))
    echo ""
    echo "--- Квадрат №$square_count ---"
    
    read -p "  ID квадрата (например verse3): " square_id
    read -p "  Название (Интро, Куплет, Припев, Бридж, Соло, Аутро): " square_name
    
    square_ids[$square_count]="$square_id"
    square_names[$square_count]="$square_name"
    
    echo ""
    echo "  🎸 Аккорды в квадрате (до 4-х):"
    
    chords=("" "" "" "")
    
    for i in 1 2 3 4; do
        read -p "    Аккорд $i (ID, Enter если пусто): " chord_in
        if [ -z "$chord_in" ]; then break; fi
        chords[$i-1]="$chord_in"
    done
    
    add_square "$square_id" "$square_name" \
        "${chords[0]}" "${chords[1]}" "${chords[2]}" "${chords[3]}"
    
    echo ""
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "     🔗  ПОРЯДОК КВАДРАТОВ В ПРОИЗВЕДЕНИИ"
echo "═══════════════════════════════════════════════════════════"
echo ""

fingering_id="fing_$(date +%s)"
sq_order=( "" "" "" "" "" "" "" "" )

for i in $(seq 1 $square_count); do
    echo "$i. ${square_names[$i]} (${square_ids[$i]})"
    read -p "   Этот квадрат идёт в произведении? (y/n): " use_sq
    if [ "$use_sq" = "y" ]; then
        sq_order[$i-1]="${square_ids[$i]}"
    fi
done

add_fingering "$fingering_id" "$piece_id" \
    "${sq_order[0]}" "${sq_order[1]}" "${sq_order[2]}" "${sq_order[3]}" \
    "${sq_order[4]}" "${sq_order[5]}" "${sq_order[6]}" "${sq_order[7]}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "     ✅  ГОТОВО! Произведение добавлено!"
echo "═══════════════════════════════════════════════════════════"
echo ""

sqlite3 "$DB" "SELECT название, автор, bpm FROM Произведения WHERE id='$piece_id';"

