import json
import aiofiles
import os
from datetime import datetime
from typing import Any, Dict

LOG_FILE = "data/llm_audit.log"

async def log_llm_conversation(
    type: str, 
    user_id: str, 
    system_prompt: str, 
    user_input: Any, 
    response: Any,
    batch_id: str = None
):
    """记录 LLM 对话审计日志"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": type,
        "user_id": user_id,
        "batch_id": batch_id,
        "system_prompt": system_prompt,
        "user_input": user_input,
        "response": response
    }
    
    # 确保目录存在
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    async with aiofiles.open(LOG_FILE, mode="a", encoding="utf-8") as f:
        await f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
