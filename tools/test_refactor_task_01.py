#!/usr/bin/env python3
import ast
import sys
import os

def check_task_01():
    if not os.path.exists("task_01.py"):
        return False, "Файл task_01.py не найден"
    
    try:
        with open("task_01.py", "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка: {e}"

    # Проверяем, что "x" НЕ используется
    has_x = any(
        isinstance(node, ast.Name) and node.id == "x"
        for node in ast.walk(tree)
    )
    if has_x:
        return False, "Переменная 'x' всё ещё используется — переименуйте!"

    # Проверяем, что "user_id" используется
    has_user_id = any(
        isinstance(node, ast.Name) and node.id == "user_id"
        for node in ast.walk(tree)
    )
    if not has_user_id:
        return False, "Переменная 'user_id' не найдена — должно быть переименовано в неё"

    # Проверяем поведение: запускаем с тестовым вводом
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "task_01.py"],
            input="hi\n", text=True, capture_output=True, timeout=3
        )
        if result.returncode != 0:
            return False, "Программа завершилась с ошибкой"
        if result.stdout.strip() != "hihi":
            return False, f"Неверный вывод: ожидалось 'hihi', получено '{result.stdout.strip()}'"
    except Exception as e:
        return False, f"Ошибка при запуске программы: {e}"

    return True, "OK"

if __name__ == "__main__":
    ok, msg = check_task_01()
    if ok:
        print("✅ task_01: Переименование выполнено корректно")
        sys.exit(0)
    else:
        print(f"❌ task_01: {msg}")
        sys.exit(1)