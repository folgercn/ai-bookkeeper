import httpx
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.config import settings
from app.utils.audit_logger import log_llm_conversation

logger = logging.getLogger(__name__)

class LLMParser:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.OPENROUTER_BASE_URL,
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://family-accounting.app",
                "X-Title": settings.APP_NAME
            },
            timeout=60.0
        )
        self._prompt_template = self._load_prompt_template()
        self.is_mock = "xxxxx" in settings.OPENROUTER_API_KEY or not settings.OPENROUTER_API_KEY

    def _load_prompt_template(self) -> str:
        try:
            with open("prompts/system_prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            # 兜底 Prompt
            return "你是一个记账助手，请将用户输入解析为 JSON 格式的 items 列表。"

    async def parse(self, content: str, user_categories: Optional[List[Dict]] = None, **kwargs) -> List[Dict[str, Any]]:
        """解析文字内容"""
        if self.is_mock:
            # 简单的模拟解析逻辑
            if "麦当劳" in content:
                return [
                    {"date": "2025-12-26", "amount": 35.0, "main_category": "餐饮", "sub_category": "外卖", "remark": "麦当劳", "confidence": 1.0},
                    {"date": "2025-12-26", "amount": 50.0, "main_category": "餐饮", "sub_category": "食材采购", "remark": "买菜", "confidence": 1.0},
                    {"date": "2025-12-26", "amount": 100.0, "main_category": "其他", "remark": "手机充值", "confidence": 1.0},
                ]
            if "买菜" in content:
                return [{"date": "2025-12-26", "amount": 50.5, "main_category": "餐饮", "sub_category": "食材采购", "remark": "买菜", "confidence": 1.0}]
            return self._create_manual_item(content)

        current_date = datetime.now().strftime("%Y-%m-%d")
        categories_json = json.dumps(user_categories, ensure_ascii=False) if user_categories else "[]"
        payees_json = json.dumps(kwargs.get("user_payees", []), ensure_ascii=False)
        assets_json = json.dumps(kwargs.get("user_assets", []), ensure_ascii=False)
        
        system_prompt = self._prompt_template.format(
            current_date=current_date,
            user_categories_json=categories_json,
            user_payees_json=payees_json,
            user_assets_json=assets_json
        )

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # 兼容不同厂商返回格式
            content_str = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            parsed_data = json.loads(content_str)
            
            # 记录审计日志
            await log_llm_conversation(
                type="text_parse",
                user_id=kwargs.get("user_id", "unknown"),
                system_prompt=system_prompt,
                user_input=content,
                response=parsed_data
            )
            
            return parsed_data.get("items", [])

        except Exception as e:
            logger.error(f"LLM 解析异常: {e}")
            return self._create_manual_item(content)

    async def parse_image(self, image_base64: str, mime_type: str, user_categories: Optional[List[Dict]] = None, **kwargs) -> List[Dict[str, Any]]:
        """解析图片内容"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        categories_json = json.dumps(user_categories, ensure_ascii=False) if user_categories else "[]"
        payees_json = json.dumps(kwargs.get("user_payees", []), ensure_ascii=False)
        assets_json = json.dumps(kwargs.get("user_assets", []), ensure_ascii=False)
        
        system_prompt = self._prompt_template.format(
            current_date=current_date,
            user_categories_json=categories_json,
            user_payees_json=payees_json,
            user_assets_json=assets_json
        )

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "请解析这张账单截图中的所有消费记录。"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.0
                }
            )
            response.raise_for_status()
            result = response.json()
            
            content_str = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            parsed_data = json.loads(content_str)
            
            # 记录审计日志
            await log_llm_conversation(
                type="image_parse",
                user_id=kwargs.get("user_id", "unknown"),
                system_prompt=system_prompt,
                user_input="[IMAGE_BASE64_TRUNCATED]",
                response=parsed_data
            )
            
            return parsed_data.get("items", [])

        except Exception as e:
            logger.error(f"LLM 图片解析异常: {e}")
            # 图片失败不返回人工条目，因为备注无法捕获内容
            return []

    def _create_manual_item(self, content: str) -> List[Dict[str, Any]]:
        """解析失败时的兜底逻辑"""
        return [{
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": 0.0,
            "main_category": "其他",
            "sub_category": "未分类",
            "remark": f"[解析失败] {content[:50]}",
            "confidence": 0.0
        }]
