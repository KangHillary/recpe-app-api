from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        """Initial setup of the test clients"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='kangogo@gmail.com',
            password='pass12345'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='sergon@gmail.com',
            password='passwd7788',
            name='Kangogo hillary sergon'
        )

    def test_users_listed(self):
        """test that users are listed on user pages"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res,self.user.name)
        self.assertContains(res,self.user.email)

    def test_user_page_change(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """test that create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code,200)