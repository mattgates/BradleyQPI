import smtplib
import ssl
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "qpicapstone2020@gmail.com"  # Enter your address
receiver_email = ["QPIProductionApp@gmail.com",
    "qpicapstone2020@gmail.com"]  # Enter receiver address
password = "QPIBradley2020"  # input("Type your password and press enter: ")

# Date will come as day of week starting at Thursday = 0
# Just add number attached to day of week to date()


def drop_email(shiftDate, shiftStart, shiftEnd, dropID, receiver_email):

  if dropID == 0:
    subject = "Drop Shift Request has been Approved"
    text = """\
      Your request to drop shift <shiftDate> <shiftStart> - <shiftEnd> has been approved.

      This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
      """
    html = """\
    <html>
      <body>
        <p>Your request to drop shift <shiftDate> <shiftStart> - <shiftEnd> has been approved.
        <br>
        <br>
        <br>
        <br>
        <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
        <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
        <br>
        </p>
      </body>
    </html>
    """

    text = text.replace("<shiftDate>", shiftDate).replace(
        "<shiftStart>", shiftStart).replace("<shiftEnd>", shiftEnd)
    html = html.replace("<shiftDate>", shiftDate).replace(
        "<shiftStart>", shiftStart).replace("<shiftEnd>", shiftEnd)

  elif dropID == 1:
    subject = "Drop Shift Request has been Denied"
    text = """\
      Your request to drop shift <shiftDate> <shiftStart> - <shiftEnd> has been denied.

      This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
      """
    html = """\
    <html>
      <body>
        <p>Your request to drop shift <shiftDate> <shiftStart> - <shiftEnd> has been denied.
        <br>
        <br>
        <br>
        <br>
        <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
        <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
        <br>
        </p>
      </body>
    </html>
    """

    text = text.replace("<shiftDate>", shiftDate).replace(
        "<shiftStart>", shiftStart).replace("<shiftEnd>", shiftEnd)
    html = html.replace("<shiftDate>", shiftDate).replace(
        "<shiftStart>", shiftStart).replace("<shiftEnd>", shiftEnd)

  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email


# Turn these into plain/html MIMEText objects
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())


def swap_email(shiftDate1, shiftStart1, shiftEnd1, shiftDate2, shiftStart2, shiftEnd2, swapID, receiver_email):

  if swapID == 0:
    subject = "Swap Shift Request has been Approved"

    text = """\
      Your request to swap shift <shiftDate1> <shiftStart1> - <shiftEnd1> for shift <shiftDate2> <shiftStart2> - <shiftEnd2> has been approved.

      This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
      """
    html = """\
    <html>
      <body>
        <p>Your request to swap shift <shiftDate1> <shiftStart1> - <shiftEnd1> for shift <shiftDate2> <shiftStart2> - <shiftEnd2> has been approved.
        <br>
        <br>
        <br>
        <br>
        <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
        <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
        <br>
        </p>
      </body>
    </html>
    """
    text = text.replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace(
        "<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)
    html = html.replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace(
        "<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)
  elif swapID == 1:
    subject = "Swap Shift Request has been Denied"

    text = """\
      Your request to swap shift <shiftDate1> <shiftStart1> - <shiftEnd1> for shift <shiftDate2> <shiftStart2> - <shiftEnd2> has been denied.

      This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
      """
    html = """\
    <html>
      <body>
        <p>Your request to swap shift <shiftDate1> <shiftStart1> - <shiftEnd1> for shift <shiftDate2> <shiftStart2> - <shiftEnd2> has been denied.
        <br>
        <br>
        <br>
        <br>
        <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
        <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
        <br>
        </p>
      </body>
    </html>
    """
    text = text.replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace(
        "<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)
    html = html.replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace(
        "<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)

  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())


def vacation_email(shiftDate1, shiftDate2, vacID, receiver_email):
  if vacID == 0:
    subject = "Vacation Request has been Approved"

    text = """\
	    Your vacation request for dates <shiftDate1> - <shiftDate2> has been approved.

      This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
      """
    html = """\
    <html>
      <body>
        <p>Your vacation request for dates <shiftDate1> - <shiftDate2> has been approved.
        <br>
        <br>
        <br>
        <br>
        <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
        <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
        <br>
        </p>
      </body>
    </html>
    """
    text = text.replace("<shiftDate1>", shiftDate1).replace(
        "<shiftDate2>", shiftDate2)
    html = html.replace("<shiftDate1>", shiftDate1).replace(
        "<shiftDate2>", shiftDate2)
  elif vacID == 1:
    subject = "Vacation Request has been Denied"

    text = """\
	    Your vacation request for dates <shiftDate1> - <shiftDate2> has been denied.

      This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
      """
    html = """\
    <html>
      <body>
        <p>Your vacation request for dates <shiftDate1> - <shiftDate2> has been denied.
        <br>
        <br>
        <br>
        <br>
        <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
        <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
        <br>
        </p>
      </body>
    </html>0
    """
    text = text.replace("<shiftDate1>", shiftDate1).replace(
        "<shiftDate2>", shiftDate2)
    html = html.replace("<shiftDate1>", shiftDate1).replace(
        "<shiftDate2>", shiftDate2)

  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())


def swap_emp_email(shiftDate1, shiftStart1, shiftEnd1, shiftDate2, shiftStart2, shiftEnd2, empName, receiver_email):
  subject = "Shift Swap has been Requested"

  text = """\
	  <empName> has requested to swap their shift: <shiftDate1> <shiftStart1> - <shiftEnd1> for your shift: <shiftDate2> <shiftStart2> - <shiftEnd2>.

    Please log into the website to accept or deny this request.

    This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
    """
  html = """\
  <html>
    <body>
      <p><empName> has requested to swap their shift <shiftDate1> <shiftStart1> - <shiftEnd1> for your shift <shiftDate2> <shiftStart2> - <shiftEnd2>.
      <br>
      <br>
      <u><b>Please log into the website to accept or deny this request.</b></u>
      <br>
      <br>
      <br>
      <br>
      <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
      <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
      <br>
      </p>
    </body>
  </html>
  """

  text = text.replace("<empName>", empName).replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace(
      "<shiftEnd1>", shiftEnd1).replace("<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)
  html = html.replace("<empName>", empName).replace("<shiftDate1>", shiftDate1).replace("<shiftStart1>", shiftStart1).replace(
      "<shiftEnd1>", shiftEnd1).replace("<shiftDate2>", shiftDate2).replace("<shiftStart2>", shiftStart2).replace("<shiftEnd2>", shiftEnd2)

  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())


def swap_type_email(shiftDate1, shiftStart1, shiftEnd1, shiftType, empName, receiver_email):
  subject = "Shift Swap has been Requested"

  text = """\
	  <empName> has requested to swap their shift <shiftDate1> <shiftStart1> - <shiftEnd1> for any of your <shiftType> shifts.

    Please log into the website to accept or deny this request.

    This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
    """
  html = """\
  <html>
    <body>
      <p><empName> has requested to swap their shift <shiftDate1> <shiftStart1> - <shiftEnd1> for any of your <shiftType> shifts.
      <br>
      <br>
      <u><b>Please log into the website to accept or deny this request.</b></u>
      <br>
      <br>
      <br>
      <br>
      <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
      <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
      <br>
      </p>
    </body>
  </html>
  """

  text = text.replace("<empName>", empName).replace("<shiftDate1>", shiftDate1).replace(
      "<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace("<shiftType>", shiftType)
  html = html.replace("<empName>", empName).replace("<shiftDate1>", shiftDate1).replace(
      "<shiftStart1>", shiftStart1).replace("<shiftEnd1>", shiftEnd1).replace("<shiftType>", shiftType)

  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())


def custom_email(customSub, customMes, receiver_email):
  subject = customSub

  text = """\
	<custMsg>

  This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
  """
  html = """\
  <html>
    <body>
      <p><custMsg>
      <br>
      <br>
      <br>
      <br>
      <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
      <br>
      <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
      </p>
    </body>
  </html>
  """

  text = text.replace("<custMsg>", customMes)
  html = html.replace("<custMsg>", customMes)

  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())


def verify_email(receiver_email):

  digs = string.digits
  code = "".join(random.choice(digs) for i in range(1, 9))

  subject = "Verify your Email Address"
  text = """\
      Confirm the email verification process by entering the following code into the 'Secure Code' field in your browser:
        <code>

      This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
      """
  html = """\
    <html>
      <body>
        <p>Confirm the email verification process by entering the following code into the 'Secure Code' field in your browser:
        <br>
        <p><code></p>
        <br>
        <br>
        <br>
        <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
        <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
        <br>
        </p>
      </body>
    </html>
    """

  text = text.replace("<code>", code)
  html = html.replace("<code>", code)
  
  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())

  return code
  
def drop_admin_email(shiftDate, shiftStart, shiftEnd, empName, receiver_email):
  subject = "Shift Drop has been Requested by Employee"

  text = """\
	  <empName> has requested to drop their shift <shiftDate1> <shiftStart1> - <shiftEnd1>.

    Please log into the website to accept or deny this request.

    This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
    """
  html = """\
  <html>
    <body>
      <p><empName> has requested to drop their shift <shiftDate1> <shiftStart1> - <shiftEnd1>.
      <br>
      <br>
      <u><b>Please log into the website to accept or deny this request.</b></u>
      <br>
      <br>
      <br>
      <br>
      <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
      <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
      <br>
      </p>
    </body>
  </html>
  """

  text = text.replace("<empName>", empName).replace("<shiftDate1>", shiftDate).replace(
      "<shiftStart1>", shiftStart).replace("<shiftEnd1>", shiftEnd)
  html = html.replace("<empName>", empName).replace("<shiftDate1>", shiftDate).replace(
      "<shiftStart1>", shiftStart).replace("<shiftEnd1>", shiftEnd)

  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())


def vacation_admin_email(startDate, endDate, empName, receiver_email):
  subject = "Vacation has been Requested by Employee"

  text = """\
	  <empName> has requested a vacation from <startDate> to <endDate>.

    Please log into the website to accept or deny this request.

    This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.
    """
  html = """\
  <html>
    <body>
      <p><empName> has requested a vacation from <startDate> to <endDate>.
      <br>
      <br>
      <u><b>Please log into the website to accept or deny this request.</b></u>
      <br>
      <br>
      <br>
      <br>
      <p style="float:left;"><img src="https://imgur.com/o533wY4.jpg" width="85" height="44" alt="QPI Logo"></p>
      <p><b>This message is automated so please do not reply to this message. If you have any questions, please contact HR or management.</b></p>
      <br>
      </p>
    </body>
  </html>
  """

  text = text.replace("<empName>", empName).replace("<startDate>", startDate).replace(
      "<endDate>", endDate)
  html = html.replace("<empName>", empName).replace("<startDate>", startDate).replace(
      "<endDate>", endDate)

  if isinstance(receiver_email, list):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
  else:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
