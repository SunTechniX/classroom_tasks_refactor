# tools/utils.py
import json
import base64
import sys

def decode_autograding_result(encoded_result):
    if not encoded_result or encoded_result in ('null', 'undefined', '', 'None'):
        return {'score': 0, 'max_score': 0, 'tests': []}
    try:
        decoded = base64.b64decode(encoded_result).decode('utf-8')
        return json.loads(decoded)
    except Exception as e:
        print(f"ERROR decoding result: {e}", file=sys.stderr)
        return {'score': 0, 'max_score': 0, 'tests': []}

def encode_result_for_classroom(result_dict):
    json_str = json.dumps(result_dict, ensure_ascii=False)
    return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

def make_task_result_stub(task_config):
    """Создаёт заглушку для задачи, которая не прошла тестирование"""
    tests = []
    total_score = 0
    for test in task_config["tests"]:
        tests.append({
            "name": test["name"],
            "status": "fail",
            "raw_score": 0,
            "max_score": test["max_score"],
            "score": 0,
            "output": "Файл задания отсутствует или не запускается"
        })
    return {
        "version": 1,
        "status": "fail",
        "max_score": task_config["max_score"],
        "tests": tests
    }

