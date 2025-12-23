#!/usr/bin/env python3
import json
import sys
import os
import subprocess
import argparse
from pathlib import Path

# Путь к директории tools, чтобы можно было импортировать utils
sys.path.insert(0, str(Path(__file__).parent))
from utils import make_task_result_stub

def run_behavioral_test(task_config):
    """Запускает поведенческие тесты (как раньше)"""
    task_id = task_config["id"]
    task_file = task_config["file"]
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    result_path = results_dir / f"{task_id}.json"

    if not os.path.exists(task_file):
        print(f"⚠️ {task_file} не найден — создаём заглушку")
        stub = make_task_result_stub(task_config)
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(stub, f, ensure_ascii=False, indent=2)
        return

    tests = []
    total_score = 0

    for test in task_config["tests"]:
        try:
            result = subprocess.run(
                ["python3", task_file],
                input=test["input"],
                text=True,
                capture_output=True,
                timeout=5
            )
            output = result.stdout.strip()
            expected = test["expected_output"]
            method = test["comparison_method"]

            if method == "exact":
                passed = output == expected
            elif method == "contains":
                passed = expected in output
            else:
                passed = False

            score = test["max_score"] if passed else 0
            total_score += score

            tests.append({
                "name": test["name"],
                "status": "pass" if passed else "fail",
                "score": score,
                "output": output[:200]  # Обрезаем длинный вывод
            })

        except subprocess.TimeoutExpired:
            tests.append({
                "name": test["name"],
                "status": "fail",
                "score": 0,
                "output": "TIMEOUT"
            })
        except Exception as e:
            tests.append({
                "name": test["name"],
                "status": "fail",
                "score": 0,
                "output": f"ERROR: {str(e)}"
            })

    result_data = {
        "version": 1,
        "status": "pass" if total_score == task_config["max_score"] else "fail",
        "max_score": task_config["max_score"],
        "tests": tests
    }

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

def run_refactor_check(task_id: str, check_script: str, max_score: int):
    """Запускает скрипт проверки рефакторинга и генерирует results/{task_id}.json"""
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    result_path = results_dir / f"{task_id}.json"

    try:
        result = subprocess.run(
            ["python3", check_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        passed = result.returncode == 0
        score = max_score if passed else 0
        output = result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        passed = False
        score = 0
        output = f"Ошибка при запуске проверки рефакторинга: {e}"

    test_entry = {
        "name": "Проверка рефакторинга",
        "status": "pass" if passed else "fail",
        "score": score,
        "output": output[:200]
    }

    result_data = {
        "version": 1,
        "status": "pass" if score == max_score else "fail",
        "max_score": max_score,
        "tests": [test_entry]
    }

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    status = "✅" if passed else "❌"
    print(f"{status} Рефакторинг {task_id}: {output}")

def main():
    config_path = ".github/tasks.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Запускаем обычные тесты для всех задач
    for task in config["tasks"]:
        if not task["id"].endswith("_refactor"):
            print(f"🔍 Запуск тестов для {task['id']}")
            run_behavioral_test(task)

    # Запускаем проверки рефакторинга (если есть)
    refactor_tasks = [
        ("task_01_refactor", "tools/test_refactor_task_01.py", 20),
        ("task_02_refactor", "tools/test_refactor_task_02.py", 20),
    ]

    for task_id, script, max_score in refactor_tasks:
        print(f"🔍 Проверка рефакторинга: {task_id}")
        if os.path.exists(script):
            run_refactor_check(task_id, script, max_score)
        else:
            # Если скрипт не найден — создаём заглушку
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)
            stub = make_task_result_stub({
                "id": task_id,
                "max_score": max_score,
                "tests": [{"name": "Проверка", "max_score": max_score}]
            })
            with open(results_dir / f"{task_id}.json", "w") as f:
                json.dump(stub, f, ensure_ascii=False, indent=2)
            print(f"⚠️ Скрипт {script} не найден — создан заглушка-результат")

if __name__ == "__main__":
    main()