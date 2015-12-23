# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import TestCase, RequestFactory
from wechat_response.models import *
from web_data.views import *
import json

# Create your tests here.
class test_ifregistered(TestCase):
	def setUp(self):
		self.user = RingUser.objects.create(
				user_id = "sheep94lion",
				nickname = "zhaoyi",
				headimgurl = "1.jpg",
				sex = "male",
				age = 21,
				height = 177,
				weight = 87,
				target = 10000,
				last_record = 12345,
				steps_totalused = 1355
		)
		self.factory = RequestFactory()

	def test_notregistered(self):
		request = self.factory.get('data/ifregistered/littlepig')
		response = ifregistered(request, "littlepig")
		self.assertEqual(response.status_code, 200)
		result = json.loads(response.content)
		self.assertEqual(result.get(u'ifregistered'), False)

	def test_doregistered(self):
		request = self.factory.get('data/ifregistered/sheep94lion')
		response = ifregistered(request, "sheep94lion")
		self.assertEqual(response.status_code, 200)
		result = json.loads(response.content.encode('utf-8'))
		self.assertEqual(result.get(u'ifregistered'), True)

	def test_nousers(self):
		self.user.delete()
		request = self.factory.get('data/ifregistered/littlepig')
		response = ifregistered(request, "littlepig")
		self.assertEqual(response.status_code, 200)
		result = json.loads(response.content)
		self.assertEqual(result.get(u'ifregistered'), False)

class test_saveuserbet(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user = RingUser.objects.create(
				user_id = "sheep94lion",
				nickname = "zhaoyi",
				headimgurl = "1.jpg",
				sex = "male",
				age = 21,
				height = 177,
				weight = 87,
				target = 10000,
				last_record = 12345,
				steps_totalused = 0
			)
		self.subject = GuessSubject.objects.create(
				id=3,
				content='1',
				choiceA='1',
				choiceB='1',
				stepsA=0,
				stepsB=0,
				result='',
				disabled=False
			)

	def test_savesuccess(self):
		request = self.factory.get('data/saveuserbet?subid=3&openid=sheep94lion&steps=100&choice=A')
		response = save_user_bet(request)
		subject = GuessSubject.objects.all()[0]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(subject.stepsA, 100)
		record = GuessInfomation.objects.all()[0]
		self.assertEqual(record.user_id, "sheep94lion")
		self.assertEqual(record.choice, 'A')

class test_getguesssubject(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.subject1 = GuessSubject.objects.create(
			id=3,
			content="hello_not",
			choiceA="good",
			choiceB="bad",
			stepsA=0,
			stepsB=0,
			result="",
			disabled=False
		)
		self.subject2 = GuessSubject.objects.create(
			id=4,
			content="hello_dis",
			choiceA="good",
			choiceB="bad",
			stepsA=0,
			stepsB=0,
			result="A",
			disabled=True
		)
		self.subject3 = GuessSubject.objects.create(
			id=2,
			content="hello_no_result",
			choiceA="good",
			choiceB="bad",
			stepsA=0,
			stepsB=0,
			result="",
			disabled=True
		)

	def test_getnotdisabled(self):
		request = self.factory.get('data/getguesssubject')
		response = get_guess_subject(request)
		self.assertContains(response, "hello_not", count=1, status_code=200)

	def test_getdisabled(self):
		request = self.factory.get('data/getguesssubject')
		response = get_guess_subject(request)
		self.assertNotContains(response, "hello_dis", status_code=200)

	def test_getnoresult(self):
		request = self.factory.get('data/getguesssubject')
		response = get_guess_subject(request)
		self.assertNotContains(response, "hello_no_result", status_code=200)

class test_freezeactivity(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.subject1 = GuessSubject.objects.create(
			id=3,
			content="hello_not",
			choiceA="good",
			choiceB="bad",
			stepsA=0,
			stepsB=0,
			result="",
			disabled=False
		)
		self.subject2 = GuessSubject.objects.create(
			id=4,
			content="hello_dis",
			choiceA="good",
			choiceB="bad",
			stepsA=0,
			stepsB=0,
			result="A",
			disabled=True
		)
		self.subject3 = GuessSubject.objects.create(
			id=2,
			content="hello_no_result",
			choiceA="good",
			choiceB="bad",
			stepsA=0,
			stepsB=0,
			result="",
			disabled=True
		)


	def test_freezenotfreezed(self):
		request = self.factory.get('data/freeze?subid=3')
		response = freeze_activity(request)
		self.assertContains(response, "success", count=1, status_code=200)
		self.subject1 = GuessSubject.objects.filter(id=3)[0]
		self.assertEqual(self.subject1.disabled, True)


	def test_freezefreezed(self):
		request = self.factory.get('data/freeze?subid=4')
		response = freeze_activity(request)
		self.assertContains(response, "success", count=1, status_code=200)
		self.subject2 = GuessSubject.objects.filter(id=4)[0]
		self.assertEqual(self.subject2.disabled, True)


	def test_freezegetresult(self):
		request = self.factory.get('data/freeze?subid=2')
		response = freeze_activity(request)
		self.assertContains(response, "success", count=1, status_code=200)
		self.subject3 = GuessSubject.objects.filter(id=2)[0]
		self.assertEqual(self.subject3.disabled, True)

	def test_freezenotexisted(self):
		request = self.factory.get('data/freeze?subid=100')
		response = freeze_activity(request)
		self.assertContains(response, "failure", count=1, status_code=200)

class test_addguessobject(TestCase):
	def setUp(self):
		self.factory = RequestFactory()

	def test_addguessobject(self):
		request = self.factory.post('data/addguesssubject', {'content':'hello', 'choiceA':'good', 'choiceB':'bad'})
		response = add_guess_subject(request)
		self.assertContains(response, "success", count=1, status_code=200)
		subject = GuessSubject.objects.filter(id=1)
		self.assertNotEqual(subject, [])
		self.assertEqual(subject[0].content, "hello")

	def test_addguessobjectnotcomplete(self):
		request = self.factory.post('data/addguesssubject', {'content':'world'})
		response = add_guess_subject(request)
		self.assertContains(response, "failure", count=1, status_code=200)
		subject = GuessSubject.objects.filter(id=1)
		self.assertQuerysetEqual(subject, [])

class test_calculate(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user1 = RingUser.objects.create(
				id=1,
				user_id = "czj",
				nickname = "zhaoyi",
				headimgurl = "1.jpg",
				sex = "male",
				age = 21,
				height = 177,
				weight = 87,
				target = 10000,
				last_record = 12345,
				steps_totalused = 100
		)
		self.user2 = RingUser.objects.create(
				id=2,
				user_id = "xja",
				nickname = "zhaoyi",
				headimgurl = "1.jpg",
				sex = "male",
				age = 21,
				height = 177,
				weight = 87,
				target = 10000,
				last_record = 12345,
				steps_totalused = 200
		)
		self.information1 = GuessInfomation.objects.create(
			id=1,
			user_id="czj",
			sub_id=1,
			choice='A',
			steps=15
		)
		self.information2 = GuessInfomation.objects.create(
			id=2,
			user_id="czj",
			sub_id=2,
			choice='B',
			steps=20
		)
		self.information3 = GuessInfomation.objects.create(
			id=3,
			user_id="czj",
			sub_id=3,
			choice='B',
			steps=30
		)
		self.information4 = GuessInfomation.objects.create(
			id=4,
			user_id="xja",
			sub_id=1,
			choice='B',
			steps=17
		)
		self.information5 = GuessInfomation.objects.create(
			id=5,
			user_id="xja",
			sub_id=2,
			choice='A',
			steps=16
		)
		self.information6 = GuessInfomation.objects.create(
			id=6,
			user_id="xja",
			sub_id=3,
			choice='B',
			steps=18
		)
		self.subject1 = GuessSubject.objects.create(
			id=1,
			content="hello_not",
			choiceA="good_not",
			choiceB="bad_not",
			stepsA=15,
			stepsB=17,
			result="",
			disabled=False
		)
		self.subject2 = GuessSubject.objects.create(
			id=2,
			content="hello_dis",
			choiceA="good_dis",
			choiceB="bad_dis",
			stepsA=16,
			stepsB=20,
			result="A",
			disabled=True
		)
		self.subject3 = GuessSubject.objects.create(
			id=3,
			content="hello_no_result",
			choiceA="good_no_result",
			choiceB="bad_no_result",
			stepsA=0,
			stepsB=48,
			result="",
			disabled=True
		)

	def test_calculatenotdisabled(self):
		request = self.factory.get('data/calculate?subid=1&choice=A')
		response = calculate(request)
		self.assertContains(response, "failure")

	def test_calculatenormalA(self):
		request = self.factory.get('data/calculate?subid=3&choice=A')
		response = calculate(request)
		self.assertContains(response, "success")
		user_info1 = RingUser.objects.filter(id=1)[0]
		user_info2 = RingUser.objects.filter(id=2)[0]
		self.assertEqual(user_info1.steps_totalused, 100)
		self.assertEqual(user_info2.steps_totalused, 200)

	def test_calculatenormalB(self):
		request = self.factory.get('data/calculate?subid=3&choice=B')
		response = calculate(request)
		self.assertContains(response, "success")
		user_info1 = RingUser.objects.filter(id=1)[0]
		user_info2 = RingUser.objects.filter(id=2)[0]
		self.assertEqual(user_info1.steps_totalused, 70)
		self.assertEqual(user_info2.steps_totalused, 182)

	def test_calculatealreadycalculated(self):
		request = self.factory.get('data/calculate?subid=2&choice=B')
		response = calculate(request)
		self.assertContains(response, "already calculated")
		user_info1 = RingUser.objects.filter(id=1)[0]
		user_info2 = RingUser.objects.filter(id=2)[0]
		self.assertEqual(user_info1.steps_totalused, 100)
		self.assertEqual(user_info2.steps_totalused, 200)

class test_autosave(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user1 = RingUser.objects.create(
				id=1,
				user_id = "czj",
				nickname = "zhaoyi",
				headimgurl = "1.jpg",
				sex = "male",
				age = 21,
				height = 177,
				weight = 87,
				target = 10000,
				last_record = 12345,
				steps_totalused = 100
		)
		self.user2 = RingUser.objects.create(
				id=2,
				user_id = "xja",
				nickname = "zhaoyi",
				headimgurl = "1.jpg",
				sex = "male",
				age = 21,
				height = 177,
				weight = 87,
				target = 10000,
				last_record = 12345,
				steps_totalused = 200
		)
		self.information1 = GuessInfomation.objects.create(
			id=1,
			user_id="czj",
			sub_id=1,
			choice='A',
			steps=15
		)
		self.information2 = GuessInfomation.objects.create(
			id=2,
			user_id="czj",
			sub_id=2,
			choice='B',
			steps=20
		)
		self.information3 = GuessInfomation.objects.create(
			id=3,
			user_id="czj",
			sub_id=3,
			choice='B',
			steps=30
		)
		self.information4 = GuessInfomation.objects.create(
			id=4,
			user_id="xja",
			sub_id=1,
			choice='B',
			steps=17
		)
		self.information5 = GuessInfomation.objects.create(
			id=5,
			user_id="xja",
			sub_id=2,
			choice='A',
			steps=16
		)
		self.information6 = GuessInfomation.objects.create(
			id=6,
			user_id="xja",
			sub_id=3,
			choice='B',
			steps=18
		)
		self.subject1 = GuessSubject.objects.create(
			id=1,
			content="hello_not",
			choiceA="good_not",
			choiceB="bad_not",
			stepsA=15,
			stepsB=17,
			result="",
			disabled=False
		)
		self.subject2 = GuessSubject.objects.create(
			id=2,
			content="hello_dis",
			choiceA="good_dis",
			choiceB="bad_dis",
			stepsA=16,
			stepsB=20,
			result="A",
			disabled=True
		)
		self.subject3 = GuessSubject.objects.create(
			id=3,
			content="hello_no_result",
			choiceA="good_no_result",
			choiceB="bad_no_result",
			stepsA=0,
			stepsB=48,
			result="",
			disabled=True
		)

	def test_sleepsavesucceed(self):
		request = self.factory.get('data/autosave?sleep=1&exercise_and_time=0')
		response = auto_save(request)
		self.assertContains(response, "success", count=1, status_code=200)
		data = RecordByDay.objects.all()
		self.assertEqual(len(data), 60)

	def test_exercisesavesucceed(self):
		request = self.factory.get('data/autosave?sleep=0&exercise_and_time=1')
		response = auto_save(request)
		self.assertContains(response, "success", count=1, status_code=200)
		data = RecordByDay.objects.all()
		self.assertEqual(len(data), 60)

	def test_exercisesavesucceed(self):
		request = self.factory.get('data/autosave?sleep=0&exercise_and_time=1')
		response = auto_save(request)
		self.assertContains(response, "success", count=1, status_code=200)
		subject = GuessSubject.objects.all()
		info = GuessInfomation.objects.all()
		self.assertIn(self.subject1, subject)
		self.assertNotIn(self.subject2, subject)
		self.assertIn(self.subject3, subject)
		self.assertIn(self.information1, info)
		self.assertIn(self.information3, info)
		self.assertNotIn(self.information2, info)
		self.assertNotIn(self.information5, info)
		self.assertIn(self.information4, info)
		self.assertIn(self.information6, info)

class test_register(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user2 = RingUser.objects.create(
				id=2,
				user_id = "xja",
				nickname = "zhaoyi",
				headimgurl = "1.jpg",
				sex = "male",
				age = 21,
				height = 177,
				weight = 87,
				target = 10000,
				last_record = 12345,
				steps_totalused = 200
		)

	def test_normalregister(self):
		request = self.factory.post('data/register', {"sex":"male", "age":20, "height":182, "weight":75, 'goal_step':100, "openid":'czj'})
		response = register(request)
		self.assertContains(response, "add info successfully", count=1, status_code=200)
		user = RingUser.objects.filter(user_id="czj")
		self.assertEqual(len(user), 1)
		self.assertEqual(user[0].sex, "male")
		self.assertEqual(user[0].user_id, "czj")

	def test_alreadyregistered(self):
		request = self.factory.post('data/register', {"sex":"female", "age":20, "height":182, "weight":75, 'goal_step':100, "openid":'xja'})
		response = register(request)
		self.assertContains(response, "add info successfully", count=1, status_code=200)
		user = RingUser.objects.all()
		self.assertEqual(len(user), 1)
		self.assertNotEqual(user[0].sex, "male")
		self.assertEqual(user[0].sex, "female")
		self.assertNotEqual(user[0].weight, 87)
		self.assertEqual(user[0].weight, 75)
		self.assertEqual(user[0].user_id, "xja")

	def test_notcomplete(self):
		request = self.factory.post('data/register', {"sex":"female", "height":182, "weight":75, 'goal_step':100, "openid":'xja'})
		response = register(request)
		self.assertContains(response, "failure", count=1, status_code=200)


class test_datachart(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user2 = RingUser.objects.create(
				id=2,
				user_id = "xja",
				nickname = "zhaoyi",
				headimgurl = "1.jpg",
				sex = "male",
				age = 21,
				height = 177,
				weight = 87,
				target = 10000,
				last_record = 12345,
				steps_totalused = 200
		)


	def test_getsleepdataexistshavedata(self):
		request1 = self.factory.get('data/autosave?sleep=1&exercise_and_time=0')
		request2 = self.factory.get('data/getsleepdata?openid=xja')
		auto_save(request1)
		response = get_sleepdata(request2)
		data = json.loads(response.content)
		self.assertEqual(data["isnull"], False)

	def test_getsleepdatanotexists(self):
		request = self.factory.get('data/getsleepdata?openid=czj')
		response = get_sleepdata(request)
		data = json.loads(response.content)
		self.assertEqual(data["isnull"], True)

	def test_getsleepdataexistsnodata(self):
		request = self.factory.get('data/getsleepdata?openid=xja')
		response = get_sleepdata(request)
		data = json.loads(response.content)
		self.assertEqual(data["isnull"], False)