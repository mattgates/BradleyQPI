from flask import Flask, render_template, redirect, url_for, request, flash, session, logging, jsonify, make_response
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms import ValidationError
from markupsafe import escape
import time
import hashlib
import datetime
import requests
import json
import emails
import texts
import phonenumbers

app = Flask(__name__)


app.secret_key = "test"

ACCESS = {
    "guest": 0,
    "unverified": 1,
    "user": 2,
    "admin": 3
}


class User():
    def __init__(self, employee_id, position, first_name, last_name, part_time_ind, email, phone, access=ACCESS["guest"]):
        self.id_employee = employee_id
        self.access = access
        self.position = position
        self.first_name = first_name
        self.last_name = last_name
        self.part_time_ind = part_time_ind
        self.email = email
        self.phone = phone


def getUser():

    username = ""
    user = ""

    if 'username' in session:
        username = int(escape(session['username']))
        response = requests.get(
            "http://localhost:5000/getuserdata/" + str(username))

        user = User(username, response.json()["role_name"], response.json()["first_name"], response.json()[
                    "last_name"], response.json()["part_time_ind"], response.json()["email"], response.json()["phone"], response.json()["user_type"])

        return username, user
    else:
        return "", ""


@app.route('/')
def home():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))
    if user.access == "3":
        return redirect(url_for('notifications'))

    # gets ID of shifts scheduled by employee
    shift_ids = requests.get(
        "http://localhost:5000/myshiftids/" + str(username))
    # for each ID, gets shift information
    shift_ids = shift_ids.json()
    dictOfShifts = {}
    # for each request, get information
    for i in range(len(shift_ids)):
        id_shift = str(shift_ids[i]["id_calendar"])
        shiftDesc = requests.get("http://localhost:5000/myshifts/" + id_shift)
        s = shiftDesc.json()[0]
        # create dictionary of shifts
        dictOfShifts[id_shift] = s

    return render_template('home.html', schedule=dictOfShifts, user=user)


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    # gets all shifts for a current role: eg 006
    allShifts = requests.get(
        "http://localhost:5000/getshifts/" + str(username))
    # gets ID of shifts scheduled by employee
    shift_ids = requests.get(
        "http://localhost:5000/myshiftids/" + str(username))
    # for each ID, gets shift information
    shift_ids = shift_ids.json()
    myShiftsList = []
    # for each request, get information
    for i in range(len(shift_ids)):
        id_shift = str(shift_ids[i]["id_calendar"])
        shiftDesc = requests.get("http://localhost:5000/myshifts/" + id_shift)
        s = shiftDesc.json()[0]
        # create list of shift ids
        myShiftsList.append(s['id_shift_daypart'])

    if request.method == 'POST':
        shift_id = request.form.getlist('id_shift_daypart')
        shifts = ""
        # format shift ids so they can be passed to the query
        for i in shift_id:
            shifts += i + ","
        shifts = shifts.rstrip(',')
        # posts shifts for employees with id 47
        sendShifts = requests.post(
            "http://localhost:5000/setshifts/" + str(username) + "/" + shifts)
        return redirect(url_for('schedule'))
    return render_template('schedule.html', schedule=allShifts.json(), mySchedule=myShiftsList, user=user)

# This gets the all of the employees eligible to swap with
# Corresponds to class getSwapEmp(Resource):
@app.route('/employee/<orig_shift>', methods=['GET', 'POST'])
def employee(orig_shift):

    username, user = getUser()
    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    # query to get all of the employes of same role as employee x, not working orig_shift
    result = []
    result = requests.get(
        "http://localhost:5000/getswapemp/" + str(username) + "/" + orig_shift)
    result = result.json()
    dictOfResult = {i: result[i] for i in range(0, len(result))}
    # remove duplicate employees
    newDictOfResult = {}
    for key, value in dictOfResult.items():
        if (value not in newDictOfResult.values() and dictOfResult[key]['id_employee'] != username):
            newDictOfResult[key] = value
    # return json object of all employees
    return newDictOfResult

# This gets all possible shifts of swap user
# Corresponds to class getSwapEmp(Resource):
@app.route('/newSwapShift/<employee_id>', methods=['GET', 'POST'])
def newSwapShift(employee_id):

    username, user = getUser()
    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    # gets ID of shifts scheduled by employee
    id_calendar = requests.get(
        "http://localhost:5000/getswapshiftids/" + str(username) + "/" + employee_id)
    # for each ID, gets shift information
    id_calendar = id_calendar.json()
    dictOfShifts = {}
    # for each request, get information
    for i in range(len(id_calendar)):
        id_cal = str(id_calendar[i]["id_calendar"])
        shiftDesc = requests.get(
            "http://localhost:5000/getswapshifts/" + id_cal)
        s = shiftDesc.json()[0]
        # create dictionary of shifts
        dictOfShifts[id_cal] = s
    return dictOfShifts


@app.route('/swap', methods=['GET', 'POST'])
def swap():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    # gets ID of shifts scheduled by employee
    shift_ids = requests.get(
        "http://localhost:5000/myshiftids/" + str(username))
    # for each ID, gets shift information
    shift_ids = shift_ids.json()
    dictOfShifts = {}
    # for each request, get information
    for i in range(len(shift_ids)):
        id_shift = str(shift_ids[i]["id_calendar"])
        shiftDesc = requests.get("http://localhost:5000/myshifts/" + id_shift)
        s = shiftDesc.json()[0]
        # create dictionary of shifts
        dictOfShifts[id_shift] = s
    # gets ID OF pending dropped shifts requested by employee
    pending_ids = requests.get(
        "http://localhost:5000/getpendingswapids/" + str(username))
    # for each ID, gets pending swap information
    pending_ids = pending_ids.json()
    dictOfPendingSwaps = {}
    # for each request, get information
    for i in range(len(pending_ids)):
        id_swap = str(pending_ids[i]["id_pending_swap"])
        pending_swaps = requests.get(
            "http://localhost:5000/getpendingswap/" + id_swap)
        p = pending_swaps.json()[0]
        # create dictionary of pending swap values
        dictOfPendingSwaps[id_swap] = p
    # gets ID OF approved swapped shifts requested by employee 47
    approved_ids = requests.get(
        "http://localhost:5000/getapprovedswapids/" + str(username))
    # for each ID, gets approved swap information
    approved_ids = approved_ids.json()
    dictOfApprovedSwaps = {}
    # for each request, get information
    for i in range(len(approved_ids)):
        id_swap = str(approved_ids[i]["id_pending_swap"])
        approved_swaps = requests.get(
            "http://localhost:5000/getapprovedswap/" + id_swap)
        a = approved_swaps.json()[0]
        # create dictionary of approved drop values
        dictOfApprovedSwaps[id_swap] = a

    # get email and phone number
    contact = requests.get(
        "http://localhost:5000/getemailandphone/" + str(username))
    contact = contact.json()[0]
    email = contact["email_address"]
    phone = contact["phone_number"]
    print(phone)

    if request.method == 'POST':
        # request a swap
        if request.form.get('swapShift1'):
            shift1 = request.form.getlist('swapShift1')
            employee = request.form.getlist('swapShiftEmp')
            shift2 = request.form.getlist('swapShift2')
            # posts pending swap for employee 47
            swapShiftID = requests.post(
                "http://localhost:5000/setpendingswap/" + str(username) + "/" + shift1[0] + "/" + employee[0] + "/" + shift2[0])
            swapShiftID = swapShiftID.json()[0]['id_pending_swap']
            # POST to notifications table for employee 47
            requests.post(
                "http://localhost:5000/setswapnotification/" + str(username) + "/" + str(swapShiftID))

            pending_swaps = requests.get(
                "http://localhost:5000/getpendingswap/" + str(swapShiftID))
            p = pending_swaps.json()[0]

            from_emp = p["from_id_employee"]

            to_contact = requests.get(
                "http://localhost:5000/getemailandphone/" + str(from_emp))
            to_contact = to_contact.json()[0]
            to_email = to_contact["email_address"]
            to_phone = to_contact["phone_number"]

            # send pending swap email
            shiftDate1 = p["orig_start_date"]
            shiftStart1 = p["orig_start_time"]
            shiftEnd1 = p["orig_end_time"]
            shiftDate2 = p["new_start_date"]
            shiftStart2 = p["new_start_time"]
            shiftEnd2 = p["new_end_time"]
            empName = p["first_name"] + " " + p["last_name"]
            emails.swap_emp_email(shiftDate1, shiftStart1, shiftEnd1, shiftDate2, shiftStart2, shiftEnd2, empName, to_email)

            phone_with_code = "+1" + to_phone
            if to_phone.isdigit():
                texts.swap_emp_text(shiftDate1, shiftStart1, shiftEnd1, shiftDate2, shiftStart2, shiftEnd2, empName, phone_with_code)

        # cancel swap request
        elif request.form.get('cancel_swap'):
            cancel_swap = request.form.get('cancel_swap')
            # updates pending_swap table
            requests.post(
                "http://localhost:5000/updateswaprequest/'Cancelled'/" + cancel_swap)
            # update notifications table
            requests.post(
                "http://localhost:5000/updateswapnotification/'Cancelled'/" + cancel_swap)
        # swap by shift type
        elif request.form.get("shiftToSwap"):
            shift = request.form.get("shiftToSwap")
            typeWanted = request.form.get("shiftType")
        return redirect(url_for('swap'))
    return render_template('swap.html', schedule=dictOfShifts, pendingSwaps=dictOfPendingSwaps, approvedSwaps=dictOfApprovedSwaps, user=user)


@app.route('/drop', methods=['GET', 'POST'])
def drop():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    # gets ID of shifts scheduled by employee
    shift_ids = requests.get(
        "http://localhost:5000/myshiftids/" + str(username))
    # for each ID, gets shift information
    shift_ids = shift_ids.json()
    dictOfShifts = {}
    # for each request, get information
    for i in range(len(shift_ids)):
        id_shift = str(shift_ids[i]["id_calendar"])
        shiftDesc = requests.get("http://localhost:5000/myshifts/" + id_shift)
        s = shiftDesc.json()[0]
        # create dictionary of shifts
        dictOfShifts[id_shift] = s

    # gets ID OF pending dropped shifts requested by employee
    pending_ids = requests.get(
        "http://localhost:5000/getpendingdropids/" + str(username))
    # for each ID, gets pending drop information
    pending_ids = pending_ids.json()
    dictOfPendingDrops = {}
    for i in range(len(pending_ids)):
        id_drop = str(pending_ids[i]["id_pending_drop"])
        pending_drops = requests.get(
            "http://localhost:5000/getpendingdrop/" + id_drop)
        p = pending_drops.json()[0]
        # create dictionary of pending drop values
        dictOfPendingDrops[id_drop] = p

    # gets ID OF approved dropped shifts requested by employee 47
    approved_ids = requests.get(
        "http://localhost:5000/getapproveddropids/" + str(username))
    # for each ID, gets approved drop information
    approved_ids = approved_ids.json()
    dictOfApprovedDrops = {}
    for i in range(len(approved_ids)):
        id_drop = str(approved_ids[i]["id_pending_drop"])
        approved_drops = requests.get(
            "http://localhost:5000/getapproveddrop/" + id_drop)
        a = approved_drops.json()[0]
        # create dictionary of approved drop values
        dictOfApprovedDrops[id_drop] = a

    if request.method == 'POST':
        if request.form.get('drop_shift'):
            dropped_shift = request.form.get('drop_shift')
            # drop shift for employee #47
            dropShiftID = requests.post(
                "http://localhost:5000/setpendingdrop/" + str(username) + "/" + dropped_shift)
            dropShiftID = dropShiftID.json()[0]['id_pending_drop']
            # POST to notifications table for employee 47
            requests.post(
                "http://localhost:5000/setdropnotification/" + str(username) + "/" + str(dropShiftID))

        elif request.form.get('cancel_drop'):
            cancel_shift = request.form.get('cancel_drop')
            requests.post(
                "http://localhost:5000/updatedroprequest/'Cancelled'/" + cancel_shift)
            # update notifications table
            requests.post(
                "http://localhost:5000/updatedropnotification/'Cancelled'/" + cancel_shift)
        return redirect(url_for('drop'))

    return render_template('drop.html', schedule=dictOfShifts, pendingDrops=dictOfPendingDrops, approvedDrops=dictOfApprovedDrops, user=user)


@app.route('/vacation', methods=['GET', 'POST'])
def vacation():

    username, user = getUser()
    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    # gets number of vacation days left in current year
    hours = requests.get(
        "http://localhost:5000/getvacationdays/" + str(username))
    # gets ID OF pending vacation days requested by employee 47
    pending_ids = requests.get(
        "http://localhost:5000/getpendingvacationids/" + str(username))
    # for each ID, gets pending drop information
    pending_ids = pending_ids.json()
    dictOfPendingVacations = {}
    for i in range(len(pending_ids)):
        id_drop = str(pending_ids[i]["id_pending_vacation"])
        pending_vacations = requests.get(
            "http://localhost:5000/getpendingvacation/" + id_drop)
        p = pending_vacations.json()[0]
        # create dictionary of pending drop values
        dictOfPendingVacations[id_drop] = p

    # gets ID OF approved vacations requested by employee 47
    approved_ids = requests.get(
        "http://localhost:5000/getapprovedvacationids/" + str(username))
    # for each ID, gets approved information
    approved_ids = approved_ids.json()
    dictOfApprovedVacations = {}
    for i in range(len(approved_ids)):
        id_vacation = str(approved_ids[i]["id_pending_vacation"])
        approved_vacations = requests.get(
            "http://localhost:5000/getapprovedvacation/" + id_vacation)
        a = approved_vacations.json()[0]
        # create dictionary of pending drop values
        dictOfApprovedVacations[id_vacation] = a

    if request.method == 'POST':
        if request.form.get('start_date'):
            dropped_shift = request.form.getlist('drop_shift')
            startDate = request.form.getlist('start_date')
            endDate = request.form.getlist('end_date')
            numDays = request.form.getlist('num_days')
            print(startDate, endDate)
            vacationID = requests.post(
                "http://localhost:5000/requestvacation/" + str(username) + "/" + startDate[0] + "/" + endDate[0] + "/" + numDays[0])
            vacationID = vacationID.json()[0]['id_pending_vacation']
            requests.post(
                "http://localhost:5000/setvacationnotification/" + str(username) + "/" + str(vacationID))

        elif request.form.get('cancel_vacation'):
            cancel_vacation = request.form.get('cancel_vacation')
            print(cancel_vacation)
            requests.post(
                "http://localhost:5000/updatevacationrequest/'Cancelled'/" + cancel_vacation)
            # update notifications table
            requests.post(
                "http://localhost:5000/updatevacationnotification/'Cancelled'/" + cancel_vacation)
        return redirect(url_for('vacation'))

    return render_template('vacation.html', pending_vacations=dictOfPendingVacations, scheduled_vacations=dictOfApprovedVacations, days_left=hours.json(), user=user)


@app.route('/notifications', methods=['GET', 'POST'])
def notifications():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))
    if user.access == "2":

        # POST (NEEDS TO BE FIRST)
        if request.method == 'POST':
        # Approve Swap
            if request.form.get('status_app'):
                statusApprove = request.form.get('status_app')
                id_swap = request.form.get('id_swap')
                requests.post(
                    "http://localhost:5000/updateswaprequest/'Approved'/" + str(id_swap))
                # get swap info to perform swap
                approved_swap = requests.get(
                    "http://localhost:5000/getpendingswap/" + id_swap)
                app = approved_swap.json()[0]
                to_id = app["to_id_shift_daypart"]
                from_id = app["from_id_shift_daypart"]
                from_emp = app["from_id_employee"]

                all_info = requests.get(
                    'http://localhost:5000/getapprovedswap/' + id_swap)
                a = all_info.json()[0]

                to_contact = requests.get(
                    "http://localhost:5000/getemailandphone/" + str(from_emp))
                to_contact = to_contact.json()[0]
                to_email = to_contact["email_address"]
                to_phone = to_contact["phone_number"]

                shiftDate1 = a["orig_start_date"]
                shiftStart1 = a["orig_start_time"]
                shiftEnd1 = a["orig_end_time"]
                shiftDate2 = a["new_start_date"]
                shiftStart2 = a["new_start_time"]
                shiftEnd2 = a["new_end_time"]
                swapID = 0
                emails.swap_email(shiftDate1, shiftStart1, shiftEnd1,
                              shiftDate2, shiftStart2, shiftEnd2, swapID, to_email)

                phone_with_code = "+1" + to_phone
                if to_phone.isdigit():
                    texts.swap_text(shiftDate1, shiftStart1, shiftEnd1,
                              shiftDate2, shiftStart2, shiftEnd2, swapID, phone_with_code)

                requests.post("http://localhost:5000/swap/" + str(from_emp) +
                          "/" + str(from_id) + "/" + str(username) + "/" + str(to_id))

            # Deny Swap
            elif request.form.get('status_deny'):
                statusDeny = request.form.get('status_deny')
                id_swap = request.form.get('id_swap')
                requests.post(
                    "http://localhost:5000/updateswaprequest/'Denied'/" + str(id_swap))

                all_info = requests.get(
                    'http://localhost:5000/getalldeniedswaps/' + id_swap)
                a = all_info.json()[0]

                deny_swap = requests.get(
                    "http://localhost:5000/getpendingswap/" + id_swap)
                d = deny_swap.json()[0]
                from_emp = d["from_id_employee"]

                to_contact = requests.get(
                    "http://localhost:5000/getemailandphone/" + str(from_emp))
                to_contact = to_contact.json()[0]
                to_email = to_contact["email_address"]
                to_phone = to_contact["phone_number"]

                shiftDate1 = a["orig_start_date"]
                shiftStart1 = a["orig_start_time"]
                shiftEnd1 = a["orig_end_time"]
                shiftDate2 = d["new_start_date"]
                shiftStart2 = a["new_start_time"]
                shiftEnd2 = a["new_end_time"]
                swapID = 1
                emails.swap_email(shiftDate1, shiftStart1, shiftEnd1,
                              shiftDate2, shiftStart2, shiftEnd2, swapID, to_email)

                phone_with_code = "+1" + to_phone
                if to_phone.isdigit():
                    texts.swap_text(shiftDate1, shiftStart1, shiftEnd1,
                              shiftDate2, shiftStart2, shiftEnd2, swapID, phone_with_code)

            return redirect(url_for('notifications'))

         # CUSTOM MESSAGES
        messages = requests.get("http://localhost:5000/getmsgnotification/2")

        # USERS
        # DROPS
        # APPROVED
        # gets ID OF approved dropped shifts requested by employee 47
        approved_ids = requests.get(
            "http://localhost:5000/getapproveddropids/" + str(username))
        # for each ID, gets approved drop information
        approved_ids = approved_ids.json()
        dictOfApprovedDrops = {}
        for i in range(len(approved_ids)):
            id_drop = str(approved_ids[i]["id_pending_drop"])
            approved_drops = requests.get(
                "http://localhost:5000/getapproveddrop/" + id_drop)
            a = approved_drops.json()[0]
            # create dictionary of approved drop values
            dictOfApprovedDrops[id_drop] = a

        # DENIED
        # gets ID OF denied dropped shifts requested by employee 47
        denied_ids = requests.get(
            "http://localhost:5000/getdenieddropids/" + str(username))
        # for each ID, gets denied drop information
        denied_ids = denied_ids.json()
        dictOfDeniedDrops = {}
        for i in range(len(denied_ids)):
            id_drop = str(denied_ids[i]["id_pending_drop"])
            denied_drops = requests.get(
                "http://localhost:5000/getdenieddrop/" + id_drop)
            d = denied_drops.json()[0]
            # create dictionary of denied drop values
            dictOfDeniedDrops[id_drop] = d

        # VACATIONS
        # APPROVED
        # gets ID OF approved vacations requested by employee 47
        approved_ids = requests.get(
            "http://localhost:5000/getapprovedvacationids/" + str(username))
        # for each ID, gets approved information
        approved_ids = approved_ids.json()
        dictOfApprovedVacations = {}
        for i in range(len(approved_ids)):
            id_vacation = str(approved_ids[i]["id_pending_vacation"])
            approved_vacations = requests.get(
                "http://localhost:5000/getapprovedvacation/" + id_vacation)
            a = approved_vacations.json()[0]
            # create dictionary of approved vacation values
            dictOfApprovedVacations[id_vacation] = a

        # DENIED
        # gets ID OF denied vacations requested by employee 47
        denied_ids = requests.get(
            "http://localhost:5000/getdeniedvacationids/" + str(username))
        # for each ID, gets denied information
        denied_ids = denied_ids.json()
        dictOfDeniedVacations = {}
        for i in range(len(denied_ids)):
            id_vacation = str(denied_ids[i]["id_pending_vacation"])
            denied_vacations = requests.get(
                "http://localhost:5000/getdeniedvacation/" + id_vacation)
            d = denied_vacations.json()[0]
            # create dictionary of denied vacation values
            dictOfDeniedVacations[id_vacation] = d

        # SWAPS
        # NO RESPONSE
        # gets ID OF all swap requested by employee 47
        all_ids = requests.get(
            'http://localhost:5000/getapprovedswapids/' + str(username))
        # for each ID, gets approved information
        all_ids = all_ids.json()
        dictOfAllSwaps = {}
        for i in range(len(all_ids)):
            id_swap = str(all_ids[i]["id_pending_swap"])
            all_info = requests.get(
                'http://localhost:5000/getapprovedswap/' + id_swap)
            a = all_info.json()[0]
            # create dictionary of approved swap values
            dictOfAllSwaps[id_swap] = a

        # RESPONSE
        # EMPLOYEE
        # gets ID OF all pending drop requests
        pending_swap_ids = requests.get(
            "http://localhost:5000/getpendingswapstoapproveids/" + str(username))
        # for each ID, gets approved drop information
        pending_swap_ids = pending_swap_ids.json()
        dictOfPendingSwaps = {}

        for i in range(len(pending_swap_ids)):
            id_swap = str(pending_swap_ids[i]["id_pending_swap"])
            pending_swap_info = requests.get(
                "http://localhost:5000/getpendingswapstoapprove/" + id_swap)
            p = pending_swap_info.json()[0]
            # create dictionary of approved drop values
            dictOfPendingSwaps[id_swap] = p

        return render_template('notifications.html', vacationAppDict=dictOfApprovedVacations, vacationDenDict=dictOfDeniedVacations, swapDict=dictOfAllSwaps, dropAppDict=dictOfApprovedDrops, dropDenDict=dictOfDeniedDrops, pendEmpSwapDict=dictOfPendingSwaps, messages=messages.json(), user=user)

    if user.access == "3":

        # get email and phone number
        contact = requests.get(
            "http://localhost:5000/getemailandphone/" + str(username))
        contact = contact.json()[0]
        email = contact["email_address"]
        phone = contact["phone_number"]

        # POST (NEEDS TO BE FIRST)
        if request.method == 'POST':
            # Approve Drop
            if request.form.get('drop_app'):
                statusApprove = request.form.get('drop_app')
                id_drop = request.form.get('id_drop')
                requests.post(
                    "http://localhost:5000/updatedroprequest/'Approved'/" + str(id_drop))
                approved_drop = requests.get(
                    "http://localhost:5000/getpendingdrop/" + id_drop)
                app = approved_drop.json()[0]
                requests.post("http://localhost:5000/drop/" +
                          str(username) + "/" + str(id_drop))

                shift_date = app["start_date"]
                start_time = app["start_time"]
                end_time = app["end_time"]
                drop_id = 0
                emails.drop_email(shift_date, start_time, end_time, drop_id, email)
                
                phone_with_code = "+1" + phone
                if phone.isdigit():
                    texts.drop_text(shift_date, start_time, end_time, drop_id, phone_with_code)

            # Deny Drop
            elif request.form.get('drop_deny'):
                statusDeny = request.form.get('drop_deny')
                id_drop = request.form.get('id_drop')
                requests.post(
                    "http://localhost:5000/updatedroprequest/'Denied'/" + str(id_drop))

                denied_drops = requests.get(
                    "http://localhost:5000/getdenieddrop/" + id_drop)
                d = denied_drops.json()[0]
                # create dictionary of denied drop values

                shift_date = d["start_date"]
                start_time = d["start_time"]
                end_time = d["end_time"]
                drop_id = 1
                emails.drop_email(shift_date, start_time, end_time, drop_id, email)
                phone_with_code = "+1" + phone
                if phone.isdigit():
                    texts.drop_text(shift_date, start_time, end_time, drop_id, phone_with_code)
            
            # Approve Vacation
            elif request.form.get('vac_app'):
                statusApprove = request.form.get('vac_app')
                id_vac = request.form.get('id_vac')
                requests.post(
                    "http://localhost:5000/updatevacationrequest/'Approved'/" + str(id_vac))
                approved_vac = requests.get(
                    "http://localhost:5000/getpendingvacation/" + id_vac)
                app = approved_vac.json()[0]

                start_date = app["start_date"]
                end_date = app["end_date"]
                num_days = app["duration"]
                #update vacation days left 
                requests.post("http://localhost:5000/updatevacationdays/"+ id_employee + "/" + num_days)
           
                vac_id = 0
                emails.vacation_email(start_date, end_date, vac_id, email)
                phone_with_code = "+1" + phone
                if phone.isdigit():
                    texts.vacation_text(start_date, end_date, vac_id, phone_with_code)

            # Deny Vacation
            elif request.form.get('vac_deny'):
                statusDeny = request.form.get('vac_deny')
                id_vac = request.form.get('id_vac')
                requests.post(
                    "http://localhost:5000/updatevacationrequest/'Denied'/" + str(id_vac))

                denied_vac = requests.get(
                    "http://localhost:5000/getdeniedvacation/" + id_vac)
                d = denied_vac.json()[0]
                # create dictionary of denied drop values

                start_date = d["start_date"]
                end_date = d["end_date"]
                vac_id = 1
                emails.vacation_email(start_date, end_date, vac_id, email)
                phone_with_code = "+1" + phone
                if phone.isdigit():
                    texts.vacation_text(start_date, end_date, vac_id, phone_with_code)
            return redirect(url_for('notifications'))

        # ADMIN
        # DROPS
        # gets ID OF all pending drop requests
        pending_ids = requests.get("http://localhost:5000/getallpendingdropids")
        # for each ID, gets approved drop information
        pending_ids = pending_ids.json()
        dictOfPendingDrops = {}
        for i in range(len(pending_ids)):
            id_drop = str(pending_ids[i]["id_pending_drop"])
            pending_requests = requests.get(
                "http://localhost:5000/getallpendingdrops/" + id_drop)
            p = pending_requests.json()[0]
            # create dictionary of approved drop values
            dictOfPendingDrops[id_drop] = p

        # VACATIONS
        # gets ID OF all pending vacation requests
        # for each ID, gets approved drop information
        pending_ids = requests.get(
            "http://localhost:5000/getallpendingvacationids")
        pending_ids = pending_ids.json()
        dictOfPendingVacations = {}
        for i in range(len(pending_ids)):
            id_vacation = str(pending_ids[i]["id_pending_vacation"])
            pending_requests = requests.get(
                "http://localhost:5000/getallpendingvacation/" + id_vacation)
            p = pending_requests.json()[0]
            # create dictionary of approved drop values
            dictOfPendingVacations[id_vacation] = p
        
        # CUSTOM MESSAGES
        messages = requests.get("http://localhost:5000/getmsgnotification/2")
            
        return render_template('notifications.html', pendDropDict=dictOfPendingDrops, pendVacDict=dictOfPendingVacations, messages=messages.json(), user=user)
   
# This gets all of the employees working a selected date/time/role
@app.route('/mastercal/<date>/<shift>/<role>', methods=['GET', 'POST'])
def mastercal(date, shift, role):
    print(shift, type(shift))
    dictOfAllShifts = {}
    mcids = requests.get("http://localhost:5000/mastercalids/" + role)
    mcids = mcids.json()
    # iterate through to grab shift info
    m = 0
    for i in range(len(mcids)):
        id_shift = str(mcids[i]["id_shift"])
        all_info = requests.get("http://localhost:5000/mastercalshifts/" + id_shift + "/" + shift)
        a = all_info.json()
        print(a, len(a))
        # iterate through to grab all employees working that shift
        for k in range(len(a)):
            print("entering for loop")
            id_shift_daypart = a[k]['id_shift_daypart']
            day_of_week = a[k]['day_of_week']
            first_or_second_code = a[k]['first_or_second']
            start_time = a[k]['start_time']
            end_time = a[k]['end_time']
            # send request to get all employees
            emp = requests.get("http://localhost:5000/mastercalemp/" + str(id_shift_daypart) + "/" +
                               day_of_week + "/" + first_or_second_code + "/" + start_time + "/" + end_time + "/" + date)
            if (len(emp.json()) != 0):
                dictOfAllShifts[m] = emp.json()
                m = m + 1
    return dictOfAllShifts


@app.route('/calendar', methods=['GET', 'POST'])
def calendar():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    return render_template('calendar.html', user=user)


@app.route('/log', methods=['GET', 'POST'])
def log():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    return render_template('log.html', user=user)


@app.route('/messaging', methods=['GET', 'POST'])
def messaging():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))
    if user.access == "1":
        return redirect(url_for('settings'))

    if request.method == 'POST':
        recipients = request.form.get('role')
        msg = request.form.get('message')

        print(recipients, msg)
        message = requests.post(
            "http://localhost:5000/setmsgnotification/" + recipients + "/" + msg)

        return redirect(url_for('messaging'))

    return render_template('messaging.html', user=user)


@app.route('/settings', methods=['GET', 'POST'])
def settings():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))

    if user.part_time_ind == "Y":
        status = "Part Time"
    else:
        status = "Full Time"

    phone = user.phone

    form = SettingsForm(request.form)
    return render_template('settings.html', form=form, user=user, status=status, phone=phone)


@app.route('/editinfo', methods=['GET', 'POST'])
def editinfo():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))

    form = EditInfo(request.form)
    return render_template('editinfo.html', form=form, user=user)


@app.route('/changepassfromsettings', methods=['GET', 'POST'])
def changepassfromsettings():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))

    form = ChangePassFromSettings(request.form)
    return render_template('changepassfromsettings.html', form=form, user=user)


@app.route('/verifyemail', methods=['GET', 'POST'])
def verifyemail():

    username, user = getUser()

    if not username:
        return redirect(url_for('login'))

    form = VerifyEmail(request.form)
    return render_template('verifyemail.html', form=form, user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():

    username, user = getUser()

    if username:
        return redirect(url_for('home'))

    form = Login(request.form)
    error = ""
    if(request.method == "POST" and form.validate()):
        response = requests.get(
            "http://localhost:5000/getuserdata/" + str(form.username.data))

        user = User(form.username.data, response.json()["role_name"], response.json()["first_name"], response.json()[
                    "last_name"], response.json()["part_time_ind"], response.json()["email"], response.json()["phone"], response.json()["user_type"])

        password = hashlib.sha256(
            ('clientsidesalt' + form.password.data).encode('utf-8')).hexdigest()
        response = requests.get("http://localhost:5000/login/" +
                                password + "/" + str(form.username.data))

        if response.text.strip() == "1":
            session['username'] = str(form.username.data)
            return redirect(url_for('home'))
        else:
            error = "Invalid Credentials."

    return render_template('login.html', form=form, Error=error, user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    username, user = getUser()

    if username:
        return redirect(url_for('home'))

    form = Registration(request.form)
    if(request.method == "POST" and form.validate()):
        response = requests.get(
            "http://localhost:5000/checkifemployee/" + str(form.username.data))

        if(response.json()["validEmployee"] and not response.json()["registered"]):
            return redirect(url_for('registerForm', id_employee=form.username.data))

    return render_template('register.html', form=form, user=user)


@app.route('/registerForm/<int:id_employee>', methods=['GET', 'POST'])
def registerForm(id_employee):
    username, user = getUser()

    if username:
        return redirect(url_for('home'))

    form = RegistrationFull(request.form)

    if(request.method == "POST" and form.validate()):
        password = hashlib.sha256(
            ('clientsidesalt' + form.password.data).encode('utf-8')).hexdigest()
        response = requests.post("http://localhost:5000/register/" + password + "/" + str(
            form.phone.data) + "/" + form.email.data + "/" + str(id_employee))
        if response.status_code == 200:
            return redirect(url_for('login'))
    return render_template('registerFull.html', form=form, id_employee=id_employee, user=user)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


class Registration(Form):
    username = IntegerField('Employee ID', [
                            validators.InputRequired(), validators.NumberRange(min=1, max=9999)])


class RegistrationFull(Form):
    username = IntegerField('Employee ID')
    password = PasswordField('Password', [
        validators.Length(min=8, max=40),
        validators.EqualTo(
            'confirm', message="Passwords do not match!"), validators.InputRequired()
    ])
    confirm = PasswordField('Confirm Password', [validators.InputRequired()])
    email = EmailField('Email', [validators.InputRequired()])
    phone = StringField('Phone Number', [validators.InputRequired()])

    def validate_phone(form, field):
        if len(field.data) > 11:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')


class Login(Form):
    username = IntegerField('Username', [validators.NumberRange(
        min=1, max=9999), validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(
        min=8, max=40), validators.InputRequired()])


class SettingsForm(Form):
    username = IntegerField('Employee ID')
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    position = StringField('Position')
    employment_status = StringField('Ful or Part Time')
    email = EmailField('Email')
    phone = StringField('Phone Number')


class EditInfo(Form):
    email = EmailField('Email', [validators.InputRequired()])
    phone = StringField('Phone Number', [validators.InputRequired()])

    def validate_phone(form, field):
        if len(field.data) > 11:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')


class VerifyEmail(Form):
    email = EmailField('Email', [validators.InputRequired()])
    code = StringField('Verification Code', [
                       validators.InputRequired(), validators.Length(min=8, max=8)])


class ChangePassFromSettings(Form):
    password = PasswordField('Old Password', [
        validators.Length(min=8, max=40), validators.InputRequired()
    ])
    new_password = PasswordField('New Password', [
        validators.Length(min=8, max=40),
        validators.EqualTo(
            'confirm', message="Passwords do not match!"), validators.InputRequired()
    ])
    confirm = PasswordField('Confirm New Password', [
                            validators.InputRequired()])


if __name__ == '__main__':
    app.run(debug=True, port=5001)
