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


def teacher_check(user):
	return Teacher.objects.filter(user=user).exists()

def teacher_info(user):
	teacher = Teacher.objects.get(user=user)
	all_classrooms = Teacher.clasrooms.all()
	classroom_name = teacher.curr_class
	classroom = Classroom.objects.get(name=classroom_name)
	students = classroom.students.all()
	GDs = classroom.GDs.all()
	rewards = classroom.Rewards.all()
	PRs = classroom.PRs.all()
	SRs = classroom.SRs.all()
	teams = classroom.teams.all()



#MANAGE CLASSES STARTS HERE
def ManageClasses(request):
	curr_user = request.user
	curr_teacher = Teacher.objects.get(user=curr_user)
	context = {}
	context["Classes"] = []
	class_names = []
	student_list = []
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
			student_user = User.objects.get(username=x)
			student = Student.objects.get(user=student_user) 
			student.points = student.points + 1
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
			student.points = student.points - 1
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
		if x != "":
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



# Create your views here.
@user_passes_test(teacher_check)
def TeacherHome(request):
	user = request.user
	teacher_info(user)
		# all_classrooms
		# teacher = Teacher.objects.get(user=user)
		# classroom_name = teacher.curr_class
		# classroom = Classroom.objects.get(name=classroom_name)
		# students = classroom.students.all()
		# GDs = classroom.GDs.all()
		# rewards = classroom.Rewards.all()
		# PRs = classroom.PRs.all()
		# SRs = classroom.SRs.all()
		# teams = classroom.teams.all()
	logout_func(request)
	teacher_classes = teacher.classrooms.all()
	context = {}
	all_classroom_names = []
	for i in all_classrooms:
		all_classroom_names.append(i.name)
	classroom_context(context, "")
	#CONTEXT FUNCTIONS
	student_list = []


	if(request.GET.get("selectclass")):
		class_name = request.REQUEST.get("selectclass")
		classroom_context(context, class_name)
		selected_class = Classroom.objects.get(name=class_name)
		print(class_name)
		teacher.curr_class = selected_class.name
		teacher.save()
		return HttpResponseRedirect('/teacher/home')

	if teacher.curr_class == "":
		teacher.curr_class = context["Classes"][0]
		teacher.save()
	else:
		classroom_context(context, teacher.curr_class)


	def StudentListContext():
		for i in classroom.students.all():
			student_info = []
			student_info.append(i.user.username) #0 is username
			student_info.append(i.user.first_name + " " + i.user.last_name) #1 is full name
			student_info.append(i.user.first_name) #2 is first name
			student_info.append(i.user.last_name) #3 is last name
			student_info.append(i.points) #4 is points
#			dollars = (i.points - (i.points % 10))/10
			dollars = float(i.points)/10
			student_info.append(dollars) #5 is dollars
			student_list.append(student_info)

	def UpdateContextStudents():
		a = Student.objects.filter(class_name=classroom.name)
		if len(a) == 0:
			return None
		for i in a:
			student_info = []
			student_info.append(i.user.username) #0 is username
			student_info.append(i.user.first_name + " " + i.user.last_name) #1 is full name
			student_info.append(i.user.first_name) #2 is first name
			student_info.append(i.user.last_name) #3 is last name
			student_info.append(i.points) #4 is points
#			dollars = (i.points - (i.points % 10))/10
			dollars = float(i.points)/10
			student_info.append(dollars) #5 is dollars

		if student_info not in student_list:
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
			return HttpResponseRedirect('/teacher/home')
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

			UpdateContextStudents()

			return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("givepoint")):
		if request.REQUEST.get("select") != "":
			point_username = request.REQUEST.get("select")
			point_user = User.objects.get(username=point_username)
			point_student = Student.objects.get(user=point_user)
			point_student.points = point_student.points + 1
			point_student.save()
			return HttpResponseRedirect("/teacher/home")
		else:
			return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("removepoint")):
		if request.REQUEST.get("select") != "":
			point_username = request.REQUEST.get("select")
			point_user = User.objects.get(username=point_username)
			point_student = Student.objects.get(user=point_user)
			point_student.points = point_student.points + 1
			point_student.save()
			return HttpResponseRedirect("/teacher/home")
		else:
			return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("givedollar")):
		if request.REQUEST.get("select") != "":
			point_username = request.REQUEST.get("select")
			point_user = User.objects.get(username=point_username)
			point_student = Student.objects.get(user=point_user)
			point_student.points = point_student.points + 10
			point_student.save()
			return HttpResponseRedirect("/teacher/home")
		else:
			return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("removedollar")):
		if request.REQUEST.get("select") != "":
			print(request.REQUEST.get("select"))
			for x in User.objects.all():
				print(x.username)
			point_username = request.REQUEST.get("select")
			point_user = User.objects.get(username=point_username)
			point_student = Student.objects.get(user=point_user)
			point_student.points = point_student.points - 10
			point_student.save()
			return HttpResponseRedirect("/teacher/home")
		else:
			return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("edit_btn")):
		edit_username = request.REQUEST.get("select")
		points_user = User.objects.get(username=edit_username)
		points_student = Student.objects.get(user = points_user)
		if(edit_username):
			newpoints = request.REQUEST.get("cust_val")
			newfname = request.REQUEST.get("new_fname")
			newlname = request.REQUEST.get("new_lname")			
			if newpoints != "":
				points_student.points = newpoints
				points_user.save()				
				points_student.save()
			if newfname != "":
				points_user.first_name = newfname
				points_user.save()				
				points_student.save()
			if newlname != "":
				points_user.last_name = newlname
				points_user.save()				
				points_student.save()
		return TeacherHome(request)

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
	context["Teams"] = []
	for i in teams:
		row = []
		row.append(i.name) #0 is name
		row.append(i.pk) #1 is ID
		team_student_names = ""
		students = i.members.all()
		team_captain = ""
		captain_username = i.captain_username
		print("captain username:")
		print(captain_username)
		for x in User.objects.all():
			print(x.username)
		print("those were usernames")
		print(captain_username)

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
		row.append(i.points) #4 is team points

		context["Teams"].append(row)

	if(request.GET.get("teamadd")):
		team_select = request.REQUEST.get("selectteam")
		team_add = Team.objects.get(name=team_select)
		add_username = request.REQUEST.get("select")
		#team_add.add_student(add_username)
		user = User.objects.get(username=add_username)
		student = Student.objects.get(user=user)
		team_add.members.add(student)
		team_add.points = team_add.points + student.points
		team_add.save()

		print(team_add.members.all())
		return HttpResponseRedirect("/teacher/home")

	if(request.GET.get("delete_teams")):
		team_delete_name = request.REQUEST.get("selectteam")
		
		for i in classroom_teams:
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
		for s in class_students:
			print(s)
			print(s.team_set.all())
			if not s.team_set.all():
				info = []
				info.append(s.user.first_name + " " + s.user.last_name) #0 is full name
				info.append(s.user.username) #1 is username
				info.append(s.points) #2 is points
				unassigned_students.append(info)
			if not unassigned_students:
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

		if Team.objects.filter(name=teacher.curr_team) > 1:
			teams = Team.objects.filter(name=classroom.name)
			for i in teams:
				if i.classroom_set.all()[0] == teacher.curr_class:
					this_team = i
		else:
			this_team = Team.objects.get(name=teacher.curr_team)
		this_team.members.add(add_student)
		this_team.save()

		return HttpResponseRedirect("/teacher/home")


	if(request.GET.get("team_captain")):
		print("Team Captain:")
		print(request.REQUEST.get("selectteamcaptain"))
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

	if(request.GET.get("close")):
		return HttpResponseRedirect("/teacher/home")

	return render(request, "TeacherHome.html", context)

@user_passes_test(teacher_check)
def GoodDeeds(request):
	user = request.user
	teacher_info(user)
	# all_classrooms
	# teacher = Teacher.objects.get(user=user)
	# classroom_name = teacher.curr_class
	# classroom = Classroom.objects.get(name=classroom_name)
	# students = classroom.students.all()
	# GDs = classroom.GDs.all()
	# rewards = classroom.Rewards.all()
	# PRs = classroom.PRs.all()
	# SRs = classroom.SRs.all()
	# teams = classroom.teams.all()
	if request.GET.get("logout"):
		logout(request)
		return Login(request)
	curr_user = request.user
	curr_teacher = Teacher.objects.get(user=curr_user)
	curr_classname = curr_teacher.curr_class
	curr_class = Classroom.objects.get(name=curr_classname)
		
	print(GoodDeed.objects.count())
	for i in GoodDeed.objects.all():
		print(i.name)
	context = {}
	#Displays all defined GDs on context, creates GDs that aren't created yet
	def UpdateContext():
		output = {}
		for index in range(1, 11):
			GD_tag = "GD_" + str(index)
			P_tag = "P_" + str(index)	
			if (GoodDeed.objects.filter(id_num=index).exists()):
				a = GoodDeed.objects.get(id_num=index)
				if a.defined == True:
					print(index)
					print(a.name)
					print(a.cost)
					output[GD_tag] = a.name
					output[P_tag] = a.cost
				if a.defined == False:
					output[GD_tag] = "Enter Deed Here" 
					output[P_tag] = 0
					a.defined = False
					a.save()
			else:
				new = GoodDeed()
				new.cost = 0
				new.id_num = index
				new.defined = False
				new.name = "Good Deed " + str(index)	
				new.save()				
				output[GD_tag] = "Enter Deed Here"
				output[P_tag] = 0
		return output

	context = UpdateContext()


	if(request.GET.get('enter-deed-btn')):
		cost_ = request.REQUEST.get("value")
		name_ = request.REQUEST.get("gdname")
		for i in range(1, 11):
			gd_check = GoodDeed.objects.get(id_num=i)
			if gd_check.defined == False:
				gd_check.defined = True
				gd_check.cost = cost_
				gd_check.name = name_
				gd_check.save()

				curr_class.GDs.add(gd_check)
				curr_class.save()
			
				curr_teacher.GDs.add(gd_check)
				curr_teacher.save()
				break					
				if gd_check.defined == True and i == 10:
					context["TooMany"] = "You have too many good deeds"
					return HttpResponseRedirect("/teacher/good-deeds")
		context = UpdateContext()
		return HttpResponseRedirect("/teacher/good-deeds")


	if(request.POST.get("gdedit")):
		check_list = request.POST.getlist("gd")
		new_name = request.POST.get("editname")
		new_points = request.POST.get("editpoint")
		if len(check_list) > 1:
			#can only edit one GD error
			return HttpResponseRedirect("/teacher/good-deeds")
		else:
			i = check_list[0]
			edit_gd = GoodDeed.objects.get(id_num=i)
			edit_gd.name = new_name
			edit_gd.cost = new_points
			edit_gd.defined = True
			edit_gd.save()
			context = UpdateContext()
			return HttpResponseRedirect("/teacher/good-deeds")

	if(request.POST.get("gddelete")):
		check_list = request.POST.getlist("gd")
		for i in check_list:
			print("this is in check list")
			print(i)
			print("this is end of check check_list")
			#if (GoodDeed.objects.filter(id_num=i).exists()):
			del_gd = GoodDeed.objects.get(id_num=i)
			del_gd.name = "Enter Deed Here"
			del_gd.cost = 0
			del_gd.defined = False
			del_gd.save()
		context = UpdateContext()
		return HttpResponseRedirect("/teacher/good-deeds")

			#context = UpdateContext()
		
	context = UpdateContext()

	if(request.GET.get('delete-deed-btn')):
		GoodDeed.objects.all().delete()
		context = UpdateContext()
		return HttpResponseRedirect("/teacher/good-deeds")

	return render(request, "TeacherGoodDeeds.html", context)

@user_passes_test(teacher_check)
def Rewards(request):
	user = request.user
	teacher_info(user)
	if request.GET.get("logout"):
		logout(request)
		return Login(request)
	
	curr_user = request.user
	curr_teacher = Teacher.objects.get(user=curr_user)
	curr_classname = curr_teacher.curr_class
	curr_class = Classroom.objects.get(name=curr_classname)
	
	context = {}
	context["RewardsList"] = []
	def maxrewards():
		x = Reward.objects.count()
		return (x >= 10)

	if(request.POST.get("editrewards")):		
		check_list = request.POST.getlist("R")	
		for i in check_list:
			to_edit = Reward.objects.get(pk=i)
			to_edit.name = request.REQUEST.get("nreward")			
			to_edit.cost = request.REQUEST.get("npoint")
			to_edit.save()
	
	if(request.POST.get("delete")):
		del_list = request.POST.getlist("R")
		for i in del_list:
			to_delete = Reward.objects.get(pk=i)
			to_delete.delete()
	
	if(request.POST.get("addR")):
		name = request.REQUEST.get("Name")
		cost = request.REQUEST.get("Cost")
		if name != "" and cost != "":
			new_reward = Reward(name=name, cost=cost, id_num=0)
			new_reward.save()
			curr_teacher.Rewards.add(new_reward)
			curr_teacher.save()
			curr_class.Rewards.add(new_reward)
			curr_class.save()
	if(request.POST.get("clear")):
		Reward.objects.all().delete()
		context["RewardsList"] = []

	rewards_by_class = curr_class.Rewards.all()
	rewards_by_teacher = curr_teacher.Rewards.all()

	for i in rewards_by_teacher:
		reward = []
		reward.append(i.name) #0 is name
		reward.append(i.cost) #1 is cost
		reward.append(i.pk) #2 is django ID
		context["RewardsList"].append(reward)
	return render(request, "TeacherRewards.html", context)

@user_passes_test(teacher_check)
def Requests(request):
	user = request.user
	teacher_info(user)
	if request.GET.get("logout"):
		logout(request)
		return FirstPage(request)
	#inbox = request.session['inbox']
	#keys = sorted(inbox.keys(), reverse=True)
	#requests = Request.objects.all()
	user = request.user
	curr_teacher = Teacher.objects.get(user=user)
	curr_classname = curr_teacher.curr_class
	curr_class = Classroom.objects.get(name=curr_classname)
	requests = curr_class.PRs.all()

	identifiers = []

	for i in requests:
		identifiers.append(i.identifier)
	keys = sorted(identifiers, reverse=True)
	context = {}
	context["RequestKeys"] = []
	context["Names"] = []
	context["Deeds"] = []
	context["Points"] = []
	context["Times"] = []
	context["IDs"] = []
	context["TableRows"] = []

	def create_context(i, name, points, deed, time):
			#n = keys.index(i)
			row = []
			row.append(i + 1)
			row.append(name)
			row.append(points)
			row.append(deed)
			row.append("A" + str(i))
			row.append("D" + str(i))
			row.append(time)
			context["TableRows"].append(row)

	def update_context(i):
		for row in context["TableRows"]:
			if row[0] == i + 1:
				context["TableRows"].remove(row)
			if row[0] > i + 1:
				row[0] = row[0] - 1

	def check_btns(i, student, n_points):
		if request.POST.get("A" + str(i)):
			student.points = student.points + n_points
			student.save()
			print(student.user.first_name + "has " + str(student.points) + " points")
			#3 LEVELS OF EDITING
			#MODEL(STUDENT OBJECT)
			x = Request.objects.get(identifier=keys[i])
			x.delete()
			#REQUEST SESSION (TEACHER INBOX)
			#request.session['inbox'].pop(keys[i])
			#request.session.save()
			#CONTEXT (FRONT END HTML)
			update_context(i)
			print(context["TableRows"])
			return HttpResponseRedirect('/teacher/requests')
		if request.POST.get("D" + str(i)):
			x = Request.objects.get(identifier=keys[i])
			x.delete()
			#request.session['inbox'].pop(keys[i])
			#request.session.save()
			update_context(i)
			print(context["TableRows"])							
			return render(request, "TeacherRequests.html", context)

	#for every request in inbox, a new list is created to make a row
	for i in range(len(keys)):
		x = Request.objects.get(identifier=keys[i])
		r_username = x.requester_id
		r_user = User.objects.get(username=r_username)
		name = r_user.first_name + " " + r_user.last_name
		n_points = x.points
		deed = x.g_deed
		student = Student.objects.get(user=r_user)
		time = keys[i]


		#n_points = int(inbox[keys[i]]["Points"])
		#r_username = inbox[keys[i]]["requester_id"]
		#r_user = User.objects.get(username=r_username)
		#deed = inbox[keys[i]]["Deed"]
		print(n_points)
		check_btns(i, student, n_points)
		create_context(i, name, n_points, deed, time)

	if request.GET.get('update'):
		return HttpResponseRedirect('/teacher/requests')
	
	if request.GET.get("delete"):
		Request.objects.all().delete()
		#request.session['inbox'] = {}
		#request.session.save()
		context["TableRows"] = []
		return render (request, "TeacherRequests.html", context)

	print(context["TableRows"])

	return render(request, "TeacherRequests.html", context)

@user_passes_test(teacher_check)
def SpendRequests(request):
	user = request.user
	teacher_info(user)
	if request.GET.get("logout"):
		logout(request)
		return FirstPage(request)
	spend_inbox = []
	index_list = []
	user = request.user
	curr_teacher = Teacher.objects.get(user=user)
	curr_classname = curr_teacher.curr_class
	curr_class = Classroom.objects.get(name=curr_classname)
	x = curr_class.SRs.all()

	def create_inbox():
		for index in range(len(x)):
			row = []
			row.append(index) #0 is index
			row.append(x[index].rewardname) #1 is reward name
			row.append(x[index].studentname) #2 is student name
			row.append(x[index].username) #3 is student username 
			spend_inbox.append(row)
			print(spend_inbox)
			index_list.append(index)

	def check_buttons():
		for i in index_list:
			if request.GET.get("S" + str(i)):
				
				student_user = User.objects.get(username=spend_inbox[i][3])
				student = Student.objects.get(user=student_user)
				student.inventory.remove(spend_inbox[i][1])
				student.save()

				spend_inbox.remove(spend_inbox[i])
				request.session.save()
				
				x[i].delete()				
				index_list.remove(index_list[i])				

				reindex(i)
				print("S" + str(i) + "input received")


	def reindex(index):
		for i in spend_inbox:
			if i[0] > index:
				i[0] = i[0] - 1
		for x in index_list:
			if x > index_list:
				x = x - 1

	create_inbox()
	check_buttons()

	context = {}
	
	context["TableRows"] = spend_inbox

	print(spend_inbox)
	
	if request.GET.get("update"):
		return render(request, "TeacherSpend.html", context)

	if request.POST.get("clear"):
		SpendRequest.objects.all().delete()
		spend_inbox = []
		request.session.save()
		context["TableRows"] = spend_inbox
		return render(request, "TeacherSpend.html", context)

	
	return render(request, "TeacherSpend.html", context)

@user_passes_test(teacher_check)
def TeacherSettings(request):
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
	return render(request, "TeacherSettings.html")

