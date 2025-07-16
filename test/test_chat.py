import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_chat_endpoint():
    """测试聊天接口"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 模拟登录获取token
        token = "test_token"
        
        # 发送聊天消息
        response = await ac.post(
            "/api/chat/",
            json={"message": "我感觉今天呼吸有点困难"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert len(data["response"]) > 0

@pytest.mark.asyncio
async def test_chat_with_session():
    """测试带会话ID的聊天"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = "test_token"
        session_id = "test_session_123"
        
        # 第一条消息
        response1 = await ac.post(
            "/api/chat/",
            json={
                "message": "你好",
                "session_id": session_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response1.status_code == 200
        assert response1.json()["session_id"] == session_id
        
        # 第二条消息（应该记住上下文）
        response2 = await ac.post(
            "/api/chat/",
            json={
                "message": "我刚才说了什么？",
                "session_id": session_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response2.status_code == 200
        # TODO: 验证上下文记忆