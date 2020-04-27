from twilio.rest import Client
import random
import string

# fail safe vLj1kTX0RjqB_vl4rIuZAx_E8dOlTVkt2Q1AAfKa

account_sid = 'AC28c93597da66f1a4c29b371d04b474e5'
auth_token = '4fc720f3a7390fddfbee3e4d43cc1593'
client = Client(account_sid, auth_token)

from_num = '+13133074651'
to_num = ''


def drop_text(shiftDate, shiftStart, shiftEnd, dropID, receiver_num):
    if dropID == 0:
        msg = "Your request to drop shift <shiftDate> <shiftStart> - <shiftEnd> has been approved. \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
        msg = msg.replace("<shiftDate>", shiftDate).replace(
            "<shiftStart>", shiftStart).replace("<shiftEnd>", shiftEnd)

    elif dropID == 1:
        msg = "Your request to drop shift <shiftDate> <shiftStart> - <shiftEnd> has been denied. \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
        msg = msg.replace("<shiftDate>", shiftDate).replace(
            "<shiftStart>", shiftStart).replace("<shiftEnd>", shiftEnd)

    message = client.messages \
        .create(
            body=msg,
            from_=from_num,
            to=receiver_num
        )

    print(message.sid)


def swap_text(shiftDate1, shiftStart1, shiftEnd1, shiftDate2, shiftStart2, shiftEnd2, swapID, receiver_num):
    if swapID == 0:
        msg = "Your request to swap shift <shiftDate1> <shiftStart1> - <shiftEnd1> for shift <shiftDate2> <shiftStart2> - <shiftEnd2> has been approved. \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
        msg = msg.replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace(
            "<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)
    elif swapID == 1:
        msg = "Your request to swap shift <shiftDate1> <shiftStart1> - <shiftEnd1> for shift <shiftDate2> <shiftStart2> - <shiftEnd2> has been denied. \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
        msg = msg.replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace(
            "<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)

    message = client.messages \
        .create(
            body=msg,
            from_=from_num,
            to=receiver_num
        )

    print(message.sid)


def vacation_text(shiftDate1, shiftDate2, vacID, receiver_num):
    if vacID == 0:
        msg = "Your vacation request for dates <shiftDate1> - <shiftDate2> has been approved. \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
        msg = msg.replace("<shiftDate1>", shiftDate1).replace(
            "<shiftDate2>", shiftDate2)
    elif vacID == 1:
        msg = "Your vacation request for dates <shiftDate1> - <shiftDate2> has been denied. \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
        msg = msg.replace("<shiftDate1>", shiftDate1).replace(
            "<shiftDate2>", shiftDate2)

    message = client.messages \
        .create(
            body=msg,
            from_=from_num,
            to=receiver_num
        )

    print(message.sid)


def swap_emp_text(shiftDate1, shiftStart1, shiftEnd1, shiftDate2, shiftStart2, shiftEnd2, empName, receiver_num):
    msg = "<empName> has requested to swap their shift: <shiftDate1> <shiftStart1> - <shiftEnd1> for your shift: <shiftDate2> <shiftStart2> - <shiftEnd2>. \n\nPlease log into the website to accept or deny this request. This message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
    msg = msg.replace("<empName>", empName).replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace(
        "<shiftEnd1>", shiftEnd1).replace("<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)

    message = client.messages \
        .create(
            body=msg,
            from_=from_num,
            to=receiver_num
        )

    print(message.sid)


def swap_type_text(shiftDate1, shiftStart1, shiftEnd1, shiftType, empName, receiver_num):
    msg = "<empName> has requested to swap their shift <shiftDate1> <shiftStart1> - <shiftEnd1> for any of your <shiftType> shifts. Please log into the website to accept or deny this request. \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
    msg = msg.replace("<empName>", empName).replace("<shiftDate1>", shiftDate1).replace(
        "<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace("<shiftType>", shiftType)

    message = client.messages \
        .create(
            body=msg,
            from_=from_num,
            to=receiver_num
        )

    print(message.sid)


def custom_text(customSub, customMes, receiver_num):
    msg = "<custMsg> \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
    msg = msg.replace("<custMsg>", customMes)

    message = client.messages \
        .create(
            body=msg,
            from_=from_num,
            to=receiver_num
        )

    print(message.sid)


def verify_text(receiver_email):

    digs = string.digits
    code = "".join(random.choice(digs) for i in range(8))

    msg = "Confirm the text verification process by entering the following code into the 'Secure Code' field in your browser: <code> \n\nThis message is automated so please do not reply to this message. If you have any questions, please contact HR or management."
    msg = msg.replace("<code>", code)

    message = client.messages \
        .create(
            body=msg,
            from_=from_num,
            to=receiver_email
        )

    print(message.sid)