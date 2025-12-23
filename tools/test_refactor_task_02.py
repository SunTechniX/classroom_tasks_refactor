#!/usr/bin/env python3
import ast
import sys
import os

def count_expression_314_power2(tree):
    count = 0
    for node in ast.walk(tree):
        if (isinstance(node, ast.BinOp) and
            isinstance(node.op, ast.Pow) and
            isinstance(node.right, ast.Constant) and node.right.value == 2 and
            isinstance(node.left, ast.BinOp) and
            isinstance(node.left.op, ast.Mult) and
            isinstance(node.left.left, ast.Constant) and node.left.left.value == 3.14):
            count += 1
    return count

def check_task_02():
    if not os.path.exists("task_02.py"):
        return False, "Файл task_02.py не найден"
    
    try:
        with open("task_02.py", "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка: {e}"

    # Проверка: есть ли функция circle_area
    has_func = any(
        isinstance(node, ast.FunctionDef) and node.name == "circle_area"
        for node in ast.walk(tree)
    )
    if not has_func:
        return False, "Функция 'circle_area' не найдена"

    # Считаем, сколько раз встречается 3.14 * ... ** 2
    expr_count = count_expression_314_power2(tree)
    if expr_count > 1:
        return False, f"Выражение '3.14 * r ** 2' встречается {expr_count} раз(а) — должно быть ≤ 1 (внутри функции)"

    # Проверяем поведение
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "task_02.py"],
            input="1.0\n2.0\n", text=True, capture_output=True, timeout=3
        )
        if result.returncode != 0:
            return False, "Программа завершилась с ошибкой"
        expected = "3.14\n12.56\n"
        if result.stdout != expected:
            return False, f"Неверный вывод. Ожидалось:\n{expected}\nПолучено:\n{result.stdout}"
    except Exception as e:
        return False, f"Ошибка при запуске программы: {e}"

    return True, "OK"

if __name__ == "__main__":
    ok, msg = check_task_02()
    if ok:
        print("✅ task_02: Вынос кода в функцию выполнен корректно")
        sys.exit(0)
    else:
        print(f"❌ task_02: {msg}")
        sys.exit(1)