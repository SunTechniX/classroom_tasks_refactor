#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import encode_result_for_classroom, make_task_result_stub

def main():
    config_path = ".github/tasks.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    for task in config["tasks"]:
        task_id = task["id"]
        json_path = f"results/{task_id}.json"

        if not os.path.exists(json_path):
            print(f"⚠️ {json_path} missing — creating stub", file=sys.stderr)
            result_data = make_task_result_stub(task)
        else:
            with open(json_path, "r", encoding="utf-8") as f:
                result_data = json.load(f)

        total_score = sum(t.get("score", 0) for t in result_data["tests"])
        max_score = task["max_score"]

        aggregated = {
            "version": 1,
            "status": "pass" if total_score == max_score else "fail",
            "max_score": max_score,
            "tests": [{
                "name": task["name"],
                "status": "pass" if total_score == max_score else "fail",
                "score": total_score,
                "output": f"Набрано баллов: {total_score}/{max_score}"
            }]
        }

        encoded = encode_result_for_classroom(aggregated)
        with open(f"{task_id}_aggregated.txt", "w") as f:
            f.write(f"AGGREGATED_RESULT={encoded}\n")

        print(f"📦 Aggregated {task_id}: {total_score}/{max_score}")

if __name__ == "__main__":
    main()
