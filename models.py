from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # Default role is 'user'

    def __repr__(self):
        return f'<User :{self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    quotes = db.relationship('Quote', backref='author', lazy=True)

    def __repr__(self):
        return f'<Author :{self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'quotes': [quote.to_dict() for quote in self.quotes]
        }
    
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __repr__(self):
        return f'<Quote :{self.text[:10]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'author': self.author.to_dict() if self.author else None
        }
