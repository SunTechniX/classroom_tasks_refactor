#!/usr/bin/env python3
import json
import sys
import os
import argparse
from pathlib import Path

def extract_and_output_env():
    config_path = ".github/tasks.json"
    if not os.path.exists(config_path):
        print("❌ .github/tasks.json not found", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        print("⚠️ GITHUB_OUTPUT not set (running locally?)", file=sys.stderr)
        return

    with open(github_output, "a") as f:
        for task in config["tasks"]:
            task_id = task["id"]
            path = f"./{task_id}_aggregated.txt"
            encoded = ""
            if os.path.exists(path):
                with open(path) as fp:
                    content = fp.read()
                if "AGGREGATED_RESULT=" in content:
                    encoded = content.split("AGGREGATED_RESULT=", 1)[1].strip()
            f.write(f"{task_id}_aggregated={encoded}\n")

def generate_summary():
    config_path = ".github/tasks.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    total_score = 0
    max_total = 0
    task_scores = {}

    for task in config["tasks"]:
        task_id = task["id"]
        max_score = task["max_score"]
        max_total += max_score

        json_path = f"results/{task_id}.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            score = sum(t.get("score", 0) for t in data["tests"])
        else:
            score = 0

        task_scores[task_id] = score
        total_score += score

    percentage = int(100 * total_score / max_total) if max_total > 0 else 0

    summary = []
    summary.append("## 📊 ИТОГОВЫЙ ОТЧЕТ ПО ВСЕМ ЗАДАНИЯМ\n")
    summary.append("### 📈 Сводная таблица\n")
    summary.append("| Задание | Баллы | Максимум | Статус |")
    summary.append("|---------|-------|----------|--------|")

    for task in config["tasks"]:
        tid = task["id"]
        name = task["name"]
        score = task_scores[tid]
        max_score = task["max_score"]
        status = "✅" if score == max_score else ("⚠️" if score > 0 else "❌")
        summary.append(f"| **{name}** | {score} | {max_score} | {status} |")

    summary.append(f"| **ВСЕГО** | **{total_score}** | **{max_total}** | **{percentage}%** |")
    summary.append("")

    summary.append("### 📁 Найденные файлы:\n")
    for task in config["tasks"]:
        f = task["file"]
        if os.path.exists(f):
            summary.append(f"✅ **{f}** - найден")
        else:
            summary.append(f"❌ **{f}** - не найден")

    summary.append("")
    summary.append(f"### 🏆 Итоговая оценка: **{total_score} / {max_total}**")
    summary.append("")
    if total_score == max_total:
        summary.append("🎉 **ПОЗДРАВЛЯЕМ! Все задачи выполнены на 100%!**")
    else:
        summary.append("💡 **Есть что улучшить! Смотри детали тестов.**")
    summary.append("")
    summary.append(f"**GitHub Classroom: {total_score}/{max_total} баллов**")
    summary.append("")
    summary.append("*Автоматическая проверка завершена* • $(date)")

    # Запись в GITHUB_STEP_SUMMARY
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY", "/dev/stdout")
    with open(summary_file, "a") as f:
        f.write("\n".join(summary))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--output-env", action="store_true")
    parser.add_argument("--generate-summary", action="store_true")

    args = parser.parse_args()

    if args.extract and args.output_env:
        extract_and_output_env()
    elif args.generate_summary:
        generate_summary()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
