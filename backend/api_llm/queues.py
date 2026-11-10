"""

Єдине місце з іменами Celery-тасок і черг.
Імпортуй звідси в celery_app.py, воркерах і queue-сервісі, не пиши рядки вручну.
"""

LLM_EVALUATION_TASK = "llm.evaluation"
LLM_QUEUE = "llm_tasks"

JUDGE_EVALUATION_TASK = "llm.judge.evaluation"
JUDGE_EVALUATION_QUEUE = "judge_tasks"

CHAT_TASK = "chat.generate_text"
CHAT_QUEUE = "chat_tasks"

ATTACK_DATASET_TASK = "attack.build_dataset"
ATTACK_DATASET_QUEUE = "attack_build_dataset_tasks"

ATTACK_GENERATION_TASK = "attack.generate"
ATTACK_GENERATION_QUEUE = "attack_generation_tasks"

ATTACK_JUDGE_TASK = "attack.judge"
ATTACK_JUDGE_QUEUE = "attack_judge_tasks"