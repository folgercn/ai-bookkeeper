import asyncio
import httpx
import time
import uuid

async def test_interaction_flow():
    base_url = "http://127.0.0.1:8000/v1"
    
    async with httpx.AsyncClient() as client:
        # 1. 注册与登录
        username = f"inter_{uuid.uuid4().hex[:6]}"
        print(f"\n--- 1. 用户注册: {username} ---")
        reg_resp = await client.post(f"{base_url}/auth/register", json={"username": username,"password": "password123"})
        api_key = reg_resp.json()["data"]["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}
        await client.post(f"{base_url}/config/categories/init", headers=headers)

        # 2. 提交多条记录
        content = "今天早上麦当劳花了35，中午买菜50，给手机充值100"
        print(f"\n--- 2. 提交记录: '{content}' ---")
        record_resp = await client.post(f"{base_url}/record", headers=headers, json={
            "type": "text", "content": content
        })
        record_data = record_resp.json()["data"]
        batch_id = record_data["batch_id"]
        print(f"识别出 {len(record_data['items'])} 条，batch_id: {batch_id}")

        # 3. 模拟交互：部分确认 + 修改内容
        # 假设 1是麦当劳，2是买菜，3是充值
        instruction = "1和2确认，3金额改成120而且分类改成'通信/充值'"
        print(f"\n--- 3. 交互指令: '{instruction}' ---")
        inter_resp = await client.post(f"{base_url}/record/interact", headers=headers, json={
            "batch_id": batch_id,
            "instruction": instruction
        })
        inter_data = inter_resp.json()
        print(f"交互响应成功: {inter_data['success']}")
        print(f"执行动作: {inter_data['data']['actions_executed']}")
        print(f"剩余待办: {inter_data['data']['remaining_pending']}")

        # 4. 最终确认剩余
        print("\n--- 4. 确认剩余条目 ---")
        last_resp = await client.post(f"{base_url}/record/interact", headers=headers, json={
            "batch_id": batch_id,
            "instruction": "全部确认"
        })
        print(f"最终状态: {last_resp.json()['message']}")

        # 5. 检查数据库是否入库 3 条
        print("\n--- 5. 验证账单列表 ---")
        exp_resp = await client.get(f"{base_url}/expenses", headers=headers)
        exp_data = exp_resp.json()["data"]
        print(f"最终确认账单数: {len(exp_data['items'])}")
        for i in exp_data['items']:
            print(f"- {i['remark']}: {i['amount']} ({i['main_category']})")

if __name__ == "__main__":
    asyncio.run(test_interaction_flow())
