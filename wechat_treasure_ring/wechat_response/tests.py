from django.test import TestCase, RequestFactory
from wechat_response.models import *
from wechat_response.views import *

# Create your tests here.
class test_get_userinfo(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
	def test_invalidcode(self):
		request = self.factory.get('/data/getuserinfo?code=12345')
		response = get_userinfo(request)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content, "Invalid code".encode('utf-8'))

