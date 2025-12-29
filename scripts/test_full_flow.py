import asyncio
import httpx
import time
import uuid

async def test_full_flow():
    base_url = "http://127.0.0.1:8000/v1"
    
    async with httpx.AsyncClient() as client:
        # 1. 注册
        username = f"user_{uuid.uuid4().hex[:6]}"
        print(f"\n--- 1. 注册用户: {username} ---")
        reg_resp = await client.post(f"{base_url}/auth/register", json={
            "username": username,
            "password": "testpassword123"
        })
        if reg_resp.status_code != 200:
            print(f"注册失败: {reg_resp.text}")
            return
        user_data = reg_resp.json()["data"]
        api_key = user_data["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}
        print("注册成功")

        # 2. 初始化分类
        print("\n--- 2. 初始化默认分类 ---")
        init_resp = await client.post(f"{base_url}/config/categories/init", headers=headers)
        print(f"Status: {init_resp.status_code}")
        if init_resp.status_code == 200:
            print(f"Response: {init_resp.text}")
        else:
            print(f"Error: {init_resp.text}")
            return

        # 3. 提交记账 (模拟文字)
        print("\n--- 3. 提交记账内容 ---")
        record_resp = await client.post(f"{base_url}/record", headers=headers, json={
            "type": "text",
            "content": "昨天在物美买菜花了50.5元"
        })
        print(f"Status: {record_resp.status_code}")
        print(f"Text: {record_resp.text}")
        if record_resp.status_code != 200:
             return
        record_data = record_resp.json()
        print(f"Response: {record_data}")

        if record_data["success"]:
            batch_id = record_data["data"]["batch_id"]
            
            # 4. 确认入库
            print("\n--- 4. 确认入库 ---")
            confirm_resp = await client.post(f"{base_url}/record/confirm", headers=headers, json={
                "batch_id": batch_id,
                "action": "confirm_all"
            })
            print(f"确认结果: {confirm_resp.json()}")

            # 5. 查询账单
            print("\n--- 5. 查询账单 ---")
            query_resp = await client.get(f"{base_url}/expenses", headers=headers)
            query_data = query_resp.json()
            print(f"账单总数: {query_data['data']['pagination']['total']}")
            print(f"统计摘要: {query_data['data']['summary']}")

            # 6. 导出测试
            print("\n--- 6. 导出 CSV ---")
            export_resp = await client.get(f"{base_url}/export/csv", headers=headers)
            print(f"导出结果: {export_resp.status_code}")
            print(f"CSV 预览: {export_resp.text[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
