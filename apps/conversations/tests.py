from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Conversation, Message

User = get_user_model()


class TestConversationAPI(APITestCase):
    def setUp(self):
        """테스트를 위한 초기 설정"""
        # 테스트용 사용자 2명 생성
        self.user1 = User.objects.create_user(
            email="user1@test.com", password="password123", username="user1"
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com", password="password123", username="user2"
        )

        # API 클라이언트 생성 및 user1로 인증
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        # user1을 위한 대화 1개 생성
        self.conversation1 = Conversation.objects.create(
            owner=self.user1, title="User1's Conversation"
        )
        # user2를 위한 대화 1개 생성
        self.conversation2 = Conversation.objects.create(
            owner=self.user2, title="User2's Conversation"
        )

    def test_create_conversation(self):
        """대화 생성 테스트"""
        url = reverse("conversations:conversation-list")
        data = {"title": "New Conversation"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Conversation")
        self.assertTrue(
            Conversation.objects.filter(
                owner=self.user1, title="New Conversation"
            ).exists()
        )

    def test_list_conversations(self):
        """대화 목록 조회 테스트 - 자신의 대화만 보여야 함"""
        url = reverse("conversations:conversation-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # user1의 대화는 1개이므로, 목록에 1개만 있어야 함
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], self.conversation1.title)

    def test_retrieve_conversation(self):
        """특정 대화 조회 테스트"""
        url = reverse(
            "conversations:conversation-detail", kwargs={"pk": self.conversation1.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.conversation1.title)

    def test_update_conversation(self):
        """대화 수정 테스트"""
        url = reverse(
            "conversations:conversation-detail", kwargs={"pk": self.conversation1.id}
        )
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")
        self.conversation1.refresh_from_db()
        self.assertEqual(self.conversation1.title, "Updated Title")

    def test_delete_conversation(self):
        """대화 삭제 테스트"""
        url = reverse(
            "conversations:conversation-detail", kwargs={"pk": self.conversation1.id}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Conversation.objects.filter(id=self.conversation1.id).exists())

    def test_unauthorized_access(self):
        """미인증 사용자 접근 차단 테스트"""
        self.client.force_authenticate(user=None)
        url = reverse("conversations:conversation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_access_to_other_user_conversation(self):
        """다른 사용자의 대화에 접근 차단 테스트"""
        # user2의 대화에 접근 시도
        url = reverse(
            "conversations:conversation-detail", kwargs={"pk": self.conversation2.id}
        )
        response = self.client.get(url)

        # IsOwner 권한에 의해 404 Not Found가 반환됨
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestMessageAPI(APITestCase):
    def setUp(self):
        """테스트를 위한 초기 설정"""
        self.user1 = User.objects.create_user(
            email="user1@test.com", password="password123", username="user1"
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com", password="password123", username="user2"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        self.conversation1 = Conversation.objects.create(
            owner=self.user1, title="User1's Conversation"
        )
        self.conversation2 = Conversation.objects.create(
            owner=self.user2, title="User2's Conversation"
        )

        # user1의 대화에 메시지 1개 생성
        self.message1 = Message.objects.create(
            conversation=self.conversation1, role="user", content="Hello"
        )

    def test_create_message(self):
        """메시지 생성 테스트"""
        url = reverse(
            "conversations:message-list-create",
            kwargs={"conversation_pk": self.conversation1.id},
        )
        data = {"content": "New message"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "New message")
        self.assertEqual(
            response.data["role"], "user"
        )  # 자동으로 'user' 역할이 부여되어야 함
        self.assertTrue(
            Message.objects.filter(
                conversation=self.conversation1, content="New message"
            ).exists()
        )

    def test_list_messages(self):
        """메시지 목록 조회 테스트"""
        url = reverse(
            "conversations:message-list-create",
            kwargs={"conversation_pk": self.conversation1.id},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], self.message1.content)

    def test_forbidden_create_message_in_other_user_conversation(self):
        """다른 사용자의 대화에 메시지 생성 차단 테스트"""
        url = reverse(
            "conversations:message-list-create",
            kwargs={"conversation_pk": self.conversation2.id},  # user2의 대화
        )
        data = {"content": "Forbidden message"}
        response = self.client.post(url, data)

        # IsOwner 권한에 의해 403 Forbidden이 반환됨
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_list_messages_from_other_user_conversation(self):
        """다른 사용자의 대화에서 메시지 목록 조회 차단 테스트"""
        url = reverse(
            "conversations:message-list-create",
            kwargs={"conversation_pk": self.conversation2.id},  # user2의 대화
        )
        response = self.client.get(url)

        # IsOwner 권한에 의해 403 Forbidden이 반환됨
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
