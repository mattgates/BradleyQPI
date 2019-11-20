from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/schedule')
def schedule():
	return render_template('schedule.html')

@app.route('/swap')
def swap():
	return render_template('swap.html')

@app.route('/drop')
def drop():
	return render_template('drop.html')

@app.route('/vacation')
def vacation():
	return render_template('vacation.html')

@app.route('/notifications')
def notifications():
	return render_template('notifications.html')

@app.route('/settings')
def settings():
	return render_template('settings.html')

@app.route('/login')
def login():
	return render_template('login.html')
	
@app.route('/register')
def register():
	return render_template('register.html')
	
if __name__ == '__main__':
	app.run(debug=True)#