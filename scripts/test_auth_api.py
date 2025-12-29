import asyncio
import httpx
import time

async def test_auth():
    base_url = "http://127.0.0.1:8000/v1"
    
    async with httpx.AsyncClient() as client:
        # 1. 注册
        print("\n--- 测试用户注册 ---")
        try:
            reg_resp = await client.post(f"{base_url}/auth/register", json={
                "username": f"testuser_{int(time.time())}",
                "password": "testpassword123"
            })
            print(f"Status: {reg_resp.status_code}")
            print(f"Response: {reg_resp.json()}")
            
            if reg_resp.status_code == 200:
                user_data = reg_resp.json()["data"]
                api_key = user_data["api_key"]
                
                # 2. 登录
                print("\n--- 测试用户登录 ---")
                login_resp = await client.post(f"{base_url}/auth/login", json={
                    "username": user_data["username"],
                    "password": "testpassword123"
                })
                print(f"Status: {login_resp.status_code}")
                print(f"Response: {login_resp.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth())
