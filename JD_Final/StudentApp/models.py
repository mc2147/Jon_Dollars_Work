from django.db import models
import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse
#from TeacherApp.models import GoodDeed, Reward, SpendRequest
#this is mapped to which button the student presses -> map to ID_num -> display using context on teacher's screen
class Request(models.Model):
	custom_input = models.CharField(max_length=1500, default="")
	deed_name = models.CharField(max_length=300, default="")
	points = models.IntegerField(default=0)
	time_created = models.DateTimeField(auto_now_add=True)
	time_string = models.CharField(max_length=1000, default="")
	updated = models.BooleanField(default=False)
	
	#Teacher and Classroom identifiers
	class_name = models.CharField(max_length=500, default="")
	teacher_name = models.CharField(max_length=500, default="")

class GoodDeed(models.Model):
	cost = models.IntegerField(default=0)
	name = models.CharField(max_length=1000)
	id_num = models.IntegerField(default=0)
	defined = models.BooleanField(default=False)	
	created = models.BooleanField(default=False)
	#Teacher and Classroom identifiers
	class_name = models.CharField(max_length=500, default="")


class SpendRequest(models.Model):
	rewardname = models.CharField(max_length=500, default="")
	number = models.IntegerField(default=0)
	student_name = models.CharField(max_length=500, default="") #maybe make into class later
	student_username = models.CharField(max_length=500, default="")
	time_created = models.DateTimeField(auto_now_add=True)
	#Teacher and Classroom identifiers
	class_name = models.CharField(max_length=500, default="")
	teacher_name = models.CharField(max_length=500, default="")
	#username = models.CharField(max_length=500, default="")
	#studentname = models.CharField(max_length=500, default="")
	#spender = models.CharField(max_length=500, default="")

class Reward(models.Model):
	cost = models.IntegerField(default=0)
	name = models.CharField(max_length=1000)
	#Teacher and Classroom identifiers
	class_name = models.CharField(max_length=500, default="")


class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	points = models.IntegerField(default=0)
	dollars = models.IntegerField(default=0)
	#10 points becomes 1 dollar
	inventory = []
	inventory_backup = models.CharField(max_length=1000,default="")
	requests = models.ManyToManyField("Request")	
	#Teacher and Classroom identifiers
	class_name = models.CharField(max_length=500, default="")
	teacher_user = models.CharField(max_length=500, default="")
	spendrequests = models.ManyToManyField("SpendRequest")
#	has_team = models.BooleanField(default=False)
	captain = models.BooleanField(default=False)
	def reset(self):
		if self.points >= 10:
			num_points = self.points
			remainder = num_points % 10
			self.dollars = (num_points - remainder)/10 		
			self.points = (num_points % 10)
	def update(self):
		if self.points >= 10:
			self.dollars = self.dollars + (self.points - (self.points%10))/10 		
			self.points = self.points%10


class Teacher(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	GDs = models.ManyToManyField("GoodDeed")
	Rewards = models.ManyToManyField("Reward")
	Requests = models.ManyToManyField("Request")
	Spendbox = models.ManyToManyField("SpendRequest")
	curr_class = models.CharField(max_length=500, default="")
	curr_team = models.CharField(max_length=500, default="")
	#inbox_backup = models.CharField(max_length=1000,default="")	
	#spendbox_backup = models.CharField(max_length=1000,default="")
	students = models.ManyToManyField("Student")
	classrooms = models.ManyToManyField("Classroom")
	#id_num = models.CharField(max_length=100, default="")
#	inbox = []
#	spendbox = []
	#Students and classrooms 


class Classroom(models.Model):
	#mapped under teacher
	#number and name
	class_num = models.IntegerField(default=0)
	name = models.CharField(max_length=500,default="")
	#MTMS begin here
	students = models.ManyToManyField(Student)
	teams = models.ManyToManyField("Team")
	GDs = models.ManyToManyField("GoodDeed")
	Rewards = models.ManyToManyField("Reward")
	PRs = models.ManyToManyField("Request")
	SRs = models.ManyToManyField("SpendRequest")

class Team(models.Model):
	#Call in sequence: update dollars, update points, convert 
	#team_class = models.OneToOneField(Classroom)
	rewards = models.ManyToManyField("Reward")
	PRs = models.ManyToManyField("Request")
	SRs = models.ManyToManyField("SpendRequest")
	members = models.ManyToManyField("Student")
	captain_username = models.CharField(max_length=200, default="")
	name = models.CharField(max_length=100,default="")
	points = models.IntegerField(default=0)
	teacher = models.CharField(max_length=200, default="")
	dollars = models.IntegerField(default=0)
	def update(self):
		self.update_dollars()
		self.update_points()
		self.convert()
	def update_points(self):
		point_total = 0
		for i in self.members.all():
			point_total = point_total + i.points
		self.points = point_total
		self.save()
	def update_dollars(self):
		dollar_total = 0
		for i in self.members.all():
			dollar_total = dollar_total + i.dollars
		self.dollars = dollar_total
		self.save()
	def convert(self):
		if self.points > 10:
			remainder = self.points % 10
			more_dollars = (self.points - remainder)/10
			self.dollars = self.dollars + more_dollars 		
			self.points = remainder
			self.save()		

	def number(self):
		return self.members.count()

	def add_student(self, studentusername):
		student_user = User.objects.get(username=studentusername)
		student = Student.objects.get(user=student_user)
		self.points = self.points + student.points
		self.members.add(student)
		self.save() 
	def remove_student(self, studentusername):
		student_user = User.objects.get(username=studentusername)
		student = Student.objects.get(user=student_user)
		self.points = self.points - student.points
		self.members.delete(student)
		self.save()
	def average(self):
		output = []
		raw_total = self.dollars*10 + self.points
		num = self.members.count()
		raw_avg = raw_total/num
		output.append((raw_avg - (raw_avg % 10))/10)
		output.append(raw_avg % 10)
		return output
	def leading_scorers(self):
		scores = []
		output = []
		names = []
		for i in self.members.all():
			scores.append(i.points)
		for x in self.members.all():
			print(x)
			print(x.points)
			if x.points == max(scores):
				names.append(x)
		output.append(names)
		output.append(max(scores))
		return output
	def score_leader(self):
		output = ""
		scores = []
		for i in self.members.all():
			scores.append(i.dollars*10 + i.points)
		for x in self.members.all():
			if x.dollars*10 + x.points == max(scores):
				output = x.user.first_name + " " + x.user.last_name
				output = output + " (" + str(x.dollars) + " Dollars, " + str(x.points) + " Points)"
		return output
	def have_points(self):
		output = []
		for i in self.members:
			if i.points > 0:
				output.append[i]
		return output




