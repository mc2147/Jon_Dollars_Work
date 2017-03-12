def make_classrooms(user):
	if Teacher.objects.filter(user=user).exists():
		teacher = Teacher.objects.get(user=user)
	for i in range(1, 6):
		if Classroom.objects.filter(name="Classroom " + str(i)).exists() == False:
			x = Classroom(name="Classroom " + str(i))
			x.save()
			teacher.classrooms.add(x)
			teacher.save()
s
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
