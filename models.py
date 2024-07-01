from TV_Display import db, bcrypt
from TV_Display import login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Secondary table for the many-to-many relationship
tv_file_association = db.Table('tv_file_association',
    db.Column('tv_id', db.Integer, db.ForeignKey('TVs.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('Files.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    Email = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    Permission = db.Column(db.String(length=8), default='Manager')
    First_name = db.Column(db.String(length=30), nullable=False)
    Last_name = db.Column(db.String(length=30), nullable=False)
    TVs = db.relationship('TV', backref='user', lazy=True)
    Files = db.relationship('File', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class TV(db.Model):
    __tablename__ = 'TVs'
    id = db.Column(db.Integer(), primary_key=True)
    Serial_Number = db.Column(db.Integer(), nullable=False, unique=True)
    Location = db.Column(db.String(length=35), nullable=False)
    Status = db.Column(db.String(15), default="Inactive")
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    assigned_file_id = db.Column(db.Integer, db.ForeignKey('Files.id'), nullable=True)
    assigned_file = db.relationship('File', foreign_keys=[assigned_file_id], uselist=False)
    files = db.relationship('File', secondary=tv_file_association, backref=db.backref('tvs', lazy='dynamic'))

    def __repr__(self):
        return f"Serial_Number: {self.Serial_Number}, Location: {self.Location}, Status: {self.Status}"

class File(db.Model):
    __tablename__ = 'Files'
    id = db.Column(db.Integer(), primary_key=True)
    File_Name = db.Column(db.String(length=255), nullable=False)
    File_Type = db.Column(db.String(length=5), nullable=False)
    File_path = db.Column(db.String(length=512), nullable=False)
    Content_path = db.Column(db.String(length=255), nullable=True)
    Presentation_Content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    slide_duration = db.Column(db.Integer(), nullable=True)
    def __repr__(self):
        return f"File Name: {self.File_Name}, File Type: {self.File_Type}, Status: {self.Status}"
