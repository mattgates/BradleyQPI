from flask import Flask
from flask_restful import Resource, Api
from datetime import datetime
import pyodbc
import json
import hashlib
app = Flask(__name__)
api = Api(app)

f = open('login.txt', 'r')
line = f.readline()
(server, database, username, password) = line.split(';')

driver = '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server +
                      ';PORT=1433;DATABASE='+database+';UID='+username+';PWD=' + password)

cursor = cnxn.cursor()

# NOT USED


class Schedule(Resource):
    def get(self, shift_code):
        results = []
        columns = ('id_shift_part', 'id_shift', 'day_of_week',
                   'first_or_second_code', 'start_time', 'end_time', 'max_employees')

        cursor.execute('SELECT * FROM dbo.schedule_shift_daypart')
        for row in cursor.fetchall():
            results.append({
                'id_shift_part': row[0],
                'id_shift': row[1],
                'day_of_week': row[2],
                'first_or_second_code': row[3],
                'start_time': row[4].strftime("%I:%M %p") if row[4] is not None else 'N/A',
                'end_time': row[5].strftime("%I:%M %p") if row[5] is not None else 'N/A',
                'max_employees': row[6]
            })

        return {"results": results}, 200

    def post(self):
        return 404

# Given an an employee's ID, gets all shifts for that employee given their part_time_ind and their id_role


class GetShifts(Resource):
    def get(self, id_employee):
        data = []
        query = """
                if(
                    (SELECT part_time_ind
                    FROM employee
                    WHERE id_employee = <id_employee>) = 'y'
                )
                BEGIN
                SELECT id_shift_daypart, day_of_week, start_time, end_time, max_employees, shift_date
                FROM schedule_shift_daypart
                WHERE id_shift IN (
                    SELECT id_shift
                    FROM schedule_shift
                    WHERE id_role IN (
                            SELECT id_role
                            FROM employee
                            WHERE id_employee = <id_employee>
                            ) AND ft_or_pt_code = 'PART-TIME'
                    )
                
                END
                ELSE
                BEGIN
                
                SELECT id_shift_daypart, day_of_week, start_time, end_time, max_employees, shift_date
                FROM schedule_shift_daypart
                WHERE id_shift IN (
                    SELECT id_shift
                    FROM schedule_shift
                    WHERE id_role IN (
                            SELECT id_role
                            FROM employee
                            WHERE id_employee = <id_employee>
                            ) AND ft_or_pt_code = 'FULL-TIME'
                    )           
                END
            """

        query = query.replace("<id_employee>", str(id_employee))
        cursor.execute(query)

        for row in cursor.fetchall():
            shift = {
                'id_shift_daypart': row[0],
                'day_of_week': row[1],
                'start_time': row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
                'end_time': row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                'max_employees': row[4],
                'shift_date': row[5].strftime("%m/%d/%Y") if row[5] is not None else 'N/A',
            }
            data.append(shift)

        return data, 200


# Given a list of id_shift_dayparts and an employee, adds employee & shifts to daily_employee_calendar
class SetShifts(Resource):
    def post(self, id_employee, id_shift_daypart):

        shifts = id_shift_daypart.split(",")
        query = """
            IF ( (
                SELECT max_employees
            FROM schedule_shift_daypart
            WHERE id_shift_daypart = <id_shift_daypart>
            ) != 0)
            
            BEGIN
            INSERT INTO daily_employee_calendar
            VALUES (
                    (
                    SELECT shift_date
                    FROM schedule_shift_daypart
                    WHERE id_shift_daypart = <id_shift_daypart>
                ), 
                <id_employee>,
                <id_shift_daypart>, 'Working', 
                (SELECT last_name
                FROM employee
                WHERE id_employee = <id_employee>),
                GETDATE(), NULL, NULL)
            
            UPDATE schedule_shift_daypart
            SET max_employees = max_employees - 1
            WHERE id_shift_daypart = <id_shift_daypart>
 
            END
            """

        query = query.replace("<id_employee>", str(id_employee))
        for x in shifts:
            newQuery = query.replace("<id_shift_daypart>", str(x))
            cursor.execute(newQuery)
            cnxn.commit()

        return 200

# given an id_employee, id_calendar of all the shifts an employee is working from daily_employee_calendar


class MyShiftIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_calendar
            FROM daily_employee_calendar
            WHERE id_employee = <id_employee> 
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            idCal = {
                'id_calendar': row[0],
            }
            data.append(idCal)

        return data, 200

# given an id_calendar from daily_employee_calendar, returns employee & shift date/time associated with the entry


class MyShifts(Resource):
    def get(self, id_calendar):
        data = []
        query = """
            SELECT id_shift_daypart, day_of_week, start_time, end_time, (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_calendar = <id_calendar>
            )
            FROM schedule_shift_daypart
            WHERE id_shift_daypart IN (
                SELECT id_shift_daypart
                FROM daily_employee_calendar
                WHERE id_calendar = <id_calendar>
            )
        """
        query = query.replace("<id_calendar>", id_calendar)

        cursor.execute(query)
        for row in cursor.fetchall():
            shift = {
                'id_shift_daypart': row[0],
                'day_of_week': row[1],
                'start_time': row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
                'end_time': row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                'date': row[4].strftime("%m/%d/%Y") if row[4] is not None else 'N/A',
            }
            data.append(shift)

        return data, 200

# NOT USED


class GetUser(Resource):
    def get(self, employee_code):
        data = []
        query = """
            SELECT last_name, first_name, id_role,
            (SELECT role_name
            FROM role_list
            WHERE id_role =
            (SELECT id_role
            FROM employee
            WHERE employee_code = <employee_code>)
            ), part_time_ind
            FROM employee
            WHERE employee_code = <employee_code>
        """

        query = query.replace("<employee_code>", employee_code)

        cursor.execute(query)
        for x in cursor.fetchall():
            user = {
                "last_name": x[0],
                "first_name": x[1],
                "id_role": x[2],
                "role_name": x[3],
                "part_time_ind": x[4]
            }

        return user, 200

# swaps employees (from/to_id_employee) working shifts (from/to_id_shift_daypart) in in daily_employee_calendar


class Swap(Resource):
    def post(self, from_id_employee, to_id_employee, from_id_shift_daypart, to_id_shift_daypart):
        fromQuery = """
            UPDATE daily_employee_calendar
            SET id_employee = <from_id_employee>,
                [status] = 'Swapped',
                updated_dt = GETDATE(),
                updated_by = (SELECT last_name
                    FROM employee
                    WHERE id_employee = <from_id_employee>)
            WHERE id_employee = <to_id_employee> AND id_shift_daypart = <to_id_shift_daypart>;
        """
        toQuery = """
            UPDATE daily_employee_calendar
            SET id_employee = <to_id_employee>,
                [status] = 'Swapped',
                updated_dt = GETDATE(),
                updated_by = (SELECT last_name
                    FROM employee
                    WHERE id_employee = <to_id_employee>)
            WHERE id_employee = <from_id_employee> AND id_shift_daypart = <from_id_shift_daypart>;
        """

        fromQuery = fromQuery.replace("<from_id_employee>", from_id_employee)
        fromQuery = fromQuery.replace("<to_id_employee>", to_id_employee)
        fromQuery = fromQuery.replace(
            "<to_id_shift_daypart>", to_id_shift_daypart)

        toQuery = toQuery.replace("<from_id_employee>", from_id_employee)
        toQuery = toQuery.replace("<to_id_employee>", to_id_employee)
        toQuery = toQuery.replace(
            "<from_id_shift_daypart>", from_id_shift_daypart)

        cursor.execute(fromQuery)
        cursor.execute(toQuery)
        cnxn.commit()

        return 200


# This api & query gets all employees not working a given id_shift_daypart
class getSwapEmp(Resource):
    def get(self, id_employee, id_shift_daypart):
        data = []
        # gets ids of all employees working a certain shift
        query = """
            SELECT last_name, first_name, role_name, employee.id_employee
            FROM employee
            INNER JOIN daily_employee_calendar
            ON employee.id_employee = daily_employee_calendar.id_employee
            WHERE id_role = (
                SELECT id_role
                FROM employee
                WHERE id_employee = <id_employee>
            ) AND id_shift_daypart != <id_shift_daypart>
        """
        query = query.replace("<id_employee>", id_employee)
        query = query.replace("<id_shift_daypart>", id_shift_daypart)

        cursor.execute(query)
        for row in cursor.fetchall():
            user = {
                "last_name": row[0],
                "first_name": row[1],
                "role": row[2],
                "id_employee": row[3],
            }
            data.append(user)
        return data, 200

# NOT CURRENTLY USED


class getSwapShiftIDs(Resource):
    def get(self, from_id_employee, to_id_employee):
        data = []
        query = """
        SELECT id_calendar
        FROM daily_employee_calendar
        WHERE id_employee = <to_id_employee> AND id_shift_daypart NOT IN (
            SELECT id_shift_daypart
            FROM daily_employee_calendar
            WHERE id_employee = <from_id_employee>
        )
        """
        query = query.replace("<to_id_employee>", to_id_employee)
        query = query.replace("<from_id_employee>", from_id_employee)
        cursor.execute(query)
        for row in cursor.fetchall():
            idCal = {
                "id_calendar": row[0],
            }
            data.append(idCal)
        return data, 200

# NOT CURRENTLY USED


class getSwapShifts(Resource):
    def get(self, id_calendar):
        data = []
        query = """
        SELECT (
            SELECT calendar_date
            FROM daily_employee_calendar
            WHERE id_calendar = <id_calendar>
        ) AS [Calendar_Date], start_time, end_time, id_shift_daypart
        FROM schedule_shift_daypart
        WHERE id_shift_daypart = (
            SELECT id_shift_daypart
            FROM daily_employee_calendar
            WHERE id_calendar = <id_calendar>
        )
        """
        query = query.replace("<id_calendar>", id_calendar)
        cursor.execute(query)
        for row in cursor.fetchall():
            user = {
                "id_shift_daypart": row[3],
                "date": row[0].strftime("%m/%d/%Y") if row[0] is not None else 'N/A',
                "start_time": row[1].strftime("%I:%M %p") if row[1] is not None else 'N/A',
                "end_time": row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
            }
            data.append(user)
        return data, 200

# Adds pending swap request to pending_swap table


class SetPendingSwap(Resource):
    def post(self, from_id_employee, from_id_shift_daypart, to_id_employee, to_id_shift_daypart):
        data = []
        query = """
            INSERT INTO pending_swap(from_id_shift_daypart, from_id_employee, to_id_shift_daypart, to_id_employee, shift_time, date_of_request, status_code) 
            OUTPUT inserted.id_pending_swap
            VALUES (
                (SELECT id_shift_daypart
                FROM daily_employee_calendar
                WHERE id_employee = <from_id_employee> AND id_shift_daypart = <from_id_shift_daypart> ),
                (SELECT id_employee
                FROM daily_employee_calendar
                WHERE id_employee = <from_id_employee> AND id_shift_daypart = <from_id_shift_daypart> ),
                (SELECT id_shift_daypart
                FROM daily_employee_calendar
                WHERE id_employee = <to_id_employee> AND id_shift_daypart = <to_id_shift_daypart> ),
                (SELECT id_employee
                FROM daily_employee_calendar
                WHERE id_employee = <to_id_employee> AND id_shift_daypart = <to_id_shift_daypart> ),
                (SELECT shift_desc
                FROM schedule_shift
                WHERE id_shift = 3),
                GETDATE(),
                'pending'
            )
            
        """
        # need to replace each of the attributes with something more friendly
        query = query.replace("<from_id_employee>", str(from_id_employee))
        query = query.replace("<to_id_employee>", str(to_id_employee))
        query = query.replace("<from_id_shift_daypart>",
                              str(from_id_shift_daypart))
        query = query.replace("<to_id_shift_daypart>",
                              str(to_id_shift_daypart))

        cursor.execute(query)
        for row in cursor.fetchall():
            idPending = {
                "id_pending_swap": row[0],
            }
            data.append(idPending)

        cnxn.commit()

        return data, 200

# inserts pending swap request into notifications table


class SetSwapNotification(Resource):
    def post(self, id_employee, id_pending_swap):
        query = """
            INSERT INTO notification(sent_to, sent_from, msg, response, sent_time)
            VALUES ('Swap', <id_employee>, <id_pending_swap>, 'pending', GETDATE())

         """
        # need to replace each of the attributes with something more friendly
        query = query.replace("<id_employee>", str(id_employee))
        query = query.replace("<id_pending_swap>", str(id_pending_swap))
        cursor.execute(query)
        cnxn.commit()

        return 200

# Gets all information associated with a pending_swap request of id_pending_swap


class getPendingSwap(Resource):
    def get(self, id_pending_swap):
        data = []
        query = """
            SELECT (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [original_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [original_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                ) AND id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [original_calendar_date],
             (
                SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
            ) AS [from_id_shift_daypart],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                ) AND id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_calendar_date],
             (
                SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
            ) AS [to_id_shift_daypart],
            date_of_request,
            status_code,
            (
                SELECT first_name
                FROM employee
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [first_name],
            (
                SELECT last_name
                FROM employee
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [last_name], 
            (
                SELECT from_id_employee
                FROM pending_swap
                WHERE id_pending_swap = <id_pending_swap>
                
            ) AS [from_id_employee]
            FROM pending_swap
            WHERE id_pending_swap = <id_pending_swap>
        """

        query = query.replace("<id_pending_swap>", id_pending_swap)

        cursor.execute(query)
        for row in cursor.fetchall():

            shift = {
                "orig_start_time": row[0].strftime("%I:%M %p") if row[0] is not None else 'N/A',
                "orig_end_time": row[1].strftime("%I:%M %p") if row[1] is not None else 'N/A',
                "orig_start_date": row[2].strftime("%m/%d/%Y") if row[2] is not None else 'N/A',
                "from_id_shift_daypart": row[3],
                "new_start_time": row[4].strftime("%I:%M %p") if row[4] is not None else 'N/A',
                "new_end_time": row[5].strftime("%I:%M %p") if row[5] is not None else 'N/A',
                "new_start_date": row[6].strftime("%m/%d/%Y") if row[6] is not None else 'N/A',
                "to_id_shift_daypart": row[7],
                "request_sent_date": row[8].strftime("%m/%d/%Y") if row[8] is not None else 'N/A',
                "status": row[9],
                "first_name": row[10],
                "last_name": row[11],
                "from_id_employee": row[12]
            }
            data.append(shift)
        return data, 200

#Gets id_pending_swap of all pending swap shifts requested by employee #


class getPendingSwapIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_swap, from_id_employee, to_id_employee
            FROM pending_swap
            WHERE from_id_employee = <id_employee> AND status_code = 'pending'
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_swap": row[0]
            }
            data.append(id_drop)
        return data, 200


# Gets all information associated with a approved swap request of id_pending_swap
class getApprovedSwap(Resource):
    def get(self, id_pending_swap):
        data = []
        query = """
            SELECT (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [original_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [original_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                ) AND id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [original_calendar_date],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                ) AND id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_calendar_date],
            date_of_request,
            status_code,
            (
                SELECT first_name
                FROM employee
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [first_name],
            (
                SELECT last_name
                FROM employee
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [last_name]
            FROM pending_swap
            WHERE id_pending_swap = <id_pending_swap>
        """

        query = query.replace("<id_pending_swap>", id_pending_swap)

        cursor.execute(query)
        for row in cursor.fetchall():
            print(row)
            print(row == None)
            shift = {
                "new_start_time": row[0].strftime("%I:%M %p") if row[0] is not None else 'N/A',
                "new_end_time": row[1].strftime("%I:%M %p") if row[1] is not None else 'N/A',
                "new_start_date": row[2].strftime("%m/%d/%Y") if row[2] is not None else 'N/A',
                "orig_start_time": row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                "orig_end_time": row[4].strftime("%I:%M %p") if row[4] is not None else 'N/A',
                "orig_start_date": row[5].strftime("%m/%d/%Y") if row[5] is not None else 'N/A',
                "request_sent_date": row[6].strftime("%m/%d/%Y") if row[6] is not None else 'N/A',
                "status": row[7],
                "first_name": row[8],
                "last_name": row[9]
            }
            data.append(shift)
        return data, 200

#Gets id_pending_swap of all approved swap shifts requested by employee #


class getApprovedSwapIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_swap, from_id_employee, to_id_employee
            FROM pending_swap
            WHERE from_id_employee = <id_employee> AND status_code = 'approved'
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_swap": row[0]
            }
            data.append(id_drop)
        return data, 200

#This gets all denied swap shift ids requested by employee #


class getAllDeniedSwapIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_swap
            FROM pending_swap
            WHERE from_id_employee = <id_employee> AND status_code = 'denied'
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_swap": row[0]
            }
            data.append(id_drop)
        return data, 200

# Gets all information associated with a denied swap request of id_pending_swap


class getAllDeniedSwaps(Resource):
    def get(self, id_pending_swap):
        data = []
        query = """
            SELECT (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                )
            ) AS [original_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                )
            ) AS [original_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                ) AND id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                )
            ) AS [original_calendar_date],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                )
            ) AS [new_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                )
            ) AS [new_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                ) AND id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                )
            ) AS [new_calendar_date],
            date_of_request,
            status_code,
            (
                SELECT first_name
                FROM employee
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                )
            ) AS [first_name],
            (
                SELECT last_name
                FROM employee
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap> 
                )
            ) AS [last_name]
            FROM pending_swap
            WHERE id_pending_swap = <id_pending_swap> 


         """
        query = query.replace("<id_pending_swap>", id_pending_swap)

        cursor.execute(query)
        for row in cursor.fetchall():
            shift = {
                "orig_start_time": row[0].strftime("%I:%M %p") if row[0] is not None else 'N/A',
                "orig_end_time": row[1].strftime("%I:%M %p") if row[1] is not None else 'N/A',
                "orig_start_date": row[2].strftime("%m/%d/%Y") if row[2] is not None else 'N/A',
                "new_start_time": row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                "new_end_time": row[4].strftime("%I:%M %p") if row[4] is not None else 'N/A',
                "new_start_date": row[5].strftime("%m/%d/%Y") if row[5] is not None else 'N/A',
                "request_sent_date": row[6].strftime("%m/%d/%Y") if row[6] is not None else 'N/A',
                "status": row[7],
                "first_name": row[8],
                "last_name'": row[9],
            }
            data.append(shift)
        return data, 200

# This gets all id_pending_swaps for the shifts that employee id_employee needs to approve


class getPendingSwapsToApproveIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_swap
            FROM pending_swap
            WHERE to_id_employee = <id_employee> AND status_code = 'pending'
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_swap": row[0]
            }
            data.append(id_drop)
        return data, 200

# Gets all information associated with a pending swap request of id_pending_swap


class getPendingSwapsToApprove(Resource):
    def get(self, id_pending_swap):
        data = []
        query = """
            SELECT (
                SELECT first_name
                FROM employee
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [first_name],
            (
                SELECT last_name
                FROM employee
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [last_name],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                ) AND id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_calendar_date],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [current_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [current_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                ) AND id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [current_calendar_date],
            status_code
            FROM pending_swap
            WHERE id_pending_swap = <id_pending_swap>

        """
        query = query.replace("<id_pending_swap>", id_pending_swap)

        cursor.execute(query)
        for row in cursor.fetchall():
            shift = {
                "from_first_name": row[0],
                "from_last_name": row[1],
                "their_start_time": row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
                "their_end_time": row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                "their_start_date": row[4].strftime("%m/%d/%Y") if row[4] is not None else 'N/A',
                "your_start_time": row[5].strftime("%I:%M %p") if row[5] is not None else 'N/A',
                "your_end_time": row[6].strftime("%I:%M %p") if row[6] is not None else 'N/A',
                "your_start_date": row[7].strftime("%m/%d/%Y") if row[7] is not None else 'N/A',
            }
            data.append(shift)
        return data, 200


# updates status of id_pending_swap to 'status' in pending_swap table
class updateSwapRequest(Resource):
    def post(self, status, id_pending_swap):
        query = """
            UPDATE pending_swap
            SET status_code = <status>, date_of_request = GETDATE()
            WHERE id_pending_swap = <id_pending_swap>
        """
        query = query.replace("<status>", status)
        query = query.replace("<id_pending_swap>", id_pending_swap)
        cursor.execute(query)
        cnxn.commit()
        return 200

# updates status of exisiting swap request in notifications table


class updateSwapNotification(Resource):
    def post(self, status, id_pending_swap):
        query = """
            UPDATE notification
            SET response = <status>, sent_time = GETDATE()
            WHERE msg = <id_pending_swap> AND sent_to = 'Swap'
        """
        query = query.replace("<status>", status)
        query = query.replace("<id_pending_swap>", id_pending_swap)

        cursor.execute(query)
        cnxn.commit()

        return 200

# NOT USED


class getOpenSwapsToApproveIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_swap
            FROM pending_swap
            WHERE to_id_employee = <id_employee> AND status_code = 'open'
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_swap": row[0]
            }
            data.append(id_drop)
        return data, 200

# NOT USED


class getOpenSwapsToApprove(Resource):
    def get(self, id_pending_swap):
        data = []
        query = """
            SELECT (
                SELECT first_name
                FROM employee
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [first_name],
            (
                SELECT last_name
                FROM employee
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [last_name],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT from_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                ) AND id_shift_daypart = (
                    SELECT from_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [new_calendar_date],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [current_start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [current_end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT to_id_employee
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                ) AND id_shift_daypart = (
                    SELECT to_id_shift_daypart
                    FROM pending_swap
                    WHERE id_pending_swap = <id_pending_swap>
                )
            ) AS [current_calendar_date],
            status_code
            FROM pending_swap
            WHERE id_pending_swap = <id_pending_swap>

        """
        query = query.replace("<id_pending_swap>", id_pending_swap)

        cursor.execute(query)
        for row in cursor.fetchall():
            shift = {
                "from_first_name": row[0],
                "from_last_name": row[1],
                "their_start_time": row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
                "their_end_time": row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                "their_start_date": row[4].strftime("%m/%d/%Y") if row[4] is not None else 'N/A',
                "your_start_time": row[5].strftime("%I:%M %p") if row[5] is not None else 'N/A',
                "your_end_time": row[6].strftime("%I:%M %p") if row[6] is not None else 'N/A',
                "your_start_date": row[7].strftime("%m/%d/%Y") if row[7] is not None else 'N/A',
            }
            data.append(shift)
        return data, 200

# Updates daily_employee_calendar so that an employee is dropped from shift id_shift_daypart
# Increments spots left


class Drop(Resource):
    def post(self, id_employee, id_shift_daypart):
        query = """
            UPDATE daily_employee_calendar
            SET id_shift_daypart = <id_shift_daypart>,
            [status] = 'Dropped',
            updated_by = 'Drop',
            updated_dt = GETDATE(),
            calendar_date = (
                SELECT shift_date
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = <id_shift_daypart>
            )
            WHERE id_employee = <id_employee> AND id_shift_daypart = <id_shift_daypart> 
             
            UPDATE schedule_shift_daypart
            SET max_employees = max_employees + 1
            WHERE id_shift_daypart = <id_shift_daypart>
        """

        query = query.replace("<id_employee>", id_employee)
        query = query.replace("<id_shift_daypart>", id_shift_daypart)

        cursor.execute(query)
        cnxn.commit()

        return 200

# Inserts pending drop request into pending_drop table


class SetPendingDrop(Resource):
    def post(self, id_employee, id_shift_daypart):
        data = []
        query = """
            INSERT INTO pending_drop(id_shift_daypart, id_employee, request_sent_date, status_code)
            OUTPUT inserted.id_pending_drop
            VALUES( (<id_shift_daypart>),( <id_employee> ), GETDATE(), 'pending' ); 
         """
        # need to replace each of the attributes with something more friendly
        query = query.replace("<id_shift_daypart>", str(id_shift_daypart))
        query = query.replace("<id_employee>", str(id_employee))
        cursor.execute(query)

        for row in cursor.fetchall():
            idPending = {
                "id_pending_drop": row[0],
            }
            data.append(idPending)
        cnxn.commit()
        return data, 200

# inserts pending drop request  into notifications table


class SetDropNotification(Resource):
    def post(self, id_employee, id_pending_drop):
        query = """
            INSERT INTO notification(sent_to, sent_from, msg, response, sent_time)
            VALUES ('Drop', <id_employee>, <id_pending_drop>, 'pending', GETDATE())

         """
        # need to replace each of the attributes with something more friendly
        query = query.replace("<id_employee>", str(id_employee))
        query = query.replace("<id_pending_drop>", str(id_pending_drop))
        cursor.execute(query)
        cnxn.commit()

        return 200

# Gets all information associated with a pending drop request of id_pending_drop


class getPendingDrop(Resource):
    def get(self, id_pending_drop):
        data = []
        query = """
            SELECT (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                ) AND id_employee = (
                    SELECT id_employee
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [Original Date],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [Start Time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [End Time],
            request_sent_date
            FROM pending_drop
            WHERE id_pending_drop = <id_pending_drop>

        """

        query = query.replace("<id_pending_drop>", id_pending_drop)

        cursor.execute(query)
        for row in cursor.fetchall():
            shift = {
                "start_date": row[0].strftime("%m/%d/%Y") if row[0] is not None else 'N/A',
                "start_time": row[1].strftime("%I:%M %p") if row[1] is not None else 'N/A',
                "end_time": row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
                "request_sent_date": row[3].strftime("%m/%d/%Y") if row[3] is not None else 'N/A',
                "id_pending_drop": id_pending_drop
            }
            data.append(shift)
        return data, 200


#This gets all pending drop shift ids requested by employee #
class getPendingDropIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_drop
            FROM pending_drop
            WHERE id_employee = <id_employee> AND status_code = 'pending'
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_drop": row[0]
            }
            data.append(id_drop)
        return data, 200


# Gets all information associated with a approved drop request of id_pending_drop
class getApprovedDrop(Resource):
    def get(self, id_pending_drop):
        data = []
        query = """
            SELECT (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                ) AND id_employee = (
                    SELECT id_employee
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [Original Date],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [Start Time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [End Time],
            request_sent_date
            FROM pending_drop
            WHERE id_pending_drop = <id_pending_drop>
        """
        query = query.replace("<id_pending_drop>", id_pending_drop)

        cursor.execute(query)
        for row in cursor.fetchall():
            shift = {
                "start_date": row[0].strftime("%m/%d/%Y") if row[0] is not None else 'N/A',
                "start_time": row[1].strftime("%I:%M %p") if row[1] is not None else 'N/A',
                "end_time": row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
                "request_sent_date": row[3].strftime("%m/%d/%Y") if row[3] is not None else 'N/A',
            }
            data.append(shift)
        return data, 200

#This gets all approved drop shift ids requested by employee #


class getApprovedDropIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_drop
            FROM pending_drop
            WHERE id_employee = <id_employee> AND status_code = 'approved'
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_drop": row[0]
            }
            data.append(id_drop)
        return data, 200

# Gets all information associated with a denied drop request of id_pending_drop


class getDeniedDrop(Resource):
    def get(self, id_pending_drop):
        data = []
        query = """
            SELECT (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                ) AND id_employee = (
                    SELECT id_employee
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [Original Date],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [Start Time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop>
                )
            ) AS [End Time],
            request_sent_date
            FROM pending_drop
            WHERE id_pending_drop = <id_pending_drop>
        """
        query = query.replace("<id_pending_drop>", id_pending_drop)

        cursor.execute(query)
        for row in cursor.fetchall():
            shift = {
                "start_date": row[0].strftime("%m/%d/%Y") if row[0] is not None else 'N/A',
                "start_time": row[1].strftime("%I:%M %p") if row[1] is not None else 'N/A',
                "end_time": row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
                "request_approved_date": row[3].strftime("%m/%d/%Y") if row[3] is not None else 'N/A',
            }
            data.append(shift)
        return data, 200

#This gets all denied drop shift ids requested by employee #


class getDeniedDropIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_drop
            FROM pending_drop
            WHERE id_employee = <id_employee> AND status_code = 'denied'
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_drop": row[0]
            }
            data.append(id_drop)
        return data, 200

# This gets all pending drop shift ids for admin to approve


class getAllPendingDropIDs(Resource):
    def get(self):
        data = []
        query = """
            SELECT id_pending_drop
            FROM pending_drop
            WHERE status_code = 'pending'
        """

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_drop": row[0]
            }
            data.append(id_drop)
        return data, 200

# Gets all information associated with a pending drop request of id_pending_drop


class getAllPendingDrops(Resource):
    def get(self, id_pending_drop):
        data = []
        query = """
            SELECT (
                SELECT first_name
                FROM employee
                WHERE id_employee = (
                    SELECT id_employee
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop> 
                )
            ) AS [first_name],
            (
                SELECT last_name
                FROM employee
                WHERE id_employee = (
                    SELECT id_employee
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop> 
                )
            ) AS [last_name],
            (
                SELECT start_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop> 
                )
            ) AS [start_time],
            (
                SELECT end_time
                FROM schedule_shift_daypart
                WHERE id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop> 
                )
            ) AS [end_time],
            (
                SELECT calendar_date
                FROM daily_employee_calendar
                WHERE id_employee = (
                    SELECT id_employee
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop> 
                ) AND id_shift_daypart = (
                    SELECT id_shift_daypart
                    FROM pending_drop
                    WHERE id_pending_drop = <id_pending_drop> 
                )
            ) AS [calendar_date],
            request_sent_date
            FROM pending_drop
            WHERE id_pending_drop = <id_pending_drop> 

        """
        query = query.replace("<id_pending_drop>", id_pending_drop)

        cursor.execute(query)
        for row in cursor.fetchall():
            shift = {
                "first_name": row[0],
                "last_name": row[1],
                "start_time": row[2].strftime("%I:%M %p") if row[2] is not None else 'N/A',
                "end_time": row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                "date": row[4].strftime("%m/%d/%Y") if row[4] is not None else 'N/A',
                "request_sent_date": row[5].strftime("%m/%d/%Y") if row[5] is not None else 'N/A',
            }
            data.append(shift)
        return data, 200

# updates status of id_pending_drop to status in pending_drop table


class updateDropRequest(Resource):
    def post(self, status, id_pending_drop):
        query = """
            UPDATE pending_drop
            SET status_code = <status>, request_sent_date = GETDATE()
            WHERE id_pending_drop = <id_pending_drop>
        """
        query = query.replace("<status>", status)
        query = query.replace("<id_pending_drop>", id_pending_drop)
        cursor.execute(query)
        cnxn.commit()
        return 200

# updates existing drop request of id_pending_drop in notifications table


class updateDropNotification(Resource):
    def post(self, status, id_pending_drop):
        query = """
            UPDATE notification
            SET response = <status>, sent_time = GETDATE()
            WHERE msg = <id_pending_drop> AND sent_to = 'Drop'
        """
        query = query.replace("<status>", status)
        query = query.replace("<id_pending_drop>", id_pending_drop)

        cursor.execute(query)
        cnxn.commit()
        return 200


class getVacationDays(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT total_vacation_hours 
            FROM employee 
            WHERE id_employee = <id_employee> 

        """
        query = query.replace("<id_employee>", id_employee)
        cursor.execute(query)

        for row in cursor.fetchall():
            hours = {
                "vacation_hours": "{0:0.1f}".format(row[0]),
            }
            data.append(hours)

        cnxn.commit()
        return data, 200


# Adds vacation request to pending_vacation table
class requestVacation(Resource):
    def post(self, id_employee, start_date, end_date, num_days):
        data = []
        # convert dates to proper format
        startDate = datetime.fromtimestamp(
            int(start_date)).strftime("%Y-%m-%d")
        endDate = datetime.fromtimestamp(int(end_date)).strftime("%Y-%m-%d")
        query = """
            INSERT INTO pending_vacation(id_employee, start_date, end_date, duration, status_code)
            OUTPUT inserted.id_pending_vacation
            VALUES (
                <id_employee>,
                CONVERT(date, ? ),
                CONVERT(date, ? ),
                <num_days>,
                'pending'
            )
        """
        query = query.replace("<id_employee>", id_employee)
        query = query.replace("<num_days>", num_days)
        cursor.execute(query, (startDate, endDate))

        for row in cursor.fetchall():
            idPending = {
                "id_pending_vacation": row[0],
            }
            data.append(idPending)

        cnxn.commit()
        return data, 200

# inserts pending vacation request into notifications table by id_pending_vacation


class SetVacationNotification(Resource):
    def post(self, id_employee, id_pending_vacation):
        query = """
            INSERT INTO notification(sent_to, sent_from, msg, response, sent_time)
            VALUES ('Vacation', <id_employee>, <id_pending_vacation>, 'pending', GETDATE())

         """
        # need to replace each of the attributes with something more friendly
        query = query.replace("<id_employee>", str(id_employee))
        query = query.replace("<id_pending_vacation>",
                              str(id_pending_vacation))
        cursor.execute(query)
        cnxn.commit()

        return 200

# Gets all information associated with a pending vacation request of id_pending_vacation


class getPendingVacation(Resource):
    def get(self, id_pending_vacation):
        data = []
        query = """
            SELECT start_date, end_date, duration
            FROM pending_vacation
            WHERE id_pending_vacation = <id_pending_vacation>
        """
        query = query.replace("<id_pending_vacation>", id_pending_vacation)

        cursor.execute(query)
        for row in cursor.fetchall():
            vacation = {
                "start_date": row[0].strftime("%m/%d/%Y") if row[0] is not None else 'N/A',
                "end_date": row[1].strftime("%m/%d/%Y") if row[1] is not None else 'N/A',
                "num_days": row[2],
            }
            data.append(vacation)
        return data, 200

# This gets all pending vacation shift ids for admin to approve


class getAllPendingVacationIDs(Resource):
    def get(self):
        data = []
        query = """
            SELECT id_pending_vacation
            FROM pending_vacation
            WHERE status_code = 'pending'        
        """
        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_vacation": row[0]
            }
            data.append(id_drop)
        return data, 200

# Gets all information associated with a pending vacation request of id_pending_vacation


class getAllPendingVacation(Resource):
    def get(self, id_pending_vacation):
        data = []
        query = """
            SELECT (
                SELECT first_name
                FROM employee
                WHERE id_employee = (
                    SELECT id_employee
                    FROM pending_vacation
                    WHERE id_pending_vacation = <id_pending_vacation>
                )
            ) AS [first_name],
            (
                SELECT last_name
                FROM employee
                WHERE id_employee = (
                    SELECT id_employee
                    FROM pending_vacation
                    WHERE id_pending_vacation = <id_pending_vacation>
                )
            ) AS [last_name],
            ( SELECT start_date
                FROM pending_vacation
                WHERE id_pending_vacation = <id_pending_vacation>
            ), 
            ( SELECT end_date
                FROM pending_vacation
                WHERE id_pending_vacation = <id_pending_vacation>
            ), 
            ( SELECT duration
                FROM pending_vacation
                WHERE id_pending_vacation = <id_pending_vacation>
            )

        """
        query = query.replace("<id_pending_vacation>", id_pending_vacation)

        cursor.execute(query)
        for row in cursor.fetchall():
            vacation = {
                "first_name": row[0],
                "last_name": row[1],
                "start_date": row[2].strftime("%m/%d/%Y") if row[2] is not None else 'N/A',
                "end_date": row[3].strftime("%m/%d/%Y") if row[3] is not None else 'N/A',
                "num_days": row[4],
            }
            data.append(vacation)
        return data, 200

#This gets all pending vacation requests as requested by employee #


class getPendingVacationIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_vacation
            FROM pending_vacation
            WHERE id_employee = <id_employee> AND status_code = 'pending'        
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_vacation": row[0]
            }
            data.append(id_drop)
        return data, 200

#This gets all approved vacation requests as requested by employee #


class getApprovedVacation(Resource):
    def get(self, id_pending_vacation):
        data = []
        query = """
            SELECT start_date, end_date, duration
            FROM pending_vacation
            WHERE id_pending_vacation = <id_pending_vacation>
        """
        query = query.replace("<id_pending_vacation>", id_pending_vacation)

        cursor.execute(query)
        for row in cursor.fetchall():
            vacation = {
                "start_date": row[0].strftime("%m/%d/%Y") if row[0] is not None else 'N/A',
                "end_date": row[1].strftime("%m/%d/%Y") if row[1] is not None else 'N/A',
                "num_days": row[2],
            }
            data.append(vacation)
        return data, 200

# Given an id_employee, gets id_pending_vacation of all approved vacation requests


class getApprovedVacationIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_vacation
            FROM pending_vacation
            WHERE id_employee = <id_employee> AND status_code = 'approved'        
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_vacation": row[0]
            }
            data.append(id_drop)
        return data, 200

# Given an id_employee, gets id_pending_vacation of all denied vacation requests


class getDeniedVacation(Resource):
    def get(self, id_pending_vacation):
        data = []
        query = """
            SELECT start_date, end_date, duration
            FROM pending_vacation
            WHERE id_pending_vacation = <id_pending_vacation>
        """
        query = query.replace("<id_pending_vacation>", id_pending_vacation)

        cursor.execute(query)
        for row in cursor.fetchall():
            vacation = {
                "start_date": row[0].strftime("%m/%d/%Y") if row[0] is not None else 'N/A',
                "end_date": row[1].strftime("%m/%d/%Y") if row[1] is not None else 'N/A',
                "num_days": row[2],
            }
            data.append(vacation)
        return data, 200


# Given an id_employee, gets id_pending_vacation of all denied vacation requests
class getDeniedVacationIDs(Resource):
    def get(self, id_employee):
        data = []
        query = """
            SELECT id_pending_vacation
            FROM pending_vacation
            WHERE id_employee = <id_employee> AND status_code = 'denied'        
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        for row in cursor.fetchall():
            id_drop = {
                "id_pending_vacation": row[0]
            }
            data.append(id_drop)
        return data, 200

# updates status of id_pending_vacation to 'status' in pending_vacation table


class updateVacationRequest(Resource):
    def post(self, status, id_pending_vacation):
        query = """
            UPDATE pending_vacation
            SET status_code = <status>
            WHERE id_pending_vacation = <id_pending_vacation>
        """
        query = query.replace("<status>", status)
        query = query.replace("<id_pending_vacation>", id_pending_vacation)
        cursor.execute(query)
        cnxn.commit()
        return 200

# updates existing id_pending_vacation request to 'status' in notifications table


class updateVacationNotification(Resource):
    def post(self, status, id_pending_vacation):
        query = """
            UPDATE notification
            SET response = <status>, sent_time = GETDATE()
            WHERE msg = <id_pending_vacation> AND sent_to = 'Vacation'
        """
        query = query.replace("<status>", status)
        query = query.replace("<id_pending_vacation>", id_pending_vacation)

        cursor.execute(query)
        cnxn.commit()
        return 200

class change(Resource):
    def post(self, id_employee, num_days):
        query = """
            UPDATE employee
            SET remaining_vacation = (remaining_vacation - <num_days> )
            WHERE id_employee = <id_employee>
        """
        query = query.replace("<id_employee>", id_employee)
        query = query.replace("<num_days>", num_days)

        cursor.execute(query)

        cnxn.commit()

        return 200


# inserts custom message into notifications table
class SetMsgNotification(Resource):
    def post(self, id_role, message):
        query = """
            INSERT INTO notification(sent_to, sent_from, msg, response, sent_time)
            VALUES ('Message', <id_role> , <message> , NULL , GETDATE())

         """
        # need to replace each of the attributes with something more friendly
        query = query.replace("<id_role>", str(id_role))
        query = query.replace("<message>", str(message))
        cursor.execute(query)
        cnxn.commit()

        return 200

# gets all custom messages for a certain id_role


class getMsgNotification(Resource):
    def get(self, id_role):
        query = """
            SELECT msg
            FROM notification
            WHERE sent_to = 'Message' AND sent_from = <id_role> 
        """

        query = query.replace("<id_role>", id_role)

        cursor.execute(query)
        data = []
        for row in cursor.fetchall():
            msg = {
                "message": row[0]
            }
            data.append(msg)
        return data, 200

# deletes all entries from daily_employee_calendar


class WipeDEC(Resource):
    def post(self):
        query = """
            DELETE FROM daily_employee_calendar
            WHERE id_calendar > 1;
        """
        cursor.execute(query)
        cnxn.commit()

        return 200

# Gets id_shifts of all employees associated with an id_role


class MasterCalIDs(Resource):
    def get(self, id_role):
        query = """
            SELECT id_shift
            FROM schedule_shift
            WHERE id_role = <id_role>
        """
        data = []
        query = query.replace("<id_role>", id_role)

        cursor.execute(query)
        for row in cursor.fetchall():
            ids = {
                "id_shift": row[0]
            }
            data.append(ids)
        return data, 200

#Given an id_shift and shift_time (PT or FT) returns information associated with that shift found in schedule_shift_daypart table 
class MasterCalShifts(Resource):
    def get(self, id_shift, shift_time):
        
        if shift_time == "1":
            query = """
                SELECT id_shift_daypart, day_of_week, first_or_second_code, start_time, end_time
                FROM schedule_shift_daypart
                WHERE first_or_second_code = 'FIRST' AND id_shift = <id_shift>
            """        
            query = query.replace("<id_shift>", id_shift)
      
            cursor.execute(query)
            data = []
            for row in cursor.fetchall():
                shifts = {
                    "id_shift_daypart": row[0],
                    "day_of_week": row[1],
                    "first_or_second": row[2],
                    "start_time": row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                    "end_time": row[4].strftime("%I:%M %p") if row[4] is not None else 'N/A',
                }
                data.append(shifts)
            return data, 200

        elif shift_time == "2":
            query = """
                SELECT id_shift_daypart, day_of_week, first_or_second_code, start_time, end_time
                FROM schedule_shift_daypart
                WHERE first_or_second_code = 'SECOND' AND id_shift = <id_shift>
            """
            query = query.replace("<id_shift>", id_shift)
            cursor.execute(query)
            data = []
            for row in cursor.fetchall():
                shifts = {
                    "id_shift_daypart": row[0],
                    "day_of_week": row[1],
                    "first_or_second": row[2],
                    "start_time": row[3].strftime("%I:%M %p") if row[3] is not None else 'N/A',
                    "end_time": row[4].strftime("%I:%M %p") if row[4] is not None else 'N/A',
                }
                data.append(shifts)
            return data, 200

# Given all information associated with a shift from, returns all employees working that shift in daily_employee_calendar


class MasterCalEmp(Resource):
    def get(self, id_shift_daypart, day_of_week, first_or_second_code, start_time, end_time, date):
        date = int(date) / 1000
        dateFormatted = datetime.fromtimestamp(date).strftime("%Y-%m-%d")
        dateFormatted = datetime.strptime(dateFormatted, "%Y-%m-%d")
        query = """
            SELECT id_employee, last_name, first_name 
            FROM employee
            WHERE id_employee IN (
                SELECT id_employee
                FROM daily_employee_calendar
                WHERE id_shift_daypart = <id_shift_daypart> AND status != 'Dropped' AND calendar_date = ?
            )
        """
        query = query.replace("<id_shift_daypart>", id_shift_daypart)

        cursor.execute(query, (dateFormatted,))

        data = []
        for row in cursor.fetchall():
            shifts = {
                "id_employee": row[0],
                "last_name": row[1],
                "first_name": row[2],
                "day_of_week": day_of_week,
                "first_or_second": first_or_second_code,
                "start_time": start_time, 
                "end_time": end_time,
                "shift_date": dateFormatted.strftime("%m/%d/%Y"),

            }
            data.append(shifts)
        return data, 200

#gets all id_shifts, used to reset all the max employee values for each shift 
class resetMaxEmployeesIDS(Resource): 
    def get(self):
        query = """
            SELECT id_shift
            FROM schedule_shift
        """
        cursor.execute(query)
        data = []
        for row in cursor.fetchall():
            ids = {
                "id_shift": row[0],
            }
            data.append(ids)
        return data, 200

#resets max number of employees who can work a certain shift 
class resetMaxEmployees(Resource):
    def post(self, id_shift):
        query = """
            UPDATE schedule_shift_daypart
            SET max_employees = (
                SELECT max_emps_per_shift
                FROM schedule_shift
                WHERE id_shift IN (
                    SELECT id_shift
                    FROM schedule_shift_daypart
                    WHERE id_shift = <id_shift>
                )
            )
            WHERE id_shift = <id_shift>
        """
        query = query.replace("<id_shift>", id_shift)
        
        cursor.execute(query)
        cnxn.commit()

        return 200

#Updates the date of each shift to that of the upcoming week 
class updateShiftDates(Resource):
    def post(self):
        query = """
            UPDATE schedule_shift_daypart
            SET shift_date = DATEADD(day, 7, shift_date)
        """
        cursor.execute(query)
        cnxn.commit()

        return 200

class getEmailandPhone(Resource):
    def get(self, id_employee):
        query = """
            SELECT last_name, first_name, email_address, phone_number
            FROM employee
            WHERE id_employee = <id_employee>
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)

        data = []
        for row in cursor.fetchall():
            contact = {
                "last_name": row[0],
                "first_name": row[1],
                "email_address": row[2],
                "phone_number": row[3],
            }
            data.append(contact)
        return data, 200


class CheckIfEmployee(Resource):
    def get(self, id_employee):
        query = """
            SELECT id_employee
            FROM employee
            WHERE id_employee = <id_employee>
        """

        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)

        employee = cursor.fetchall()

        if(employee):
            query = """
                SELECT *
                FROM employee_password
                WHERE id_employee = <id_employee>
            """

            query = query.replace("<id_employee>", id_employee)

            cursor.execute(query)

            employee = cursor.fetchall()

            if(employee):
                response = {
                    "validEmployee": True,
                    "registered": True
                }
                return response, 200
            else:
                response = {
                    "validEmployee": True,
                    "registered": False
                }
                return response, 200

        else:
            response = {
                "validEmployee": False,
                "registered": False
            }
            return response, 200


class Register(Resource):
    def post(self, password, phone, email, id_employee):
        query = """
            UPDATE employee
            SET phone_number = '<phone>', email_address = '<email>', user_type = '1'
            WHERE id_employee = <id_employee>
        """

        password = hashlib.sha256(
            ('preproductionsalt' + password).encode('utf-8')).hexdigest()
        query = query.replace("<phone>", phone)
        query = query.replace("<email>", email)
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        cnxn.commit()

        query = """
            INSERT INTO employee_password (id_employee, password_string)
            VALUES ('<id_employee>', '<password>')
        """
        query = query.replace("<password>", password)
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)
        cnxn.commit()

        return 200


class Login(Resource):
    def get(self, password, id_employee):
        query = """
            SELECT password_string
            FROM employee_password
            WHERE id_employee = <id_employee>
        """
        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)

        data = cursor.fetchall()

        if not data:
            return 0, 200

        password = hashlib.sha256(
            ('preproductionsalt' + password).encode('utf-8')).hexdigest()

        response = 0

        if password == data[0][0]:
            print("here")
            response = 1

            query = """
                INSERT INTO active_login (id_employee, session_key)
                VALUES ('<id_employee>', '<session_key>')
            """

            query = query.replace("<id_employee>", id_employee)
            query = query.replace("<session_key>", hashlib.sha256((
                'sessionkeysalt' + id_employee).encode('utf-8')).hexdigest())

            cursor.execute(query)
            cnxn.commit()

            query = """
                UPDATE employee
                SET active_ind = 'Y'
                WHERE id_employee = <id_employee>
            """

            query = query.replace("<id_employee>", id_employee)

            cursor.execute(query)
            cnxn.commit()

        else:
            response = 0

        return response, 200


class GetUserData(Resource):
    def get(self, id_employee):
        query = """
            SELECT first_name, last_name, part_time_ind, role_name, id_role, user_type, phone_number, email_address
            FROM employee
            WHERE id_employee = '<id_employee>'
        """

        query = query.replace("<id_employee>", id_employee)

        cursor.execute(query)

        data = cursor.fetchall()

        response = {
            "first_name": data[0][0],
            "last_name": data[0][1],
            "part_time_ind": data[0][2],
            "role_name": data[0][3],
            "id_role": data[0][4],
            "user_type": data[0][5],
            "phone": data[0][6],
            "email": data[0][7]
        }

        return response, 200


api.add_resource(GetUserData, '/getuserdata/<string:id_employee>')
api.add_resource(Login, '/login/<string:password>/<string:id_employee>')
api.add_resource(
    Register, '/register/<string:password>/<string:phone>/<string:email>/<string:id_employee>')
api.add_resource(CheckIfEmployee, '/checkifemployee/<string:id_employee>')

# Schedule Shift APIs
api.add_resource(
    Schedule, '/schedule/<string:shift_code>')
api.add_resource(
    GetShifts, '/getshifts/<string:id_employee>')
api.add_resource(
    SetShifts, '/setshifts/<string:id_employee>/<string:id_shift_daypart>')

# My shift APIs
api.add_resource(
    MyShiftIDs, '/myshiftids/<string:id_employee>')
api.add_resource(
    MyShifts, '/myshifts/<string:id_calendar>')

# NOT USED
api.add_resource(
    GetUser, '/getuser/<string:employee_code>')

# Drop shift APIS
api.add_resource(
    Drop, '/drop/<string:id_employee>/<string:id_shift_daypart>')

api.add_resource(
    SetPendingDrop, '/setpendingdrop/<string:id_employee>/<string:id_shift_daypart>')
api.add_resource(
    SetDropNotification, '/setdropnotification/<string:id_employee>/<string:id_pending_drop>')
api.add_resource(
    getPendingDrop, '/getpendingdrop/<string:id_pending_drop>')
api.add_resource(
    getPendingDropIDs, '/getpendingdropids/<string:id_employee>')

api.add_resource(
    getDeniedDrop, '/getdenieddrop/<string:id_pending_drop>')
api.add_resource(
    getDeniedDropIDs, '/getdenieddropids/<string:id_employee>')

api.add_resource(
    getApprovedDrop, '/getapproveddrop/<string:id_pending_drop>')
api.add_resource(
    getApprovedDropIDs, '/getapproveddropids/<string:id_employee>')

api.add_resource(
    getAllPendingDrops, '/getallpendingdrops/<string:id_pending_drop>')
api.add_resource(
    getAllPendingDropIDs, '/getallpendingdropids')

api.add_resource(
    updateDropRequest, '/updatedroprequest/<string:status>/<string:id_pending_drop>')
api.add_resource(
    updateDropNotification, '/updatedropnotification/<string:status>/<string:id_pending_drop>')


# Swap shift APIS
api.add_resource(
    Swap, '/swap/<string:from_id_employee>/<string:from_id_shift_daypart>/<string:to_id_employee>/<string:to_id_shift_daypart>')

api.add_resource(
    SetSwapNotification, '/setswapnotification/<string:id_employee>/<string:id_pending_swap>')
api.add_resource(
    SetPendingSwap, '/setpendingswap/<string:from_id_employee>/<string:from_id_shift_daypart>/<string:to_id_employee>/<string:to_id_shift_daypart>')
api.add_resource(
    getSwapEmp, '/getswapemp/<string:id_employee>/<string:id_shift_daypart>')

api.add_resource(
    getSwapShiftIDs, '/getswapshiftids/<string:from_id_employee>/<string:to_id_employee>')
api.add_resource(
    getSwapShifts, '/getswapshifts/<string:id_calendar>')

api.add_resource(
    getPendingSwap, '/getpendingswap/<string:id_pending_swap>')
api.add_resource(
    getPendingSwapIDs, '/getpendingswapids/<string:id_employee>')

api.add_resource(
    getApprovedSwap, '/getapprovedswap/<string:id_pending_swap>')
api.add_resource(
    getApprovedSwapIDs, '/getapprovedswapids/<string:id_employee>')

api.add_resource(
    getAllDeniedSwaps, '/getalldeniedswaps/<string:id_pending_swap>')
api.add_resource(
    getAllDeniedSwapIDs, '/getalldeniedswapids/<string:id_employee>')

api.add_resource(
    getPendingSwapsToApprove, '/getpendingswapstoapprove/<string:id_pending_swap>')
api.add_resource(
    getPendingSwapsToApproveIDs, '/getpendingswapstoapproveids/<string:id_employee>')

api.add_resource(
    updateSwapRequest, '/updateswaprequest/<string:status>/<string:id_pending_swap>')
api.add_resource(
    updateSwapNotification, '/updateswapnotification/<string:status>/<string:id_pending_swap>')

# NOT USED
api.add_resource(
    getOpenSwapsToApprove, '/getopenswapstoapprove/<string:id_pending_swap>')
api.add_resource(
    getOpenSwapsToApproveIDs, '/getopenswapstoapproveids/<string:id_employee>')


# Vacation Request APIs
api.add_resource(getVacationDays, '/getvacationdays/<string:id_employee>')
api.add_resource(
    requestVacation, '/requestvacation/<string:id_employee>/<string:start_date>/<string:end_date>/<string:num_days>')
api.add_resource(
    updateVacationDays, '/updatevacationdays/<string:id_employee>/<string:num_days>')

api.add_resource(
    SetVacationNotification, '/setvacationnotification/<string:id_employee>/<string:id_pending_vacation>')

api.add_resource(
    getPendingVacation, '/getpendingvacation/<string:id_pending_vacation>')
api.add_resource(
    getPendingVacationIDs, '/getpendingvacationids/<string:id_employee>')

api.add_resource(
    getApprovedVacation, '/getapprovedvacation/<string:id_pending_vacation>')
api.add_resource(
    getApprovedVacationIDs, '/getapprovedvacationids/<string:id_employee>')

api.add_resource(
    getDeniedVacation, '/getdeniedvacation/<string:id_pending_vacation>')
api.add_resource(
    getDeniedVacationIDs, '/getdeniedvacationids/<string:id_employee>')

api.add_resource(
    getAllPendingVacation, '/getallpendingvacation/<string:id_pending_vacation>')
api.add_resource(
    getAllPendingVacationIDs, '/getallpendingvacationids')

api.add_resource(
    updateVacationRequest, '/updatevacationrequest/<string:status>/<string:id_pending_vacation>')
api.add_resource(
    updateVacationNotification, '/updatevacationnotification/<string:status>/<string:id_pending_vacation>')

# Master Calendar APIs
api.add_resource(
    MasterCalShifts, '/mastercalshifts/<string:id_shift>/<string:shift_time>')
api.add_resource(
    MasterCalIDs, '/mastercalids/<string:id_role>')

api.add_resource(
    MasterCalEmp, '/mastercalemp/<string:id_shift_daypart>/<string:day_of_week>/<string:first_or_second_code>/<string:start_time>/<string:end_time>/<string:date>')

#Reset Max Employees API 
api.add_resource( resetMaxEmployees, '/resetmaxemployees/<string:id_shift>')
api.add_resource( resetMaxEmployeesIDS, '/resetmaxemployeesids')

api.add_resource( updateShiftDates, '/updateshiftdates')

# Custom messaging APIs
api.add_resource(
    SetMsgNotification, '/setmsgnotification/<string:id_role>/<string:message>')
api.add_resource(
    getMsgNotification, '/getmsgnotification/<string:id_role>')

api.add_resource(
    getEmailandPhone, '/getemailandphone/<string:id_employee>')

api.add_resource(WipeDEC, '/wipeDEC')
if __name__ == '__main__':
    app.run(debug=True)
