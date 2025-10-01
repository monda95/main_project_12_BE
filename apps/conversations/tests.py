import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Conversation

User = get_user_model()


@pytest.mark.django_db
class TestConversationAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password123"
        )
        self.conversation1 = Conversation.objects.create(
            owner=self.user1, title="User1's Conversation"
        )

    def test_create_conversation_authenticated(self):
        """인증된 사용자의 대화 생성 테스트"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/v1/conversations/", {"title": "New Auth Conversation"}
        )
        assert response.status_code == 201
        assert Conversation.objects.filter(
            title="New Auth Conversation", owner=self.user1
        ).exists()

    def test_create_conversation_unauthenticated(self):
        """미인증 사용자의 대화 생성 테스트"""
        response = self.client.post(
            "/api/v1/conversations/", {"title": "New Unauth Conversation"}
        )
        assert response.status_code == 201
        assert Conversation.objects.filter(
            title="New Unauth Conversation", owner=None
        ).exists()

    def test_list_conversations_owner_only(self):
        """자신의 대화 목록만 조회되는지 테스트"""
        Conversation.objects.create(owner=self.user2, title="User2's Conversation")
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/v1/conversations/")
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == self.conversation1.id

    def test_list_conversations_unauthenticated_fails(self):
        """미인증 사용자가 대화 목록 조회 시 401 에러 테스트"""
        response = self.client.get("/api/v1/conversations/")
        assert response.status_code == 401

    def test_retrieve_other_user_conversation_fails(self):
        """다른 사용자의 대화 상세 조회 실패 테스트"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/v1/conversations/{self.conversation1.id}/")
        assert response.status_code == 404  # IsOwner or queryset filter

    def test_delete_other_user_conversation_fails(self):
        """다른 사용자의 대화 삭제 실패 테스트"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/api/v1/conversations/{self.conversation1.id}/")
        assert response.status_code == 404

    def test_create_message_in_own_conversation_success(self):
        """자신의 대화에 메시지 작성 성공 테스트"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f"/api/v1/conversations/{self.conversation1.id}/messages/",
            {"content": "Hello, world!"},
        )
        assert response.status_code == 201
        assert self.conversation1.messages.count() == 1
        assert self.conversation1.messages.first().content == "Hello, world!"
        assert self.conversation1.messages.first().role == "user"

    def test_create_message_in_other_user_conversation_fails(self):
        """다른 사용자의 대화에 메시지 작성 실패 테스트"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f"/api/v1/conversations/{self.conversation1.id}/messages/",
            {"content": "Intruder!"},
        )
        assert response.status_code == 403  # IsOwner permission

    def test_create_message_with_ai_role_fails(self):
        """사용자가 'ai' 역할로 메시지 생성 시도 시 실패 테스트"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f"/api/v1/conversations/{self.conversation1.id}/messages/",
            {"content": "I am an AI!", "role": "ai"},
        )
        assert response.status_code == 400
