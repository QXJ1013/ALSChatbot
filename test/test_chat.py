import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_chat_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # get token
        token = "test_token"
        
        # send message
        response = await ac.post(
            "/api/chat/",
            json={"message": "I feel a bit difficult to breathe today"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert len(data["response"]) > 0

@pytest.mark.asyncio
async def test_chat_with_session():
    """test chat with id"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = "test_token"
        session_id = "test_session_123"
        
        response1 = await ac.post(
            "/api/chat/",
            json={
                "message": "hello",
                "session_id": session_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response1.status_code == 200
        assert response1.json()["session_id"] == session_id
        
        response2 = await ac.post(
            "/api/chat/",
            json={
                "message": "what did I say？",
                "session_id": session_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response2.status_code == 200
        # TODO: test context memory