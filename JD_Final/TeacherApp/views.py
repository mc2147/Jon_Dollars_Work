from django.shortcuts import render
from django.contrib.auth.models import User, Group
from StudentApp.models import Student, Teacher
from StudentApp.models import Team, Classroom, Request
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from StudentApp.models import GoodDeed, SpendRequest, Reward
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout
from StudentApp.views import Login

def make_classrooms(user):
	if Teacher.objects.filter(user=user).exists():
		teacher = Teacher.objects.get(user=user)
	for i in range(1, 6):
		if Classroom.objects.filter(name="Classroom " + str(i)).exists() == False:
			x = Classroom(name="Classroom " + str(i))
			x.save()
			teacher.classrooms.add(x)
			teacher.save()



def get_classrooms():
	classes = Classroom.objects.all()
	class_names = []
	for i in classes:
		class_names.append(i.name)
	return class_names

def classroom_context(context, class_name):
	context['Classes'] = []
	if class_name == "":
		for i in Classroom.objects.all():
			context['Classes'].append(i.name)
	else:
		context['Classes'].append(class_name)
		for i in Classroom.objects.all():
			if i.name != class_name:
				context['Classes'].append(i.name)



def ClassroomContext(user, selection):
	output = []
	teacher = Teacher.objects.get(user=user)
	classrooms = teacher.classrooms.all()
	if selection == "":
		for i in classrooms:
			output.append(i.name)
	else:
		output.append(selection)
		for i in classrooms:
			if i.name != selection:
				output.append(i.name)
	return output
	
	
def ChangeClass():
	output = []
	if(request.GET.get("selectclass")):
		class_name = request.REQUEST.get("selectclass")
		output = ClassroomContext(user, class_name)
		#selected_class = Classroom.objects.get(name=class_name)
		teacher.curr_class = selected_class.name
		teacher.save()
	return output




def teacher_check(user):
	return Teacher.objects.filter(user=user).exists()

def teacher_info(user):
	output = {}

	teacher = Teacher.objects.get(user=user)
	teacher.save()
	all_classrooms = teacher.classrooms.all()
	classroom_name = teacher.curr_class
	classroom = Classroom.objects.get(name=classroom_name)
	students = classroom.students.all()
	GDs = classroom.GDs.all()
	rewards = classroom.Rewards.all()
	PRs = classroom.PRs.all()
	SRs = classroom.SRs.all()
	teams = classroom.teams.all()
	
	output["teacher"] = teacher
	output["all_classrooms"] = all_classrooms
	output["classroom_name"] = classroom_name
	output["classroom"] = classroom
	output["students"] = students
	output["GDs"] = GDs
	output["rewards"] = rewards
	output["PRs"] = PRs
	output["SRs"] = SRs
	output["teams"] = teams
	
	return output


#MANAGE CLASSES STARTS HERE
@user_passes_test(teacher_check)
def ManageClasses(request):
	user = request.user
	curr_teacher = Teacher.objects.get(user=user)
	curr_teacher.curr_class = curr_teacher.classrooms.all()[0].name
		# all_classrooms = teacher.classrooms.all()
		# teacher = Teacher.objects.get(user=user)
		# classroom_name = teacher.curr_class
		# classroom = Classroom.objects.get(name=classroom_name)
		# students = classroom.students.all()
		# GDs = classroom.GDs.all()
		# rewards = classroom.Rewards.all()
		# PRs = classroom.PRs.all()
		# SRs = classroom.SRs.all()
		# teams = classroom.teams.all()
	context = {}
	context["Classes"] = []
	class_names = []
	student_list = []
	curr_teacher.save()
	classroom = Classroom.objects.get(name=curr_teacher.curr_class)

	def CreateContext():
		for i in curr_teacher.classrooms.all():
			class_names.append(i.name)
		context["Classes"] = class_names
		for i in class_names:
			if request.GET.get(i):
				curr_teacher.curr_class = i
				curr_teacher.save()
		classroom = Classroom.objects.get(name=curr_teacher.curr_class)	
		for i in classroom.students.all():
			info = []
			info.append(i.user.first_name + " " + i.user.last_name) #0 is full name
			info.append(i.user.username) #1 is username
			info.append(i.points) #2 is points
			info.append(i.dollars) #3 is dollars
			student_list.append(info)
		context["Students"] = student_list
		context["CurrClassName"] = classroom.name

	CreateContext()
	#maybe change to just Create and Update later -> you're changing more than just Context
	def UpdateContext():	
		for i in curr_teacher.classrooms.all():
			if i.name not in class_names:
				class_names.append(i.name)
		context["Classes"] = class_names
		#Updates current class if changed on top-right selection box
		for i in class_names:
			if request.GET.get(i):
				curr_teacher.curr_class = i
				curr_teacher.save()
		listed_users=[]
		#student_list variable is created in CreateContext()
		for i in student_list:
			listed_users.append(i[0])
		for i in classroom.students.all():
			info = []
			info.append(i.user.first_name + " " + i.user.last_name) #0 is full name
			info.append(i.user.username) #1 is username
			info.append(i.points) #2 is points
			info.append(i.dollars) #3 is dollars
			if i.user.username not in listed_users:
				student_list.append(info)
		context["Students"] = student_list
		context["CurrClassName"] = classroom.name

	if request.GET.get("goto"):
		class_name=request.REQUEST.get("selectclass")
		curr_teacher.curr_class = class_name
		curr_teacher.save()
		return HttpResponseRedirect("/teacher/home")

	if request.GET.get("add_point_btn"):
		student_username = request.REQUEST.get("select")
		if student_username != "":
			student_user = User.objects.get(username=student_username)
			student = Student.objects.get(user=student_user) 
			student.points = student.points + 1
			student.update()
			student.save()
			UpdateContext()
			return HttpResponseRedirect("/teacher/manage-classes")
		else:
			#empty error here
			return HttpResponseRedirect("/teacher/manage-classes")
		
	if request.GET.get("remove_point_btn"):
		student_username = request.REQUEST.get("select")
		if student_username != "":
			student_user = User.objects.get(username=student_username)
			student = Student.objects.get(user=student_user)
			if student.points == 0:
				student.dollars = student.dollars - 1
				student.points = 9
			else:
				student.points = student.points - 1
			student.update()
			student.save()
			UpdateContext()
			return HttpResponseRedirect("/teacher/manage-classes")
		else:
			#empty error here
			return HttpResponseRedirect("/teacher/manage-classes")

	if request.GET.get("add_dollar"):
		student_username = request.REQUEST.get("select")
		if student_username != "":
			student_user = User.objects.get(username=student_username)
			student = Student.objects.get(user=student_user) 
			student.dollars = student.dollars + 1
			student.save()
			UpdateContext()
			return HttpResponseRedirect("/teacher/manage-classes")
		else:
			#empty error here
			return HttpResponseRedirect("/teacher/manage-classes")
		
	if request.GET.get("remove_dollar"):
		student_username = request.REQUEST.get("select")
		if student_username != "":
			student_user = User.objects.get(username=student_username)
			student = Student.objects.get(user=student_user) 
			student.dollars = student.dollars - 1
			student.save()
			UpdateContext()
			return HttpResponseRedirect("/teacher/manage-classes")
		else:
			#empty error here
			return HttpResponseRedirect("/teacher/manage-classes")
		

	if request.GET.get("add_class_btn"):
		#Class: 
			#mapped under teacher
			#Has: name, class_num, students(MTM), teams Good Deeds, PRs, Rewards, SRs <- last 5 all MTM
		name = request.REQUEST.get("new_classname")
		if curr_teacher.classrooms.filter(name=name).exists():
			context["Error"] = "Class name already taken"
			return render(request, "TeacherManageClass.html", context)
		else:
			new_class = Classroom.objects.create(name=name)
			new_class.save()
			curr_teacher.classrooms.add(new_class)
			curr_teacher.save()
			return render(request, "TeacherManageClass.html", context)

	if request.GET.get("add_student_btn"):
		f_name = request.REQUEST.get("firstname")
		l_name = request.REQUEST.get("lastname")
		d_password = request.REQUEST.get("defaultpassword")
		student_id = request.REQUEST.get("studentusername")
		points = request.REQUEST.get("points")
		if User.objects.filter(username=student_id).exists():
			context["Error"] = "Username already taken"
			return render(request, "TeacherManageClass.html", context)
		else:
			studentuser = User.objects.create(username=student_id, first_name=f_name, last_name=l_name, password=d_password)
			newstudent = Student(user=studentuser)
			newstudent.points = points
			newstudent.save()
			curr_teacher.students.add(newstudent)
			curr_teacher.save()
			classroom = Classroom.objects.get(name=curr_teacher.curr_class)
			classroom.students.add(newstudent)
			classroom.save()
			UpdateContext()
			return HttpResponseRedirect("/teacher/manage-classes")

	if request.GET.get("delete_btn"):
		x = request.REQUEST.get("select")
		user = User.objects.get(username=x)
		studentuser = Student.objects.get(user=user)
		#maybe raise are you sure modal later
		studentuser.delete()
		user.delete()
		UpdateContext()
		return HttpResponseRedirect("/teacher/manage-classes")

	if request.GET.get("move"):
		selected_student_username = request.REQUEST.get("select")
		classname = request.GET.get("move")
		print(request.GET.get("move"))
		end_class = Classroom.objects.get(name=classname)
		if selected_student_username != "":
			studentuser = User.objects.get(username=selected_student_username)
			student = Student.objects.get(user=studentuser)
			start_class = student.classroom_set.all()[0]
			start_class.students.remove(student)
			start_class.save()
			end_class.students.add(student)
			end_class.save()
			UpdateContext()
			return HttpResponseRedirect("/teacher/manage-classes")
		else:
			#Select student error
			return HttpResponseRedirect("/teacher/manage-classes")


	if request.GET.get("remove"):
		classname = request.GET.get("remove")
		delete_class = Classroom.objects.get(name=classname)
		for i in delete_class.students.all():
			i.user.delete()
#		delete_class.students.all().delete()
		delete_class.teams.all().delete()
		delete_class.GDs.all().delete()
		delete_class.Rewards.all().delete()
		delete_class.PRs.all().delete()
		delete_class.SRs.all().delete()
		delete_class.delete()
		teacher.curr_class = teacher.classrooms.all()[0].name
		teacher.save()
		return HttpResponseRedirect("/teacher/manage-classes")


	return render(request, "TeacherManageClass.html", context)

def logout_func(request):
	if request.GET.get("logout"):
		logout(request)
		return Login(request)

	#Initialize function should get data for variables. Variable definition still needs to happen here
	#NAMING LENGEND
	#Variables on every page - teacher, current classroom
		#teacher = teacher
		#current classroom = classroom
		#attributes = object._name 
			#name
			#username
			#points 
	#Variables for manage class - same as above
	#Variables for home - Student list, Team list 
	#Variables for GD List - GDs
	#Variables for Rewards - Rewards
	#Variables for Spendbox - Spend Requests
	#Variables for Request box - Point Requests
	#Variables for settings - username, password

	#MODEL MAPPING
	#Class: 
		#mapped under teacher
		#Has: name, class_num, students(MTM), teams Good Deeds, PRs, Rewards, SRs <- last 5 all MTM
	#Student: created on teacher home page, mapped under classroom(MTM), mapped under teacher(MTM)
		#Has: User (OTO), points, Requests (MTM), Spend Requests (MTM), Captain (T/F), teacher_user(teacher username), class_name
			

def get_teacher(request):
	user = request.user
	teacher = Teacher.objects.get(user=user)
	return teacher

def get_classroom(request):
	user = request.user
	teacher = get_teacher(request)
	name = teacher.curr_class
	classroom = Classroom.objects.get(name=name)
	return classroom


#STUDENT USERS TO IMPORT
point_list = [4, 10, 8, 8, 8, 4, 2, 6, 4, 4, 4, 0, 0, 0, 6, 8, 8, 10, 2, 0, 0]
username_list = ['erni12322',
 'bollocks',
 'Valcupcake',
 'Felipitote:)',
 'Ando',
 'nat0512',
 'gaby_rosales',
 'elivs',
 'diego_flowers',
 'fergoncor',
 'anuarllz',
 'marianaverdejo',
 'Santiago',
 'lors',
 'boli',
 'moru_rogel',
 'Fer-a',
 'Eric00',
 "seb's",
 'LuisaFer',
 'Isabelmomo']
fname_list = ['Erni :)',
 'Celso',
 'Valeria',
 'Felipe',
 'Andrea',
 'natalia',
 'gabriela',
 'Elisa',
 'Diego',
 'Fernando',
 'Anuar',
 'Mariana',
 'Santiago',
 'Lorena',
 'Lolina',
 'Moru',
 'Fernanda',
 'Erick',
 'Sebastian',
 'Luisa',
 'Isabel']
lname_list = [u'Anaya',
 u'Serna Klock',
 u'Ruiz',
 u'Niembro',
 u'Alonso',
 u'pati\xf1o',
 u'rosales',
 u'Villagordoa',
 u'Flores ',
 u'Gonzales',
 u'LLamas',
 u'Verdejo',
 u'Perez',
 u'Villasana',
 u'Schietekat',
 u'Rogel',
 u'Nava',
 u'Martinez',
 u'Sanchez',
 u'Salda\xf1a',
 u'Morales']

#username_list
#point_list
#fname_list
#lname_list

#	for i in range(len(username_list)):
	# 	print(username_list[i])
	# 	print(fname_list[i])
	# 	print(lname_list[i])
	# 	print(point_list[i])
	# 	new_user = User.objects.get(username=username_list[i], password="default")
	# 	#new_user.save()
	# 	#new_student = Student(user=new_user)
	# 	#new_student.points = point_list[i]
	# 	new_student = Student.objects.get(user=new_user)
	# 	#classroom.students.add(new_student)
	# 	#classroom.save()
	#	change_user = User.objects.get(username=username_list[i])
	#	change_user.first_name = fname_list[i]
	#	change_user.last_name = lname_list[i]
	#	change_user.save()


# Create your views here.
@user_passes_test(teacher_check)
def TeacherHome(request):
	logout_func(request)
	user = request.user
		# teacher = Teacher.objects.get(user=user)
		# all_classrooms = teacher.classrooms.all()
		# classroom_name = teacher.curr_class
		# classroom = Classroom.objects.get(name=classroom_name)
		# students = classroom.students.all()
		# GDs = classroom.GDs.all()
		# rewards = classroom.Rewards.all()
		# PRs = classroom.PRs.all()
		# SRs = classroom.SRs.all()
		# teams = classroom.teams.all()
	ref_dict = teacher_info(user)
	teacher = ref_dict["teacher"]
	teacher_classes = ref_dict["all_classrooms"]
	classroom_name = ref_dict["classroom_name"]
	classroom = ref_dict["classroom"]
	students = ref_dict["students"]
	GDs = ref_dict["GDs"]
	rewards = ref_dict["rewards"]
	PRs = ref_dict["PRs"]
	SRs = ref_dict["SRs"]
	teams = ref_dict["teams"]
	classroom.save()

	context = {}
	context['Name'] = user.first_name
	teacher_classroom_names = []
	for i in teacher_classes:
		teacher_classroom_names.append(i.name)
	#CONTEXT FUNCTIONS
	student_list = []
	context['Classes'] = ClassroomContext(user, "")


	if(request.GET.get("selectclass")):
		class_name = request.REQUEST.get("selectclass")
		context['Classes'] = ClassroomContext(user, class_name)
		#selected_class = Classroom.objects.get(name=class_name)
		teacher.curr_class = class_name
		teacher.save()
		return HttpResponseRedirect('/teacher/home')

	if teacher.curr_class == "":
		teacher.curr_class = context["Classes"][0]
		teacher.save()
	else:
		context["Classes"] = ClassroomContext(user, teacher.curr_class)
	for i in classroom.students.all():
		i.update()

	def StudentListContext():
		for i in classroom.students.all():
			i.update()
			i.save()
			student_info = []
			student_info.append(i.user.username) #0 is username
			student_info.append(i.user.first_name + " " + i.user.last_name) #1 is full name
			student_info.append(i.user.first_name) #2 is first name
			student_info.append(i.user.last_name) #3 is last name
			student_info.append(i.points) #4 is points
#			dollars = (i.points - (i.points % 10))/10
#			dollars = float(i.points)/10
			student_info.append(i.dollars) #5 is dollars
			student_list.append(student_info)

	def UpdateContextStudents():
		a = classroom.students.all()
		username_check = []
		for x in student_list:
			username_check.append(x[0])
		if len(a) == 0:
			return None
		for i in a:
			if i.user.username not in username_check:
				i.save()
				student_info = []
				student_info.append(i.user.username) #0 is username
				student_info.append(i.user.first_name + " " + i.user.last_name) #1 is full name
				student_info.append(i.user.first_name) #2 is first name
				student_info.append(i.user.last_name) #3 is last name
				student_info.append(i.points) #4 is points
				student_info.append(i.dollars) #5 is dollars
				student_list.append(student_info)

	if classroom.students.all():
		StudentListContext()
		context['Students'] = student_list
	
	if(request.GET.get('add_student_btn')):
		f_name = request.REQUEST.get("firstname")
		l_name = request.REQUEST.get("lastname")
		d_password = request.REQUEST.get("defaultpassword")
		studentusername = request.REQUEST.get("studentusername")
		points = request.REQUEST.get("points")
		if User.objects.filter(username=studentusername).exists():
			context["UsernameError"] = "This username is taken"
		else:
			#Student: created on teacher home page, mapped under classroom(MTM), mapped under teacher(MTM)
				#Has: User (OTO), points, Requests (MTM), Spend Requests (MTM), Captain (T/F), teacher_user(teacher username), class_name
			new_user = User.objects.create_user(username=studentusername, first_name=f_name, last_name=l_name, password=d_password)
			new_user.save()

			new_student = Student(user=new_user)
			new_student.points = points 
			new_student.teacher_user = teacher.user.username #maps teacher's username as string
			new_student.class_name = classroom.name #maps class name as string
			new_student.save()

			classroom.students.add(new_student)
			print(classroom.name)
			classroom.save()

			teacher.students.add(new_student)
			teacher.save()
			return HttpResponseRedirect("/teacher/home")
	#ADD/REMOVE POINTS AND DOLLARS BUTTONS START HERE 
	if(request.GET.get("givepoint")):
		student_list = request.GET.getlist("select")
		point_add = request.REQUEST.get("point_value")
		if point_add != "" and len(student_list) > 0:
			for i in student_list:
				point_username = i
				point_user = User.objects.get(username=point_username)
				point_student = Student.objects.get(user=point_user)
				point_student.points = point_student.points + int(point_add)
				point_student.update()
				point_student.save()
			return HttpResponseRedirect("/teacher/home")
		else:
			return HttpResponseRedirect("/teacher/home")

#		print("give point test")
#		print(request.REQUEST.get("select"))
		# if request.REQUEST.get("select") != "":
		# 	point_username = request.GET.get("select")
		# 	print("request from select")
		# 	print(point_username)
		# 	point_user = User.objects.get(username=point_username)
		# 	point_student = Student.objects.get(user=point_user)
		# 	point_student.points = point_student.points + 1
		# 	point_student.update()
		# 	point_student.save()
		# 	return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("removepoint")):
		student_list = request.GET.getlist("select")
		point_add = request.REQUEST.get("point_value")
		if point_add != "" and len(student_list) > 0:
			for i in student_list:
				point_username = i
				point_user = User.objects.get(username=point_username)
				point_student = Student.objects.get(user=point_user)
				point_student.points = point_student.points - int(point_add)
				point_student.update()
				point_student.save()
			return HttpResponseRedirect("/teacher/home")
		else:
			return HttpResponseRedirect("/teacher/home")
		# if request.REQUEST.get("select") != "":
		# 	point_username = request.REQUEST.get("select")
		# 	point_user = User.objects.get(username=point_username)
		# 	point_student = Student.objects.get(user=point_user)
		# 	if point_student.points == 0:
		# 		point_student.points = 9
		# 		point_student.dollars = point_student.dollars - 1
		# 		point_student.save()
		# 	else:
		# 		point_student.points = point_student.points - 1
		# 		point_student.save()
		# 	return HttpResponseRedirect("/teacher/home")
		# else:
		# 	return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("givedollar")):
		student_list = request.GET.getlist("select")
		dollar_change = request.REQUEST.get("dollar_value")
		if dollar_change != "" and len(student_list) > 0:
			for i in student_list:
				point_username = i
				point_user = User.objects.get(username=point_username)
				point_student = Student.objects.get(user=point_user)
				point_student.dollars = point_student.dollars + int(dollar_change)
				point_student.update()
				point_student.save()
			return HttpResponseRedirect("/teacher/home")
		else:
			return HttpResponseRedirect("/teacher/home")
		# if request.REQUEST.get("select") != "":
		# 	point_username = request.REQUEST.get("select")
		# 	point_user = User.objects.get(username=point_username)
		# 	point_student = Student.objects.get(user=point_user)
		# 	point_student.dollars = point_student.dollars + 1
		# 	point_student.save()
		# 	return HttpResponseRedirect("/teacher/home")
		# else:
		# 	return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("removedollar")):
		student_list = request.GET.getlist("select")
		dollar_change = request.REQUEST.get("dollar_value")
		if dollar_change != "" and len(student_list) > 0:
			for i in student_list:
				point_username = i
				point_user = User.objects.get(username=point_username)
				point_student = Student.objects.get(user=point_user)
				point_student.dollars = point_student.dollars + int(dollar_change)
				point_student.update()
				point_student.save()
			return HttpResponseRedirect("/teacher/home")
		else:
			return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("edit_btn")):
		edit_username = request.REQUEST.get("select")
		points_user = User.objects.get(username=edit_username)
		points_student = Student.objects.get(user = points_user)
		if(edit_username):
			newpoints = int(request.REQUEST.get("cust_val"))
			newfname = request.REQUEST.get("new_fname")
			newlname = request.REQUEST.get("new_lname")			
			if newpoints != "":
				points_student.points = newpoints
				points_student.reset()
				points_student.save()
			if newfname != "":
				points_user.first_name = newfname
				points_user.save()				
				points_student.save()
			if newlname != "":
				points_user.last_name = newlname
				points_user.save()				
				points_student.save()
		return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("delete_btn")):
		del_username = request.REQUEST.get("select")
		del_user = User.objects.get(username=del_username)
		del_student = Student.objects.get(user = del_user)
		del_student.delete()
		del_user.delete()
		return HttpResponseRedirect("/teacher/home")

	#TEAMS START HERE
	teams = classroom.teams.all()
	for i in teams:
		i.update()
		i.save()
	if(request.GET.get("teamcreate")):
		#Team: mapped under classroom
			#Has: members(MTM Students), teacher(str username), points, captain_username
		new_name = request.REQUEST.get("team_name")		
		if new_name != "":
			if classroom.teams.filter(name=new_name).exists():
				context["TeamError"] = "This team name is taken"
				return HttpResponseRedirect("/teacher/home")
			else:
				new_team = Team(name=new_name)
				new_team.save()
				classroom.teams.add(new_team)
				classroom.save()
		return HttpResponseRedirect("/teacher/home")
	
	#CREATING CONTEXT FOR TEAMS

	def TeamContext():
		output = []
		for i in teams:
			row = []
			row.append(i.name) #0 is name
			row.append(i.pk) #1 is ID
			team_student_names = ""
			students = i.members.all()
			team_captain = ""
			captain_username = i.captain_username

			if i.captain_username != "":
				if User.objects.filter(username=captain_username).exists():
					captain = User.objects.get(username=captain_username)
					team_captain = captain.first_name + " " + captain.last_name
					for x in students:
						name = x.user.first_name + " " + x.user.last_name
						if x.captain == False:
							team_student_names = team_student_names + ", " + name
			else:
				if i.members.count() > 1:
					for x in students:
						if x.captain == False:
							name = x.user.first_name + " " + x.user.last_name
							if x == students[0]:
								team_student_names = name
							else:
								team_student_names = team_student_names + ", " + name
			if i.members.count() == 1:
				if students[0].captain == False:
					team_student_names = students[0].user.first_name + " " + students[0].user.last_name
				if students[0].captain == True:
					team_captain = students[0].user.first_name + " " + students[0].user.last_name + " (Cpt.)"

			row.append(team_student_names) #2 is team members
			row.append(team_captain) #3 is team captain
			row.append(i.dollars) # 4 is dollars
			row.append(i.points) #5 is team points
			output.append(row)
		return output

	context["Teams"] = TeamContext()

	if(request.GET.get("teamadd")):
		team_select = request.REQUEST.get("selectteam")
		team_add = Team.objects.get(name=team_select)
		add_username = request.REQUEST.get("select")
		#team_add.add_student(add_username)
		user = User.objects.get(username=add_username)
		student = Student.objects.get(user=user)
		team_add.members.add(student)
		team_add.points = team_add.points + student.points
		team_add.dollars = team_add.dollars + student.dollars
		team_add.update()
		team_add.save()
		print(team_add.members.all())
		return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("delete_team")):
		team_delete_name = request.REQUEST.get("selectteam")
		for i in teams:
			if i.name == team_delete_name:
				team_delete = i
		x = team_delete.members.all()
		for i in x:
			i.captain = False
			i.save()
		team_delete.delete()
		return HttpResponseRedirect("/teacher/home")

	class_students = classroom.students.all()

	if(request.GET.get("edit_team")):
		edit_team_name = request.REQUEST.get("selectteam")
		if classroom.teams.filter(name=edit_team_name).exists():
			edit_team = classroom.teams.get(name=edit_team_name)
			team_student_list = []
			for x in edit_team.members.all():
				student_info = []
				student_info.append(x.user.first_name + " " + x.user.last_name) #0 is full name
				student_info.append(x.user.username) #1 is username
				student_info.append(x.points) #2 is points
				student_info.append(x.captain) #3 is captain status 
				team_student_list.append(student_info)
			unassigned_students = []
			for x in class_students:
				student_info = []
				if not x.team_set.all():
					student_info.append(x.user.first_name + " " + x.user.last_name) #0 is full name
					student_info.append(x.user.username) #1 is username
					student_info.append(x.points) #2 is points
					unassigned_students.append(student_info)
			if unassigned_students == []:
				context["NoUnassigned"] = ["All students are already on teams"]
			else:
				context["Unassigned"] = unassigned_students
			context["TeamMembers"] = team_student_list
			teacher.curr_team = edit_team_name
			teacher.save()
			return render(request, "TeacherHomeModal.html", context)

	#This is in the modal box to add a team member
	if(request.GET.get("edit_team_add")):
		member_id = request.REQUEST.get("selectteammember")
		add_user = User.objects.get(username=member_id)
		add_student = Student.objects.get(user=add_user)
		add_to_team = teams.get(name=teacher.curr_team)
		add_to_team.members.add(add_student)
		add_to_team.points = add_to_team.points + add_student.points
		add_to_team.dollars = add_to_team.dollars + add_student.dollars
		add_to_team.convert()
		add_to_team.save()
		return HttpResponseRedirect("/teacher/home")



	if(request.GET.get("team_captain")):
		member_id = request.REQUEST.get("selectteamcaptain")
		captain_user = User.objects.get(username=member_id)		
		captain_student = Student.objects.get(user=captain_user)
		captain_team = captain_student.team_set.all()[0]
		for i in captain_team.members.all():
			i.captain = False
			i.save()
		captain_student.captain = True
		captain_student.save()
		captain_team.captain_username = captain_user.username
		captain_team.save()
		return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("team_remove")):
		member_id = request.REQUEST.get("select_from_members")
		member_user = User.objects.get(username=member_id)		
		remove_student = Student.objects.get(user=member_user)
		remove_from_team = remove_student.team_set.all()[0]
		remove_from_team.members.remove(remove_student)
		remove_from_team.save()
		return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("close")):
		return HttpResponseRedirect("/teacher/home")

	return render(request, "TeacherHome.html", context)

@user_passes_test(teacher_check)
def GoodDeeds(request):
	if request.GET.get("logout"):
		logout(request)
		return Login(request)
	
	user = request.user
	ref_dict = teacher_info(user)
	teacher = ref_dict["teacher"] # teacher = Teacher.objects.get(user=user)
	teacher_classes = ref_dict["all_classrooms"] # all_classrooms = teacher.classrooms.all()
	classroom_name = ref_dict["classroom_name"] # classroom_name = teacher.curr_class
	classroom = ref_dict["classroom"] # classroom = Classroom.objects.get(name=classroom_name)
	students = ref_dict["students"] # students = classroom.students.all()
	GDs = ref_dict["GDs"] # GDs = classroom.GDs.all()
	rewards = ref_dict["rewards"] # rewards = classroom.Rewards.all()
	PRs = ref_dict["PRs"] # PRs = classroom.PRs.all()
	SRs = ref_dict["SRs"] # SRs = classroom.SRs.all()
	teams = ref_dict["teams"] # teams = classroom.teams.all()
	
	context = {}
	teacher_classroom_names = []
	for i in teacher_classes:
		teacher_classroom_names.append(i.name)
	context['Classes'] = ClassroomContext(user, "")


	if(request.GET.get("selectclass")):
		class_name = request.REQUEST.get("selectclass")
		context['Classes'] = ClassroomContext(user, class_name)
		#selected_class = Classroom.objects.get(name=class_name)
		teacher.curr_class = class_name
		teacher.save()
		return HttpResponseRedirect('/teacher/good-deeds')

	if teacher.curr_class == "":
		teacher.curr_class = context["Classes"][0]
		teacher.save()
	else:
		context["Classes"] = ClassroomContext(user, teacher.curr_class)

	GD_context = []
	for i in GDs:
		row = []
		row.append(i.name)
		row.append(i.cost) # 1 is points
		row.append(str(i.pk)) # 2 is PK ID
		GD_context.append(row)
	context["GDs"] = GD_context


	if(request.GET.get('enter-deed-btn')):
		cost_ = request.REQUEST.get("value")
		name_ = request.REQUEST.get("gdname")
		new_GD = GoodDeed(name=name_, cost=cost_)
		new_GD.save()
		classroom.GDs.add(new_GD)
		classroom.save()
		return HttpResponseRedirect("/teacher/good-deeds")


	if(request.POST.get("gdedit")):
		check_list = request.POST.getlist("gd")
		new_name = request.POST.get("editname")
		new_points = request.POST.get("editpoint")
		if len(check_list) > 1:
			context["OneOnly"] = "You can only edit one Good Deed at a time!"
			return HttpResponseRedirect("/teacher/good-deeds")
		else:
			i = int(check_list[0])
			edit_gd = GoodDeed.objects.get(pk=i)
			edit_gd.name = new_name
			edit_gd.cost = new_points
			edit_gd.defined = True
			edit_gd.save()
			return HttpResponseRedirect("/teacher/good-deeds")

	if(request.POST.get("gddelete")):
		check_list = request.POST.getlist("gd")
		for i in check_list:
			print("this is in check list")
			print(i)
			print("this is end of check check_list")
			del_gd = GoodDeed.objects.get(pk=i)
			del_gd.delete()
		return HttpResponseRedirect("/teacher/good-deeds")

	if(request.GET.get('delete-deed-btn')):
		GDs.delete()
		return HttpResponseRedirect("/teacher/good-deeds")

	return render(request, "TeacherGoodDeeds.html", context)

@user_passes_test(teacher_check)
def Rewards(request):
	user = request.user
	ref_dict = teacher_info(user)
	teacher = ref_dict["teacher"] # teacher = Teacher.objects.get(user=user)
	teacher_classes = ref_dict["all_classrooms"] # all_classrooms = teacher.classrooms.all()
	classroom_name = ref_dict["classroom_name"] # classroom_name = teacher.curr_class
	classroom = ref_dict["classroom"] # classroom = Classroom.objects.get(name=classroom_name)
	students = ref_dict["students"] # students = classroom.students.all()
	GDs = ref_dict["GDs"] # GDs = classroom.GDs.all()
	rewards = ref_dict["rewards"] # rewards = classroom.Rewards.all()
	PRs = ref_dict["PRs"] # PRs = classroom.PRs.all()
	SRs = ref_dict["SRs"] # SRs = classroom.SRs.all()
	teams = ref_dict["teams"] # teams = classroom.teams.all()
	
	if request.GET.get("logout"):
		logout(request)
		return Login(request)	
	
	context = {}
	teacher_classroom_names = []
	for i in teacher_classes:
		teacher_classroom_names.append(i.name)
	context['Classes'] = ClassroomContext(user, "")


	if(request.GET.get("selectclass")):
		class_name = request.REQUEST.get("selectclass")
		context['Classes'] = ClassroomContext(user, class_name)
		#selected_class = Classroom.objects.get(name=class_name)
		teacher.curr_class = class_name
		teacher.save()
		return HttpResponseRedirect('/teacher/rewards')

	if teacher.curr_class == "":
		teacher.curr_class = context["Classes"][0]
		teacher.save()
	else:
		context["Classes"] = ClassroomContext(user, teacher.curr_class)
	Rewards_Context = []
	
	for i in rewards:
		row = []
		row.append(i.name) #0 is name
		row.append(i.cost) #1 is cost
		row.append(i.pk) #2 is PK ID
		Rewards_Context.append(row)
	
	context["RewardsList"] = Rewards_Context

	if(request.POST.get("editrewards")):		
		check_list = request.POST.getlist("R")	
		for i in check_list:
			to_edit = Reward.objects.get(pk=i)
			to_edit.name = request.REQUEST.get("nreward")			
			to_edit.cost = request.REQUEST.get("npoint")
			to_edit.save()
			return HttpResponseRedirect("/teacher/rewards")

	
	if(request.POST.get("delete")):
		del_list = request.POST.getlist("R")
		for i in del_list:
			to_delete = Reward.objects.get(pk=i)
			to_delete.delete()
			return HttpResponseRedirect("/teacher/rewards")
	
	if(request.POST.get("addR")):
		name = request.REQUEST.get("Name")
		cost = request.REQUEST.get("Cost")
		if name != "" and cost != "":
			new_reward = Reward(name=name, cost=cost)
			new_reward.save()
			teacher.Rewards.add(new_reward)
			teacher.save()
			classroom.Rewards.add(new_reward)
			classroom.save()
			return HttpResponseRedirect("/teacher/rewards")
	
	if(request.POST.get("clear")):
		rewards.delete()
		context["RewardsList"] = []
		return HttpResponseRedirect("/teacher/rewards")


	return render(request, "TeacherRewards.html", context)

@user_passes_test(teacher_check)
def Requests(request):
	user = request.user
	ref_dict = teacher_info(user)
	teacher = ref_dict["teacher"] # teacher = Teacher.objects.get(user=user)
	teacher_classes = ref_dict["all_classrooms"] # all_classrooms = teacher.classrooms.all()
	classroom_name = ref_dict["classroom_name"] # classroom_name = teacher.curr_class
	classroom = ref_dict["classroom"] # classroom = Classroom.objects.get(name=classroom_name)
	students = ref_dict["students"] # students = classroom.students.all()
	GDs = ref_dict["GDs"] # GDs = classroom.GDs.all()
	rewards = ref_dict["rewards"] # rewards = classroom.Rewards.all()
	PRs = ref_dict["PRs"] # PRs = classroom.PRs.all()
	SRs = ref_dict["SRs"] # SRs = classroom.SRs.all()
	teams = ref_dict["teams"] # teams = classroom.teams.all()
	
	if request.GET.get("logout"):
		logout(request)
		return Login(request)	
	requests = PRs
	context = {}
	teacher_classroom_names = []
	for i in teacher_classes:
		teacher_classroom_names.append(i.name)
	context['Classes'] = ClassroomContext(user, "")


	if(request.GET.get("selectclass")):
		class_name = request.REQUEST.get("selectclass")
		context['Classes'] = ClassroomContext(user, class_name)
		teacher.curr_class = class_name
		teacher.save()
		return HttpResponseRedirect('/teacher/rewards')

	if teacher.curr_class == "":
		teacher.curr_class = context["Classes"][0]
		teacher.save()
	else:
		context["Classes"] = ClassroomContext(user, teacher.curr_class)
	identifiers = []

	for i in requests:
		identifiers.append(i.time_string)
	keys = sorted(identifiers, reverse=True)
	
	requests_context = []
	#we need student name, username, team of requester, points requested, and time created (for sorting)

	for i in requests:
		student = i.student_set.all()[0]
		student_name = student.user.first_name + " " + student.user.last_name
		student_username = student.user.username
		deed_name = i.deed_name
		dollars = i.points
		time = i.time_string
		accept = "A" + str(i.pk)
		deny = "D" + str(i.pk)
		row = []
		row.append(student_name) #0 is name
		row.append(student_username) #1 is username
		row.append(dollars) #2 is points
		row.append(deed_name) #3 is deed name
		row.append(accept) #4 is accept button code
		row.append(deny) #5 is deny button code	
		if i.team_set.all():
			team = i.team_set.all()[0]
			row.append(team.name) #6 is team name
		requests_context.append(row)
		if request.POST.get(accept):
			student.dollars = student.dollars + dollars
			student.save()
			if i.team_set.all():
				team.update_dollars()
				team.update_points()
				team.convert()
			i.delete()
			return HttpResponseRedirect('/teacher/point-requests')
		if request.POST.get(deny):
			i.delete()
			return HttpResponseRedirect('/teacher/point-requests')

	context["TableRows"] = requests_context

	if request.GET.get('update'):
		return HttpResponseRedirect('/teacher/point-requests')
	if request.GET.get("delete"):
		requests.delete()
		context["TableRows"] = []
		return HttpResponseRedirect('/teacher/point-requests')
	return render(request, "TeacherRequests.html", context)

@user_passes_test(teacher_check)
def SpendRequests(request):
	user = request.user
	ref_dict = teacher_info(user)
	teacher = ref_dict["teacher"] # teacher = Teacher.objects.get(user=user)
	teacher_classes = ref_dict["all_classrooms"] # all_classrooms = teacher.classrooms.all()
	classroom_name = ref_dict["classroom_name"] # classroom_name = teacher.curr_class
	classroom = ref_dict["classroom"] # classroom = Classroom.objects.get(name=classroom_name)
	students = ref_dict["students"] # students = classroom.students.all()
	GDs = ref_dict["GDs"] # GDs = classroom.GDs.all()
	rewards = ref_dict["rewards"] # rewards = classroom.Rewards.all()
	PRs = ref_dict["PRs"] # PRs = classroom.PRs.all()
	SRs = ref_dict["SRs"] # SRs = classroom.SRs.all()
	teams = ref_dict["teams"] # teams = classroom.teams.all()
	
	if request.GET.get("logout"):
		logout(request)
		return Login(request)	
	x = SRs
	spend_inbox = []
	index_list = []
	context = {}
	teacher_classroom_names = []
	for i in teacher_classes:
		teacher_classroom_names.append(i.name)
	context['Classes'] = ClassroomContext(user, "")


	if(request.GET.get("selectclass")):
		class_name = request.REQUEST.get("selectclass")
		context['Classes'] = ClassroomContext(user, class_name)
		#selected_class = Classroom.objects.get(name=class_name)
		teacher.curr_class = class_name
		teacher.save()
		return HttpResponseRedirect('/teacher/spend-requests')

	if teacher.curr_class == "":
		teacher.curr_class = context["Classes"][0]
		teacher.save()
	else:
		context["Classes"] = ClassroomContext(user, teacher.curr_class)
	for i in x:
		#Need reward name, team name, student requester and username
		row = []
		#SRs need to be mapped under a team
		
		
		btn_code = "S" + str(i.pk)

		row.append(i.rewardname) # 0 is reward name
		row.append("blegh") # 1 is student username
		row.append(btn_code) # 2 is button code
		
		if i.team_set.all():
			reward_type = "Team"
			row.append(reward_type) # 3 is reward type
			team = i.team_set.all()[0]
			team_name = team.name
			row.append(team_name) # 4 is team name if there is one
		if i.student_set.all():			
			student = i.student_set.all()[0]
			student_name = student.user.first_name + " " + student.user.last_name
			student_username = student.user.username
			reward_type = "Individual"
			row.append(reward_type) # 3 is reward type
			row.append(student_name) # 4 is name

		spend_inbox.append(row)

	for i in x:
		btn_code = "S" + str(i.pk)
		if request.POST.get(btn_code):
			i.delete()
			return HttpResponseRedirect('/teacher/spend-requests')
	
	context["TableRows"] = spend_inbox

	def check_buttons():
		for i in SRs:
			btn_code = "S" + str(i.pk)
			if request.POST.get(btn_code):
				i.delete()
				return HttpResponseRedirect('/teacher/requests')
	check_buttons()

	if request.GET.get("update"):
		return render(request, "TeacherSpend.html", context)

	if request.POST.get("clear"):
		SRs.delete()
		spend_inbox = []
		context["TableRows"] = spend_inbox
		return render(request, "TeacherSpend.html", context)
	
	return render(request, "TeacherSpend.html", context)

@user_passes_test(teacher_check)
def TeacherSettings(request):
	user = request.user
	ref_dict = teacher_info(user)
	teacher = ref_dict["teacher"] # teacher = Teacher.objects.get(user=user)
	teacher_classes = ref_dict["all_classrooms"] # all_classrooms = teacher.classrooms.all()
	classroom_name = ref_dict["classroom_name"] # classroom_name = teacher.curr_class
	classroom = ref_dict["classroom"] # classroom = Classroom.objects.get(name=classroom_name)
	students = ref_dict["students"] # students = classroom.students.all()
	GDs = ref_dict["GDs"] # GDs = classroom.GDs.all()
	rewards = ref_dict["rewards"] # rewards = classroom.Rewards.all()
	PRs = ref_dict["PRs"] # PRs = classroom.PRs.all()
	SRs = ref_dict["SRs"] # SRs = classroom.SRs.all()
	teams = ref_dict["teams"] # teams = classroom.teams.all()

	context = {}
	teacher_classroom_names = []
	for i in teacher_classes:
		teacher_classroom_names.append(i.name)
	context['Classes'] = ClassroomContext(user, "")


	if(request.GET.get("selectclass")):
		class_name = request.REQUEST.get("selectclass")
		context['Classes'] = ClassroomContext(user, class_name)
		#selected_class = Classroom.objects.get(name=class_name)
		teacher.curr_class = class_name
		teacher.save()
		return HttpResponseRedirect('/teacher/rewards')

	if teacher.curr_class == "":
		teacher.curr_class = context["Classes"][0]
		teacher.save()
	else:
		context["Classes"] = ClassroomContext(user, teacher.curr_class)
	if request.GET.get("logout"):
		logout(request)
		return FirstPage(request)
	user = request.user
	curr_teacher = Teacher.objects.get(user=user)
	curr_classname = curr_teacher.curr_class
	curr_class = Classroom.objects.get(name=curr_classname)
	print(request.user.username)
	if request.POST.get("usernamechange"):
		p_1 = request.POST.get("password")
		p_2 = request.POST.get("password_2")
		check_1 = (user.check_password(p_1))
		check_2 = (user.check_password(p_2))
		new_username = request.POST.get("newusername")
		print(new_username)			
		if check_1 and check_2:
			print("test")		
			if new_username != "":
				user.username = new_username
				user.save()			
	if request.POST.get("passwordchange"):
		p_1 = request.POST.get("password")
		p_2 = request.POST.get("password_2")
		check_1 = (user.check_password(p_1))
		check_2 = (user.check_password(p_2))
		if check_1 and check_2:
			print("passwords match and are correct")
			new_password = request.POST.get("newpassword")
			if new_password != "":
				user.set_password(new_password)
				user.save()
	return render(request, "TeacherSettings.html", context)

