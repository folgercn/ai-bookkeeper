import json
from typing import Dict, Any, List, Optional
from app.services.llm_parser import LLMParser
from app.config import settings
from app.utils.audit_logger import log_llm_conversation

class InstructionParser:
    def __init__(self, llm_parser: LLMParser):
        self.llm = llm_parser

    async def parse_instruction(self, user_input: str, batch_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        使用 LLM 解析用户对暂存条目的操作意图
        """
        if self.llm.is_mock:
            if "全部确认" in user_input:
                tids = [i["temp_id"] for i in batch_context["items"] if i["status"] == "pending"]
                return [{"type": "confirm", "targets": tids}]
            if "1和2确认" in user_input:
                return [
                    {"type": "confirm", "targets": [1, 2]},
                    {"type": "modify", "targets": [3], "modifications": {"amount": 120.0, "main_category": "交通", "sub_category": "充值"}}
                ]
            return []
        system_prompt = f"""
你是一个记账指令解析助手。用户正在查看一个包含多个待确认账单条目的批次。
你的任务是解析用户的自然语言指令，并将其转换为结构化的操作序列。

## 当前批次内容 (batch_id: {batch_context['batch_id']}):
{json.dumps(batch_context['items'], ensure_ascii=False, indent=2)}

## 用户的分类列表:
{json.dumps(batch_context['categories'], ensure_ascii=False)}

## 用户的家庭成员 (消费人):
{json.dumps(batch_context.get('user_payees', []), ensure_ascii=False)}

## 用户的资产账户:
{json.dumps(batch_context.get('user_assets', []), ensure_ascii=False)}

## 输出要求
必须返回一个 JSON 对象，包含 `actions` 列表：
```json
{{
    "actions": [
        {{
            "type": "confirm", 
            "targets": [1, 2]
        }},
        {{
            "type": "modify",
            "targets": [3],
            "modifications": {{
                "amount": 100.0,
                "main_category": "购物",
                "remark": "新的备注"
            }}
        }},
        {{
            "type": "delete",
            "targets": [4]
        }},
        {{
            "type": "cancel_all"
        }}
    ]
}}
```

## 注意事项
1. 如果用户说"1和2确认"，type为"confirm"，targets为[1, 2]。
2. 如果用户说"全部确认"，type为"confirm"，targets包含所有 pending 条目的编号。
3. 如果用户提到一个不存在的分类，请在 modifications 中如实记录，由业务逻辑判断是否需要创建。
4. 如果指令模糊，请尝试给出最可能的解析。
"""
        try:
            response = await self.llm.client.post(
                "/chat/completions",
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.0
                }
            )
            response.raise_for_status()
            result = response.json()
            content_str = result.get("choices", [{}])[0].get("message", {}).get("content", "{{}}")
            parsed = json.loads(content_str)
            
            # 记录审计日志
            await log_llm_conversation(
                type="instruction_parse",
                user_id=batch_context.get("user_id", "unknown"),
                batch_id=batch_context.get("batch_id"),
                system_prompt=system_prompt,
                user_input=user_input,
                response=parsed
            )
            
            return parsed.get("actions", [])
        except Exception as e:
            print(f"指令解析失败: {e}")
            return []
