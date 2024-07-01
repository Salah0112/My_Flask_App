from TV_Display import app, db
from TV_Display.models import User, TV

def add_user(username, email, password_hash, permission='', first_name='', last_name=''):
    with app.app_context():
        # Create a new User instance
        new_user = User(
            username=username,
            Email=email,
            password=password_hash,
            Permission=permission,
            First_name=first_name,
            Last_name=last_name
        )

        # Add the new user to the database
        db.session.add(new_user)

        # Commit the changes to the database
        db.session.commit()
def add_tv(serial_number, location, status, user_id):
    with app.app_context():
        new_tv = TV(
            Serial_Number=serial_number,
            Location=location,
            Status=status,
            user_id=user_id
        )

        db.session.add(new_tv)
        db.session.commit()

def assign_tv_to_user(tv_id, user_id):
    with app.app_context():
        tv = TV.query.get(tv_id)
        if tv:
            tv.user_id = user_id
            db.session.commit()
            return True
        else:
            return False

def give_permission_to_user(user_id, permission):
    with app.app_context():
        user = User.query.get(user_id)
        if user:
            user.Permission = permission
            db.session.commit()
            return True
        else:
            return False
