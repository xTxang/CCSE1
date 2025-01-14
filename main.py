from flask import Flask, request, render_template, redirect, url_for
import flask
from database import Database #Imports session and products from database.py to populate the e-commerce
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy 

db = Database()# intialises the database object

def numberCheck(word):
    return any(i.isdigit() for i in word)

app = Flask(__name__)



@app.route('/')
# @app.route('/index')
# def index():
#     return render_template('dashboad.html')

def home():
    return render_template('dashboad.html')

from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    
    # session = initDb
    # print(session)
    # print(products)


    # products = session.query(products).all()

    # Render the 'index.html' template, passing the products data

    product_list = db.returnProducts()
    return render_template('shop.html', products=product_list)
   # return render_template('shop.html')  # Fixed "dashboad" typo

@app.route('/basket')
def basket():
    return render_template('basket.html')  # Render the basket template when this route is accessed

# @app.route('/login', methods=['POST'])
# def login():
#     return render_template('login.html')

#     if requrestm


# # @app.route('/login', methods=['POST'])
# # # Function to check entered credentials and provide correct response
# # def login():
# #     # Get entered credentials
# #     action = request.form.get('action')  # Retrieve the value of the clicked button
# #     email = request.form.get('email')
# #     password = request.form.get('password')

# #     if action == 'login':
# #         # Logic for login button
# #         return "You clicked Sign In!"
# #     elif action == 'signup':
# #         # Logic for signup button
# #         return "You clicked Sign Up!"

# #     if 1 == 2:
# #         return render_template('shop.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Render the login form when accessed via GET
        # Handle form submission when accessed via POST
        action = request.form.get('action')  # Retrieve the value of the clicked button
        new_username = request.form.get('username')
        new_password = request.form.get('password')

        if action == 'login':  
            returnedUser = db.search_user(new_username,new_password)
            if returnedUser == None:
                return render_template('login.html', failed_login=True)
            else:
                print('worked')
                userId = returnedUser.userID
                print(userId)
                return redirect(f'/shop/{userId}')

            
            

            #TODO Check if login is in database, then if good, send back to shop page
            return render_template('shop.html')
        elif action == 'signup':

            if len(new_password) < 8 or len(new_username) < 8 or numberCheck(new_password) == False:
                return render_template("login.html", failed_signup=True)
            else:
                db.store_username(new_username, new_password)
                return redirect('/signup')
    return render_template('login.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    action = request.form.get('action')  # Get the value of the button
    if action == 'submit':
        print('hello')
        name = request.form.get('name')
        houseNum = request.form.get('house')
        street = request.form.get('street')
        city = request.form.get('city')
        postcode = request.form.get('postcode')
        print(name)
        print(houseNum)
        print(street)
        print(city)
        print(postcode)

        db.createUser(name, houseNum, street, city, postcode)
    return render_template("shop.html")


# @app.route('/shop')
# def shop():
#     #TODO how do i do auth i cant do it

#     return render_template('shop.html')



@app.route('/shop/<userId>')
def userShop(userId):
    print(userId)
    product_list = db.returnProducts()
    return render_template('userShop.html', products=product_list)


@app.route('/logout')
def logout():
    print('hello')
    return redirect('/index')

@app.route('/basket/<userId>')

def basket(userId):
    """Redirects to the basket of a specific user when the button is pressed on their webpage"""
    print(f'User ID: {userId}')

if __name__ == '__main__':
    app.run(debug=True)

