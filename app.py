from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, session
from models import db, User, Author, Quote

app = Flask(__name__)

app.secret_key = 'secret_key'  # Set a secret key for session management

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications

# Initialize the database with the Flask app

db.init_app(app) 

with app.app_context():
    db.create_all()  # Create database tables
    admin = User.query.filter_by(email='admin@gmail.com').first()
    if not admin:  # check if admin else create
        admin = User(
            name='Admin',
            email='admin@gmail.com',
            password='admin',
            role='admin'  # Set role to 'admin' to override default i.e 'user'
        )
        db.session.add(admin)
        db.session.commit()  # Commit the changes to the database
        print('Admin user created!\nWith email: admin@gmail.com and password: admin')


#### Decorators #####
def login_required(only_admin=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not session.get('user_id'):
                return redirect(url_for('login', message='You need to log in first!'))
            if only_admin:
                user = User.query.filter_by(email=session['user_id']).first()
                if not user or user.role != 'admin':
                    return redirect(url_for('user_dashboard', message='You do not have permission to access this page!'))
            return f(*args, **kwargs)
        return wrapper
    return decorator


#### Authentication routes #####

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        user_exists = User.query.filter_by(email=email).first()  # Check if email is already registered
        if user_exists: # Check if email is already registered
            return redirect(url_for('login', message='Email already registered!'))
        # Store user in the database
        user = User(
            name=name,
            email=email,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login', message='Registration successful! Please log in.'))
    message = request.args.get('message')
    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        user_exists = User.query.filter_by(email=email).first()  # Check if email is registered
        if not user_exists: # Check if email is not registered
            return redirect(url_for('register', message='You need to register first!'))
        password = request.form.get('password')
        if user_exists.password != password: # Check if password is incorrect
            return redirect(url_for('login', message='Incorrect password!'))
        # Since login is successful, store user ID in session
        session['user_id'] = email # Store user ID in session
        if user_exists.role == 'admin':
            return redirect(url_for('admin_dashboard', message='Login successful!'))
        return redirect(url_for('user_dashboard', message='Login successful!'))
    message = request.args.get('message')
    return render_template('login.html', message=message)

@app.route('/logout')
@login_required()
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login', message='You have been logged out!'))

####### Admin routes #######

@app.route('/admin')
@login_required(only_admin=True)
def admin_dashboard():
    message = request.args.get('message')
    return render_template('admin/dashboard.html', message=message)

@app.route('/admin/users')
@login_required(only_admin=True)
def admin_users():
    message = request.args.get('message')

    users = User.query.all()  # Fetch all users from the database
    users = [user.to_dict() for user in users]
    return render_template('admin/users.html', users=users, message=message)

@app.route('/admin/summary')
@login_required(only_admin=True)
def admin_summary():
    message = request.args.get('message')
    return render_template('admin/summary.html', message=message)

### Admin authors routes ###

@app.route('/admin/authors', methods=['GET', 'POST'])
@login_required(only_admin=True)
def admin_authors():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        image_url = request.form.get('image')
        author = Author(
            name=name,
            description=description,
            image_url=image_url
        )
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('admin_authors', message='Author added successfully!'))
    message = request.args.get('message')
    authors = Author.query.all()
    authors = [author.to_dict() for author in authors]
    return render_template('admin/authors.html', message=message, authors=authors)

@app.route('/admin/authors/<int:author_id>', methods=['GET', 'POST'])
@login_required(only_admin=True)
def admin_author(author_id):
    if request.method == 'POST':
        author = Author.query.get(author_id)
        if not author:
            return redirect(url_for('admin_authors', message='Author not found!'))
        delete = request.form.get('delete')
        if delete:
            db.session.delete(author)
            db.session.commit()
            return redirect(url_for('admin_authors', message='Author deleted successfully!'))
        name = request.form.get('name')
        description = request.form.get('description')
        image_url = request.form.get('image')
        author.name = name
        author.description = description
        author.image_url = image_url
        db.session.commit()
        return redirect(url_for('admin_author', author_id=author.id, message='Author updated successfully!'))
    message = request.args.get('message')
    author = Author.query.get(author_id)
    if not author:
        return redirect(url_for('admin_authors', message='Author not found!'))
    author = author.to_dict()
    return render_template('admin/author.html', message=message, author=author)

####### Admin quotes routes ###

@app.route('/admin/quotes', methods=['GET', 'POST'])
@login_required(only_admin=True)
def admin_quotes():
    if request.method == 'POST':
        text = request.form.get('text')
        author_id = request.form.get('author_id')
        print(request.form)
        quote = Quote(
            text=text,
            author_id=author_id
        )
        db.session.add(quote)
        db.session.commit()
        return redirect(url_for('admin_quotes', message='Quote added successfully!'))
    message = request.args.get('message')
    quotes = Quote.query.all()
    quotes = [quote.to_dict() for quote in quotes]
    authors = Author.query.all()
    authors = [author.to_dict() for author in authors]
    return render_template('admin/quotes.html', message=message, quotes=quotes, authors=authors)


@app.route('/admin/quotes/<int:quote_id>', methods=['GET', 'POST'])
@login_required(only_admin=True)
def admin_quote(quote_id):
    if request.method == 'POST':
        quote = Quote.query.get(quote_id)
        if not quote:
            return redirect(url_for('admin_quotes', message='Quote not found!'))
        delete = request.form.get('delete')
        if delete:
            db.session.delete(quote)
            db.session.commit()
            return redirect(url_for('admin_quotes', message='Quote deleted successfully!'))
        text = request.form.get('text')
        author_id = request.form.get('author_id')
        quote.text = text
        quote.author_id = author_id
        db.session.commit()
        return redirect(url_for('admin_quote', quote_id=quote.id, message='Quote updated successfully!'))
    message = request.args.get('message')
    quote = Quote.query.get(quote_id)
    if not quote:
        return redirect(url_for('admin_quotes', message='Quote not found!'))
    author = quote.author; author = author.to_dict()
    quote = quote.to_dict()
    authors = Author.query.all()
    authors = [author.to_dict() for author in authors]
    return render_template('admin/quote.html', message=message, quote=quote, author=author, authors=authors)


####### User routes #######

@app.route('/')
@login_required()
def user_dashboard():
    message = request.args.get('message')
    quotes = Quote.query.all()
    quotes = [quote.to_dict() for quote in quotes]
    return render_template('user/dashboard.html', user=session, message=message, quotes=quotes)


#### Running the app #####

if __name__ == '__main__':
    app.run(debug=True)