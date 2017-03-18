from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Store, Employee, Customer, Appointment, Treatment, Offer
from .forms import (
		AppointmentByTimeForm,
		CustomerForm,
		AppointmentForm,
		AppointmentForm1,
		AppointmentForm2,
		OfferForm,
		EmployeeForm,
		TreatForm,
		CustomSearch,
	)
import timedelta
import time
import math
import datetime

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
# Create your views here.
store_id=0
Appointment_customer = 0
Appointment_schedule = '0'
Appointment_treatment = 0

def create_treat(request,id=None):
	us = Store.objects.filter(id=id)
	if not request.user.is_authenticated() or us[0].user!=request.user:
		return HttpResponseRedirect('/')
	form = TreatForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.store = Store.objects.filter(id=id)[0]
		instance.user = request.user
		instance.save()
		return HttpResponseRedirect('/appointment/'+str(id))


	context = {
		"form":form,
	    "store" : us[0],
		"form_name": "Treatment Form",
        }
	return render(request, "custom_form2.html", context)

def appointment_create(request, id=None, cid=None):
	us = Store.objects.filter(id=id)
	if not request.user.is_authenticated() or us[0].user!=request.user:
		return HttpResponseRedirect('/')
	m=[]
	msg = ''
	form1 = AppointmentForm1(request.POST or None, request.FILES or None)
	if form1.is_valid():
		instance = form1.cleaned_data
		instance1 = form1.save(commit=False)
		request.session['Appointment_treatment'] = instance1.treatment.id
		a = str(instance.get('date')).split('-')
		schedule = datetime.datetime(int(a[0]),int(a[1]),int(a[2]),int(instance.get('hour')),int(instance.get('minutes')),0)
		request.session['Appointment_schedule'] = str(schedule)[:19]
		f = Treatment.objects.filter(id=request.session['Appointment_treatment'])
		schedule_end = schedule+f[0].duration
		obj = Appointment.objects.exclude(schedule__gt=schedule_end).exclude(schedule_end__lt=schedule).filter(Employee__store__id = id)

		for each in obj:
			if each.Employee.id not in m:
				m.append(each.Employee.id)
		if m:
			c = Employee.objects.filter(store__id = id).exclude(id__in = m)
		else:
			c = Employee.objects.filter(store__id = id)
		if c:
			return HttpResponseRedirect('/appointment/'+str(id)+'/set/'+str(cid)+'/')
		else:
			msg = "No Employee is free"
	form1.fields['treatment'].queryset = Treatment.objects.filter(store__id = id)
	context = {
			"form_name": "appointment",
			"form1": form1,
			"msg" : msg,
			"store":us[0],
		}
	return render(request, "custom_form.html", context)

def appointment_store(request, id=None):
	us = Store.objects.filter(id=id)
	if not request.user.is_authenticated() or us[0].user!=request.user:
		return HttpResponseRedirect('/')
	instance = get_object_or_404(Store, id=id)
	prof = Appointment.objects.filter(schedule__gt = datetime.datetime.now().replace(day=1).replace(hour=0).replace(minute=0).replace(second=0), schedule__lt = datetime.datetime.now(), Employee__store__id=id)
	profit = 0
	emp = Employee.objects.filter(store__id=id, active=True)
	empc = 0
	for each in emp:
		empc += 1
	for each in prof:
		profit += each.profit

	cs = CustomSearch(request.POST or None)
	if cs.is_valid():
		s = cs.cleaned_data['contact']
		customer = Customer.objects.filter(contact=s)
		if customer:
			return HttpResponseRedirect('/appointment/'+str(id)+'/create/'+str(customer[0].id)+'/')

		return HttpResponseRedirect('/appointment/'+str(id)+'/ccreate/'+s+'/')

	appoint = Appointment.objects.filter(Employee__store__id = id).filter(schedule__gt = datetime.datetime.now())[:5]
	context = {
				"store_id":id,
				"title": instance.address,
				"profit":profit,
				"appoint" : appoint,
				"empc":empc,
				"store":us[0],
				"csearch":cs
			}
	return render(request,"store_detail.html",context)

def appointment_update_others(request, id=None, cid=None):
	us = Store.objects.filter(id=id)
	if not request.user.is_authenticated() or us[0].user!=request.user:
		return HttpResponseRedirect('/')
	instance = get_object_or_404(Appointment, id=cid)
	form = AppointmentForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()

	context = {
		"title": "Update",
		"form":form,
		"store":us[0]
	}
	return render(request, "appoint_update_others.html", context)



def appointment_delete(request, id=None, cid=None):
	us = Store.objects.filter(id=id)
	if not request.user.is_authenticated() or us[0].user!=request.user:
		return HttpResponseRedirect('/')
	instance = get_object_or_404(Appointment, id=cid)
	instance.delete()
	context={
		"message":"Appointment has been cancelled",
	}
	return HttpResponseRedirect('/appointment/'+str(id)+'/applist')

def monthly_appointment(request, id=None):
	us = Store.objects.filter(id=id)
	if not request.user.is_authenticated() or us[0].user!=request.user:
		return HttpResponseRedirect('/')
	form = AppointmentByTimeForm(request.POST or None)
	x = ""
	c = datetime.datetime.now().replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
	d = datetime.datetime.now()
	if form.is_valid():
		cd = form.cleaned_data
		c = datetime.datetime.now().replace(month = int(cd.get('months'))).replace(year = int(cd.get('year'))).replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
		if cd.get('months')!="12":
			d = datetime.datetime.now().replace(month = int(cd.get('months'))+1).replace(year = int(cd.get('year'))).replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
		else:
			d = datetime.datetime.now().replace(month = 0).replace(year = int(cd.get('year'))+1).replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
	if c > datetime.datetime.now():
		c = datetime.datetime.now().replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
		x = "Future Month : Invalid Input"
	if c.month >= datetime.datetime.now().month and c.year == datetime.datetime.now().year:
		d = datetime.datetime.now()
	prof = Appointment.objects.filter(schedule__gt = c, schedule__lt = d).filter(Employee__store__id = id)
	total = 0
	whours = datetime.timedelta(0,0,0)
	for a in prof:
		total = total + a.profit
		whours = whours + a.treatment.duration
	if whours == datetime.timedelta(0,0,0):
		whours = 'None'

	context = {
		"form":form,
		"object_list" : prof,
		"tocontrib": total,
		"whours":whours,
		"store":us[0],
		"x":x,
	}
	return render(request, "month_list.html", context)

def employee_details(request, id=None, eid=None):
	us = Store.objects.filter(id=id)
	if not request.user.is_authenticated() or us[0].user!=request.user:
		return HttpResponseRedirect('/')
	e = Employee.objects.filter(id=eid)
	emp = e[0]
	store = Store.objects.filter(id=id)
	form = AppointmentByTimeForm(request.POST or None)
	x = ""
	c = datetime.datetime.now().replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
	d = datetime.datetime.now()
	if form.is_valid():
		cd = form.cleaned_data
		c = datetime.datetime.now().replace(month = int(cd.get('months'))).replace(year = int(cd.get('year'))).replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
		if cd.get('months')!="12":
			d = datetime.datetime.now().replace(month = int(cd.get('months'))+1).replace(year = int(cd.get('year'))).replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
		else:
			d = datetime.datetime.now().replace(month = 0).replace(year = int(cd.get('year'))+1).replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
	if c > datetime.datetime.now():
		c = datetime.datetime.now().replace(day=1).replace(hour=0).replace(minute=0).replace(second=0)
		x = "Future Month : Invalid Input"
	if c.month >= datetime.datetime.now().month and c.year == datetime.datetime.now().year:
		d = datetime.datetime.now()
	app = Appointment.objects.filter(schedule__gt = c, schedule__lt = d).filter(Employee__store__id = id).filter(Employee__id=eid)
	total = 0
	whours = datetime.timedelta(0,0,0)
	for a in app:
		total = total + a.profit
		whours = whours + a.treatment.duration
	if whours == datetime.timedelta(0,0,0):
		whours = 'None'

	context={
		"emp":emp,
		"store":store[0],
		"tocontrib": total,
		"whours":whours,
		"app":app,
		"filter":form,
		"x":x
	}
	return render(request, "empdet.html", context)
