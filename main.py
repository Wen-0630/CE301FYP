from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')  # Assuming your HTML file is named 'login.html' and located in the 'templates' directory

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Here you should implement your validation logic and check against your user database
        if email == "example@example.com" and password == "securepassword123":
            return "Login successful!"
        else:
            return "Invalid email or password!"

if __name__ == '__main__':
    app.run(debug=True)
