import math
import datetime
from django.shortcuts import render
from .models import Student, Teacher, Team, Request
from django.contrib.auth.models import User
from .models import GoodDeed,  SpendRequest, Reward
from django.template import Context, Template
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

#For each student page, we need: teacher, classroom, team
	#For inbox pages, we need requests and spendrequests

def PtD(num_points):
	output = []
	remainder = num_points % 10
	#return 2-item list of number of dollars and points
	output.append((num_points - remainder)/10)
	output.append(remainder)
	return output

def DtP(dollars, points):
	output = 0
	output = dollars*10 + points
	return output

def StudentInfo(user):
	output = {}
	student = Student.objects.get(user=user)
	has_team = False
	if student.team_set.all():
		team = student.team_set.all()[0]
		has_team = True
	else:
		team = ""
		has_team = False
	classroom = student.classroom_set.all()[0]
	teacher = student.teacher_set.all()[0]
	output["student"] = student
	output["classroom"] = classroom
	output["teacher"] = teacher
	output["team"] = team
	output["has_team"] = has_team
	return output

def teacher_check(user):
	return Teacher.objects.filter(user=user).exists()

def Login(request):
	if User.objects.filter(username = "Jon").exists() == False:
		new_user = User.objects.create_user(username="Jon", password="JonTeacher")
		new_user.save()
		new_teacher = Teacher(user = new_user)
		new_teacher.save()

	context = {}
	reg_user = request.user.username
	if(request.POST.get("s-login")):
		u_name = request.REQUEST.get("username")
		p_word = request.REQUEST.get("password")
		if User.objects.filter(username=u_name).exists():
			user = User.objects.get(username=u_name)
			user.is_active = True
			user.save()		
		auth = authenticate(username=u_name, password=p_word)
		if auth:
			user.save()			
			if teacher_check(user) == False:
				login(request, auth)
				print("STUDENT LOGIN SUCCESS")
				print(request.user.username)
				return HttpResponseRedirect('/student/home')

	if (request.POST.get("t-login")):
		u_name = request.REQUEST.get("username")
		p_word = request.REQUEST.get("password")
		print(u_name)
		print(p_word)		
		if User.objects.filter(username=u_name).exists():
			user = User.objects.get(username=u_name)
			user.is_active = True
			user.save()
		auth = authenticate(username=u_name, password=p_word)
		print(auth)
		if auth:
			print("auth success")
			if teacher_check(user):
				login(request, auth)
				user.save()
				print("TEACHER LOGIN SUCCESS")
				print(request.user.username)
				return HttpResponseRedirect('/teacher/home')

	return render(request, "Login.html")


	# student = Student.objects.get(user=user)
	# team = student.team_set.all()[0]
	# clasroom = student.classroom_set.all()[0]
	# teacher = student.teacher_set.all()[0]

@login_required(login_url='http://127.0.0.1:8000/login')
def StudentHome(request):
	user = request.user
	ref_dict = StudentInfo(user)
	
	student = ref_dict["student"]
	classroom = ref_dict["classroom"]
	teacher = ref_dict["teacher"]
	has_team = ref_dict["has_team"]
	team = ref_dict["team"]

	if request.GET.get("logout"):
		logout(request)
		return Login(request)

	points = student.points
	dollars = student.dollars
	until = 10 - points

	context = {}
	context["Name"] = user.first_name + " " + user.last_name
	context["FirstName"] = user.first_name
	context["Dollars"] = dollars
	context["Points"] = points
	context["Until"] = until
	if has_team:
		context["TeamName"] = team.name
		team_avg = team.dollars
		team_total = team.points
		team_lead_display = team.score_leader()
		context["Team"] = team.name
		if team.captain_username:
			team_captain_user = User.objects.get(username=team.captain_username)
			team_captain_name = team_captain_user.first_name + " " + team_captain_user.last_name
			context["TeamCaptainDisplay"] = team_captain_name
			context["Members"] = []

		member_display = ""
		member_display_list = []
		member_count = team.members.count()
		member_rows = int(math.ceil(member_count/2))
		for i in range(member_rows):
			row_text = ""
			m_1 = team.members.all()[i*2]
			row_text = row_text + m_1.user.first_name + " " + m_1.user.last_name + " (" + str(m_1.dollars) + ", " + str(m_1.points) + ") "
			if len(team.members.all()) != i*2 + 1:
				m_2 = team.members.all()[i*2 + 1] #because this would be one more than a list of the length above
				row_text = row_text + ", " + m_2.user.first_name + " " + m_2.user.last_name + " (" + str(m_2.dollars) + ", " + str(m_2.points) + ") "
			member_display_list.append(row_text)

		for i in team.members.all():
			row = []
			member_display = member_display + (i.user.first_name + " " + i.user.last_name + " (" + str(i.dollars) + ", " + str(i.points) + ") ")
			row.append(i.user.first_name + " " + i.user.last_name) #0 is name
			row.append(i.points) #1 is points
			context["Members"].append(row)
		team_sum = DtP(team.dollars, team.points)
		team_raw_avg = team_sum/team.members.count()
		team_avg = PtD(team_raw_avg)
		team_avg_context = str(team_avg[0]) + " Dollars, " + str(team_avg[1]) + " Points"

		context["TeamPoints"] = team_total
		context["TeamAverage"] = team_avg_context
		context["TeamMemberDisplay"] = member_display_list
		context["TeamName"] = team.name
#	context["TeamHS"] = team_high_score
		context["TeamLeadingScorers"] = team_lead_display
	
	else:
		context["TeamName"] = "You are not assigned to a team yet!"


	# team_leads = team.leading_scorers() #list of 1: list of student lead scorers and 2: the high score as an integer
	# team_high_score = team_leads[1] 
	# for i in team_leads[0]: 
	# 	if len(team_leads[0]) > 1 and i != team_leads[len(team_leads - 1)]:
	# 		team_lead_display = team_lead_display + i.user.first_name + " " + i.user.last_name + " (" + str(i.dollars) + " points)" + ", "
	# 	else:
	# 		team_lead_display = team_lead_display + i.user.first_name + " " + i.user.last_name + " (" + str(i.dollars) + " points)"
	

	#CONTEXT FOR TEAM NAME
	#CONTEXT FOR TEAM MEMBERS AND POINTS
	#TEAM CONTEXT HERE

	#CLASS CONTEXT BEGINS
	context["Class_Teams"] = []
	for i in classroom.teams.all():
		row = []
		team_stats = []
		row.append(i.name) #team name - 0
		row.append(i.dollars) #team dollars - 1
		row.append(i.points) #team points - 2
		row.append(str(i.average()[0]) + " Dollars, " + str(i.average()[1]) + " Points") #team average - 3
		row.append(i.score_leader()) #score leader - 4
		context["Class_Teams"].append(row)
	return render(request, "StudentHome.html", context)

def StudentTeam(request):
	user = request.user
	ref_dict = StudentInfo(user)
	
	student = ref_dict["student"]
	classroom = ref_dict["classroom"]
	teacher = ref_dict["teacher"]
	team = ref_dict["team"]
	has_team = ref_dict["has_team"]

	if request.GET.get("logout"):
		logout(request)
		return Login(request)
	# student = Student.objects.get(user=user)
	# team = student.team_set.all()[0]
	# clasroom = student.classroom_set.all()[0]
	# teacher = student.teacher_set.all()[0]
	context = {}
	#GETTING STUDENT STATS
	context["Dollars"] = student.dollars
	context["Points"] = student.points
	#GETTING CLASS AVERAGE
	total = 0
	class_avg = 0
	for i in classroom.students.all():
		total = total + i.points
	class_avg = total/classroom.students.count()
	#GETTING TEAM AVERAGE
	if has_team:
		team_total = 0
		team_total = team.points
	else:
		context["NoTeam"] = "You are not assigned to a team yet!"
	team_avg = 0
	if team != "":
		team_avg = team.points/team.members.count()
		team_leads = team.leading_scorers() #list of 1: list of student lead scorers and 2: the high score as an integer
		team_lead_display = ""
		team_high_score = team_leads[1]
		for i in team_leads[0]:
			if len(team_leads[0]) > 1 and i != team_leads[len(team_leads - 1)]:
				team_lead_display = team_lead_display + i.user.first_name + " " + i.user.last_name + " (" + str(i.points) + " points)" + ", "
			else:
				team_lead_display = team_lead_display + i.user.first_name + " " + i.user.last_name + " (" + str(i.points) + " points)"

		team_captain_user = User.objects.get(username=team.captain_username)
		team_captain_name = team_captain_user.first_name + " " + team_captain_user.last_name
	#CONTEXT FOR TEAM NAME
		context["Team"] = team.name
	#CONTEXT FOR TEAM MEMBERS AND POINTS
		context["Members"] = []

		member_display = ""
		for i in team.members.all():
			row = []
			member_display = member_display + (i.user.first_name + " " + i.user.last_name + " (" + str(i.points) + "points)")
			row.append(i.user.first_name + " " + i.user.last_name) #0 is name
			row.append(i.points) #1 is points
			row.append(i.dollars) #2 is dollars			
			context["Members"].append(row)
		#	  	<p>{{member.0}} ({{member.2}} Dollars, {{member.1}} Points)</p>      
		#if members is odd: number of rows is + 1 / 2
		#if members is even: number of rows is / 2

		text_rows = []
		for i in team.members.all():
			row = i.user.first_name + " " + i.user.last_name + " (" + str(i.dollars) + " Dollars, " + str(i.points) + " Points)"
			text_rows.append(row)

		context["Member_Half"] = []

		if len(team.members.all()) % 2 == 0:
			for i in range(len(team.members.all())/2):
				first = text_rows[i*2]
				second = text_rows[i*2 + 1]
				context["Member_Half"].append(first + ", " + second)
		else:
			for i in range((len(team.members.all()) + 1)/2):
				if i == len(team.members.all() + 1)/2 - 1:
					context["Member_Half"].append(text_rows[i*2])
				else:
					first = text_rows[i*2]
					second = text_rows[i*2 + 1]
					context["Member_Half"].append(first + ", " + second)


		context["TeamPoints"] = team_total
		context["TeamAverage"] = team_avg
		context["TeamMemberDisplay"] = member_display
		context["TeamName"] = team.name
		context["TeamHS"] = team_high_score
		context["TeamLeadingScorers"] = team_lead_display
		context["TeamCaptainDisplay"] = team_captain_name

	#CONTEXT FOR CLASS TEAMS
	context["Class_Teams"] = []
	context["Class_Teams_2"] = []
	for i in classroom.teams.all():
		row = []
		row.append(i.name) #team name - 0
		row.append(str(i.dollars) + " Dollars, " + str(i.points) + " Points") #team points - 1
		member_names = ""
		x = i.members.all()
		if i.members.count() > 1:
			for n in x:
				if n != x[len(x) - 1]:
					member_names = member_names + n.user.first_name + " " + n.user.last_name + ", "
				else:
					member_names = member_names + n.user.first_name + " " + n.user.last_name
		elif i.members.count() == 1:
			member_names = x[0].user.first_name + " " + x[0].user.last_name
		row.append(member_names) #team members - 2
		row.append(i.average()) #team average - 3
		row.append(i.score_leader())
#		row.append(i.leading_scorers()) #team leading scorer - 4, []
		if len(context["Class_Teams"]) < 3:
			context["Class_Teams"].append(row)
		else:
			context["Class_Teams_2"].append(row)


	return render(request, "StudentTeam.html", context)


@login_required(login_url='http://127.0.0.1:8000/login')
#Show rewards (linked to classroom), team points(reverse student), individual points + dollars (linked to student)
def StudentShop(request):
	user = request.user
	ref_dict = StudentInfo(user)
	username = user.username
	student = ref_dict["student"]
	classroom = ref_dict["classroom"]
	teacher = ref_dict["teacher"]
	team = ref_dict["team"]
	captain = student.captain
	#captain = True
	# student = Student.objects.get(user=user)
	# team = student.team_set.all()[0]
	# clasroom = student.classroom_set.all()[0]
	# teacher = student.teacher_set.all()[0]
	#GETTING CLASS AVERAGE
	if request.GET.get("logout"):
		logout(request)
		return Login(request)
	
	available_rewards = classroom.Rewards.all()

	#CONTEXT STARTS HERE
	context = {}
	context["RewardsList1"] = []
	context["RewardsList2"] = []


	if student.team_set.all():
		student_team = student.team_set.all()[0]
		student_team.update()
		team_points = student_team.points
		team_dollars = student_team.dollars
		context["TeamName"] = student_team.name
		context["TeamPoints"] = team_points
		context["TeamDollars"] = team_dollars

	#captain = False
	#NORMAL SHOP CONTEXT
	for i in available_rewards:
		#modal_target = "{{reward.0}}{{reward.1}}"
		btn_class = "btn-success"
		display = []
		display.append("") #0 modal differentiator
		display.append("Purchase") #1 is button name
		display.append(i.name) #2 is name
		display.append(i.cost) #3 is cost
		display.append(i.pk) #4 is pk ID
		display.append(btn_class) #5 is button class		
		if i.cost > 1:
			display.append("Dollars")
		else:
			display.append("Dollar") #6 is cost label
		
		if not captain:
			if len(context["RewardsList1"]) < 5:
				context["RewardsList1"].append([display])
			elif len(context["RewardsList1"]) == 5:
				context["RewardsList2"].append([display])

		
		if captain:
			#modal_target = "team{{reward.0}}{{reward.1}}"
			modal="team" 
			btn_class = "btn-primary"
			captain_row = []
			captain_row.append(modal) #0 is modal diff.
			captain_row.append("Team Purchase") #1 is button name
			captain_row.append(i.name) #2 is name
			captain_row.append(i.cost) #3 is cost
			captain_row.append(i.pk) #4 is pk ID
			captain_row.append(btn_class) #5 is button class
			if i.cost > 1:
				display.append("Dollars")
			else:
				display.append("Dollar") #6 is cost label
			if len(context["RewardsList1"]) < 5:
				context["RewardsList1"].append([display, captain_row])
			elif len(context["RewardsList1"]) == 5:
				context["RewardsList2"].append([display, captain_row])


	print(available_rewards)
	print(context["RewardsList2"])			

	context["PointsAvailable"] = student.points
	context["DollarsAvailable"] = student.dollars
	context["ShopTitle"] = "Shop"

	for i in available_rewards:
		print(i.pk)
		if(request.GET.get('buy' + str(i.pk))):
			print("this is reward number " + str(i))
			item = i
			name_ = item.name
			cost_ = item.cost
			if student.dollars < cost_:
				#context["NotEnough"] = "You do not have enough points to buy this!"
				context["ShopTitle"] = "Not enough dollars!"
			else:
				new_spend = SpendRequest(rewardname=name_,student_name=username,number=0)
				new_spend.class_name = classroom.name
				new_spend.save()

				student.dollars = student.dollars - cost_
				#student.inventory.append(name_)				
				student.spendrequests.add(new_spend)
				student.save()

				teacher.Spendbox.add(new_spend)
				teacher.save()

				classroom.SRs.add(new_spend)
				classroom.save()

				return HttpResponseRedirect('/student/shop')
				print(student.inventory)
		#TEAM PURCHASE for Item i 
		if(request.GET.get("teambuy" + str(i.pk))):
			def CostSplit(amount, list_of_students):
				print("Team Purchase")
				if amount == 0:
					return None
				num_students = list_of_students.count()
				leftover = amount
				avg_cost = math.floor(amount/num_students)
				if avg_cost == 0:
					avg_cost = 1
				for i in list_of_students:
					if i.dollars >= avg_cost:
						leftover = leftover - avg_cost
						i.dollars = i.dollars - avg_cost
						i.save()
					else: 
						leftover = leftover - i.dollars
						i.dollars = 0
						i.save()
				if leftover > 0:
					CostSplit(leftover, list_of_students)
			# def SimpleCostSplit(amount, list_of_students):
			# 	if amount == 0:
			# 		return None
			# 	num_students = list_of_students.count()
			# 	leftover = amount
			# 	avg_cost = math.floor(amount/num_students)



			if student_team.dollars >= i.cost:
				print(str(student_team.dollars) + str(" - ") + str(i.cost))
		 		#student_team.dollars = student_team.dollars - i.cost		 		
				new_spend = SpendRequest(rewardname=i.name,student_name=username,number=0)
				new_spend.class_name = classroom.name
				new_spend.save()

				classroom.SRs.add(new_spend)
				classroom.save()

		 		student_team.SRs.add(new_spend)
		 		student_team.save()
		 		print("Team")
		 		print(student_team)
		 		print("Team members")
		 		print(student_team.members)
		 		team_members = student_team.members.all()
				CostSplit(i.cost, team_members)
				return HttpResponseRedirect('/student/shop')
	context["PointsAvailable"] = student.points
	context["DollarsAvailable"] = (student.points - (student.points % 10))/10
	return render(request, "StudentShop.html", context)


@login_required(login_url='http://127.0.0.1:8000/login')
def StudentInventory(request):
	user = request.user
	ref_dict = StudentInfo(user)
	student = ref_dict["student"]
	classroom = ref_dict["classroom"]
	teacher = ref_dict["teacher"]
	team = ref_dict["team"]
	has_team = ref_dict["has_team"]
	rewards = student.spendrequests.all()
	if request.GET.get("logout"):
		logout(request)
		return Login(request)

	context = {}
	context["List"] = []
	context["TeamList"] = []
	
	inventory = []

	if has_team:
		team_rewards = team.SRs.all()
		for i in team_rewards:
			row = []
			row = []
			row.append(i.pk) #0 is ID
			row.append(i.rewardname) #1 is reward name
			row.append("S" + str(i.pk)) #2 is button name
			context["TeamList"].append(row)



	for i in rewards:
		print(i.rewardname)
		row = []
		row.append(i.pk) #0 is ID
		row.append(i.rewardname) #1 is reward name
		row.append("S" + str(i.pk)) #2 is button name
		context["List"].append(row)

	if request.GET.get("update"):
		return HttpResponseRedirect('/student/inventory')
		
	return render(request, "StudentInventory.html", context)


@login_required(login_url='http://127.0.0.1:8000/login')
def StudentPointRequest(request):
	user = request.user
	ref_dict = StudentInfo(user)
	
	student = ref_dict["student"]
	classroom = ref_dict["classroom"]
	teacher = ref_dict["teacher"]
	team = ref_dict["team"]
	has_team = ref_dict["has_team"]
	studentpoints = student.points
	if request.GET.get("logout"):
		logout(request)
		return Login(request)
	GDs = classroom.GDs.all()

	dollars = student.dollars
	context = {
		"empty_error": "",
		"Points": studentpoints,
		"Dollars": dollars,
	}

	if(request.GET.get("custom-request-btn")):
		c_input = request.REQUEST.get("custom")
		n_points = request.REQUEST.get("num_points")
		if c_input != "":
			new_request = Request(custom_input=c_input, points=n_points, requester_id=studentuser.username,time_created=datetime.datetime.now())
			new_request.time_string = str(new_request.time_created)
			new_request.class_name = classroom.name
			new_request.teacher.add(teacher)
			new_request.save()
			student.requests.add(new_request)
			student.save()
			team.PRs.add(new_request)
			team.save()
			teacher.Requests.add(new_request)
			teacher.save()
		if c_input == "":
			print("empty case test")
			error = "You need to input a custom request!"
			context = {
				"empty_error": error,
			}
#	GDs = GoodDeed.objects.all()	
	context["Deeds1"] = []
	context["Deeds2"] = []
	for i in GDs:
		row = []
		row.append(i.name)
		row.append(i.cost)
		row.append(i.pk)
		if i.cost > 1:
			row.append("Dollars") # 3 is noun
		else:
			row.append("Dollar") # 3 is noun
		if len(context["Deeds1"]) < 5:
			context["Deeds1"].append(row)
		else:
			context["Deeds2"].append(row)

		print(context["Deeds1"])
		print(context["Deeds2"])

	def buttons():
		for i in context["Deeds1"]:
			index = i[2] 
			if (request.GET.get('req_' + str(index))):
				deed = GoodDeed.objects.get(pk=index)
				new_request = Request(deed_name=deed.name, points=deed.cost,time_created=datetime.datetime.now())
				new_request.time_string = str(new_request.time_created)
				new_request.class_name = classroom.name
				new_request.save()

				student.requests.add(new_request)
				student.save()
		
				if has_team:
					team.PRs.add(new_request)
					team.save()
				
				teacher.Requests.add(new_request)
				teacher.save()

				classroom.PRs.add(new_request)
				classroom.save()
		for i in context["Deeds2"]:
			index = i[2]
			if (request.GET.get('req_' + str(index))):
				deed = GoodDeed.objects.get(id_num=index)
				new_request = Request(g_deed=deed.id_num, points=n_points, requester_id=studentuser.username,time_created=datetime.datetime.now())
				new_request.time_string = str(new_request.time_created)
				new_request.class_name = classroom.name
				new_request.teacher.add(teacher)
				new_request.save()

				student.requests.add(new_request)
				student.save()

				if has_team:
					team.PRs.add(new_request)
					team.save()
				
				teacher.Requests.add(new_request)
				teacher.save()

				classroom.PRs.add(new_request)
				classroom.save()
	buttons()
	return render(request, "StudentPointRequest.html", context)


@login_required(login_url='http://127.0.0.1:8000/login')
def StudentSettings(request):
	user = request.user
	ref_dict = StudentInfo(user)
	
	student = ref_dict["student"]
	classroom = ref_dict["classroom"]
	teacher = ref_dict["teacher"]
	team = ref_dict["team"]
	user = request.user

	if request.GET.get("logout"):
		logout(request)
		return Login(request)
	
	username=request.user.username
	pword = user.password
	if request.GET.get("usernamechange"):
		p_1 = request.REQUEST.get("password")
		p_2 = request.REQUEST.get("password_2")
		check_1 = (user.check_password(p_1))
		check_2 = (user.check_password(p_2))
		if check_1 and check_2:
			print("test")		
	if request.GET.get("passwordchange"):
		p_1 = request.REQUEST.get("password")
		p_2 = request.REQUEST.get("password_2")
		check_1 = (user.check_password(p_1))
		check_2 = (user.check_password(p_2))
		if check_1 and check_2:
			print("passwords match and are correct")
			new_username = request.REQUEST.get("newusername")
			new_password = request.REQUEST.get("newpassword")
			if new_username != "":
				username = request.REQUEST.get("newusername")
				user.save()
			if new_password != "":
				user.set_password(request.REQUEST.get("newpassword"))
				user.save()
	return render(request, "StudentSettings.html")
