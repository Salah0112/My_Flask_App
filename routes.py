from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, jsonify, session, json
from TV_Display.models import TV, User, File, tv_file_association, load_user
from TV_Display.forms import LoginForm, UploadFileForm, TVSerialForm, NewTVForm, Uni_UploadForm
from TV_Display import db, app
from flask_login import login_user, logout_user, login_required, current_user
from TV_Display.Convertpow import convert_ppt_to_images_and_videos, generate_presentation_html, generate_video_html, \
    generate_pdf_html, generate_image, adjust_image_resolution
from werkzeug.utils import secure_filename
import os
from sqlalchemy.exc import IntegrityError
import uuid
import hashlib
import shutil
from requests.exceptions import RequestException
from datetime import datetime
import pytz
import requests
import json
from flask_wtf import CSRFProtect
from datetime import timedelta
import pyautogui
import time


csrf = CSRFProtect(app)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)  # Example duration
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookie over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent client-side JS from a
# Accessing the cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Mitigate CSRF attacks


@app.route('/mock_authenticate', methods=['POST'])
@csrf.exempt
def mock_authenticate():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Mock response
    if username == "Hicham" and password == "Hichamsaidi2002":
        return jsonify({
            'authenticated': True,
            'id': 9,
            'expiredTime': '2024-12-31T23:59:59.000Z',
            'permissions': [
                {
                    'appName': 'TV display',
                    'roles': [
                        {
                            'roleId': 1,
                            'roleName': 'TdAdmin',
                            'permissions': [
                                {
                                    'id': 1,
                                    'name': 'View TV status',
                                    'model': 1,
                                    'archived': False
                                },
                                {
                                    'id': 2,
                                    'name': 'Edit TV settings',
                                    'model': 1,
                                    'archived': False
                                }
                            ]
                        },
                        {
                            'roleId': 2,
                            'roleName': 'Editor',
                            'permissions': [
                                {
                                    'id': 3,
                                    'name': 'Upload files',
                                    'model': 2,
                                    'archived': False
                                },
                                {
                                    'id': 4,
                                    'name': 'Delete files',
                                    'model': 2,
                                    'archived': False
                                }
                            ]
                        }
                    ]
                }
            ]
        }), 200
    elif username == "Asmae" and password == "AsmaeSaid2002":
        return jsonify({
            'authenticated': True,
            'id': 7,
            'expiredTime': '2024-12-31T23:59:59.000Z',
            'permissions': [
                {
                    'appName': 'TV display',
                    'roles': [
                        {
                            'roleId': 1,
                            'roleName': 'TdRegular',
                            'permissions': [
                                {
                                    'id': 1,
                                    'name': 'View TV status',
                                    'model': 1,
                                    'archived': False
                                },
                                {
                                    'id': 2,
                                    'name': 'Edit TV settings',
                                    'model': 1,
                                    'archived': False
                                }
                            ]
                        },
                        {
                            'roleId': 2,
                            'roleName': 'Editor',
                            'permissions': [
                                {
                                    'id': 3,
                                    'name': 'Upload files',
                                    'model': 2,
                                    'archived': False
                                },
                                {
                                    'id': 4,
                                    'name': 'Delete files',
                                    'model': 2,
                                    'archived': False
                                }
                            ]
                        }
                    ]
                }
            ]
        }), 200
    elif username == "Jabir" and password == "MrJabir2002":
        return jsonify({
            'authenticated': True,
            'id': 8,
            'expiredTime': '2024-12-31T23:59:59.000Z',
            'permissions': [
                {
                    'appName': 'TV display',
                    'roles': [
                        {
                            'roleId': 1,
                            'roleName': 'TdRegular',
                            'permissions': [
                                {
                                    'id': 1,
                                    'name': 'View TV status',
                                    'model': 1,
                                    'archived': False
                                },
                                {
                                    'id': 2,
                                    'name': 'Edit TV settings',
                                    'model': 1,
                                    'archived': False
                                }
                            ]
                        },
                        {
                            'roleId': 2,
                            'roleName': 'Editor',
                            'permissions': [
                                {
                                    'id': 3,
                                    'name': 'Upload files',
                                    'model': 2,
                                    'archived': False
                                },
                                {
                                    'id': 4,
                                    'name': 'Delete files',
                                    'model': 2,
                                    'archived': False
                                }
                            ]
                        }
                    ]
                }
            ]
        }), 200
    else:
        return jsonify({'authenticated': False}), 401


@app.route('/', methods=['GET'])
def home_page():

    return render_template('home.html')

@app.route('/current_tv_status', methods=['GET'])
def current_tv_status():
    TV_ON = TV.query.filter_by(Status="Active").count()
    return jsonify(tv_on=TV_ON)

@app.route('/current_number_files', methods=['GET'])
def current_files_number():
    Files_number = File.query.count()
    return jsonify(Files_Number=Files_number)

@app.route('/current_user_number', methods=['GET'])
def current_user_number():
    Users_Number= User.query.count()
    return jsonify(Users_Number=Users_Number)

@app.route('/current_tv_number', methods=['GET'])
def current_tv_number():
    TVs_Number= TV.query.count()
    return jsonify(TVs_Number=TVs_Number)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        url = "http://127.0.0.1:5000/mock_authenticate"
        data = {'username': username, 'password': password}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                user_info = response.json()
                if user_info['authenticated']:
                    user = load_user(user_info['id'])  # Assuming user_info includes 'user_id'
                    login_user(user)
                    session['expiredTime'] = datetime.strptime(user_info['expiredTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    User_permissions = user_info['permissions']
                    for permission in User_permissions:
                        if permission['appName'] == 'TV display':
                            session['permissions'] = permission['roles']
                            break
                    flash(f'Success! You are logged in as: {user.username}', category='success')
                    return redirect(url_for('home_page'))
                else:
                    flash('Authentication failed. Please check username and password.', 'danger')
            else:
                flash('Failed to connect to authentication service.', 'danger')
        except RequestException as e:
            flash('Failed to connect to authentication service.', 'danger')
    return render_template('Login.html', form=form)
    


@app.before_request
def check_token_expiration():
    if 'expiredTime' in session:
        if datetime.now(pytz.utc) >= session['expiredTime']:
            session.clear()
            flash('Your session has expired. Please log in again.', 'info')
            return redirect(url_for('logout_page'))
            
@app.route('/logout')
def logout_page():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for("home_page"))


def has_permission(required_role):
    # Fetch the permissions list from the session; default to an empty list if not found
    user_permissions = session.get('permissions', [])

    # Check if the required role is in any of the dictionaries within the list
    for permission_dict in user_permissions:
        if permission_dict.get('roleName') == required_role:
            return True
    return False


@app.context_processor
def inject_permissions():
    return dict(has_permission=has_permission)


"""

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('Login.html', form=form)
"""


app.config['UPLOAD_FOLDER'] = 'TV_Display/static/Upload/files'
app.config['CONVERTED_FILES_FOLDER'] = 'TV_Display/static/Upload/converted_files'


@app.route('/TVs_manage', methods=['GET', 'POST'])
@login_required
def TVs_manage_page():
    all_tvs = TV.query.filter_by(
        user_id=current_user.id).all() if not has_permission('TdAdmin') else TV.query.all()
    permission = current_user.Permission

    return render_template("manage.html", all_tvs=all_tvs, permission=permission)


@app.route('/TV_Display', methods=['GET', 'POST'])
def TV_display_page():
    form = TVSerialForm()
    if form.validate_on_submit():
        serial_number = form.serial_number.data
        tv = TV.query.filter_by(Serial_Number=serial_number).first()
        if not tv:
            flash('TV with the specified Serial Number not found or not accessible.', 'danger')
            return redirect(url_for('TV_display_page'))

        if not tv.assigned_file:
            flash('No presentation assigned to this TV.', 'info')
            return redirect(url_for('default_show', tv_id=tv.id))

        presentation_content = tv.assigned_file.Presentation_Content if tv.assigned_file else None
        current_content_hash = hashlib.md5(presentation_content.encode()).hexdigest() if presentation_content else None

        if presentation_content:
            time.sleep(5)
            pyautogui.press('space')

            return render_template("Presentation.html", presentation_content=presentation_content, tv_id=tv.id,
                                   current_content_hash=current_content_hash)
        else:
            flash('Presentation content is missing.', 'danger')
            return redirect(url_for('TV_display_page'))

    return render_template('TV_Display.html', form=form)






@app.route('/check_update/<int:tv_id>')
def check_update(tv_id):
    tv = TV.query.get(tv_id)

    if tv and tv.assigned_file:
        db.session.commit()
        current_content_hash = hashlib.md5(tv.assigned_file.Presentation_Content.encode()).hexdigest()
        tv.Status = "Active"
        db.session.commit()
        return jsonify({
            'updated': True,
            'content_hash': current_content_hash
        })
    return jsonify({'updated': False})

import logging

logging.basicConfig(level=logging.DEBUG)

@app.route('/stop_presentation', methods=['POST'])
@csrf.exempt
def update_status():
    # Log the received data for debugging
    data = request.get_data(as_text=True)
    app.logger.debug(f"Received data: {data}")

    if data:
        try:
            parsed_data = json.loads(data)
            tv_id = parsed_data.get('status')
            app.logger.debug(f"Parsed data: {parsed_data}")

            # Assuming TV is a SQLAlchemy model
            tv = TV.query.get_or_404(tv_id)
            if tv:
                tv.Status = "Inactive"
                db.session.commit()
                return jsonify({'message': 'Status updated successfully'})
        except json.JSONDecodeError as e:
            app.logger.error(f"JSON decode error: {e}")
            return jsonify({'message': 'Invalid JSON received'}), 400
        except Exception as e:
            app.logger.error(f"Error processing request: {e}")
            return jsonify({'message': f'Error processing request: {e}'}), 500

    return jsonify({'message': 'No data received'}), 400


@app.route('/get_slideduration/<int:tv_id>')
def get_slideduration(tv_id):
    tv = TV.query.get_or_404(tv_id)
    if not tv.assigned_file:
        return jsonify({"error": "No presentation assigned to this TV"}), 404

    # Retrieve slide duration from the assigned file, or use a default value if not set
    slideduration = tv.assigned_file.slide_duration*1000 if tv.assigned_file.slide_duration else 3000

    return jsonify({"slideduration": slideduration})
@app.route('/remove_file/<int:file_id>', methods=['POST'])
@login_required
def remove_file(file_id):
    file_to_remove = File.query.get_or_404(file_id)

    # Remove file references in many-to-many relationships
    tvs = TV.query.filter(TV.files.any(id=file_id)).all()
    for tv in tvs:
        tv.files.remove(file_to_remove)

    # Clear the assigned file if this file is currently assigned
    tvs_with_assigned_file = TV.query.filter_by(assigned_file_id=file_id).all()
    for tv in tvs_with_assigned_file:
        tv.assigned_file_id = None

    # Commit the session to ensure all references are cleared
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while updating TV references: {str(e)}", category='danger')
        return redirect(url_for('File_page'))

    # Attempt to delete the files from the filesystem
    try:
        # Delete individual files
        if file_to_remove.File_path:
            file_paths = file_to_remove.File_path.split('; ')
            for path in file_paths:
                if os.path.exists(path):
                    os.remove(path)

        # Delete the directory if it exists
        if file_to_remove.Content_path and os.path.isdir(file_to_remove.Content_path):
            shutil.rmtree(file_to_remove.Content_path)

    except Exception as e:
        flash(f"An error occurred while deleting the files: {str(e)}", category='danger')

    # Attempt to delete the database record
    try:
        db.session.delete(file_to_remove)
        db.session.commit()
        flash("File deleted successfully.", category='success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while removing the database entry: {str(e)}", category='danger')

    return redirect(url_for('File_page'))

from datetime import datetime


@app.route('/Files', methods=['GET', 'POST'])
@login_required
def File_page():
    form = UploadFileForm()
    all_files = File.query.filter_by(user_id=current_user.id).all() if not has_permission(
        'TdAdmin') else File.query.all()

    if form.validate_on_submit():
        files = form.file.data  # This now contains a list of files
        test_list = []
        presentation_content = ""
        file_paths = []  # List to store individual file paths for database record
        file_names = []  # List to collect valid filenames for creating a combined name

        if not files:
            flash("No files uploaded.")
            return redirect(url_for("File_page"))

        try:
            for file in files:  # Iterate over each file
                individual_filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], individual_filename)
                print(f"Processing file: {individual_filename}")

                # Check file type and process accordingly
                if individual_filename.endswith('.pptx'):
                    file.save(file_path)
                    file_paths.append(file_path)
                    file_names.append(individual_filename)
                    # Convert and handle PPTX files
                    output_dir = os.path.join(app.config['CONVERTED_FILES_FOLDER'], str(uuid.uuid4()))
                    os.makedirs(output_dir, exist_ok=True)
                    test_list += convert_ppt_to_images_and_videos(file_path, output_dir)
                    presentation_content += generate_presentation_html(test_list)
                    file_type = 'pptx'
                    content_path = output_dir

                elif individual_filename.lower().endswith(
                        ('.mp4', '.mov', '.avi', '.wmv', '.pdf', '.jpg', '.png', '.jpeg')):
                    file.save(file_path)
                    file_paths.append(file_path)
                    file_names.append(individual_filename)
                    # Handle various file types
                    if individual_filename.lower().endswith(('.mp4', '.mov', '.avi', '.wmv')):
                        presentation_content += generate_video_html(
                            url_for('static', filename=f'Upload/files/{individual_filename}'))
                        file_type = 'video'
                    elif individual_filename.lower().endswith('.pdf'):
                        presentation_content += generate_pdf_html(
                            url_for('static', filename=f'Upload/files/{individual_filename}'))
                        file_type = 'pdf'
                    elif individual_filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                        adjust_image_resolution(file_path)
                        presentation_content += generate_image(
                            url_for('static', filename=f'Upload/files/{individual_filename}'))
                        file_type = 'Image'
                    content_path = 'None'

                else:
                    flash(f"Unsupported file type for {individual_filename}.")
                    continue

            if not file_names:
                flash("No supported files were uploaded.")
                return redirect(url_for("File_page"))

            # Determine the filename based on the number of valid files uploaded
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if len(file_names) == 1:
                filename = file_names[0]  # Single file, use original name
            else:
                # Truncate individual file names to avoid overly long combined name
                truncated_names = [name.split('.')[0][:4] for name in file_names[:3]]  # Truncate to 10 chars
                filename = f"Combined_{'_'.join(truncated_names)}_and_{len(file_names)}Files_{timestamp}"  # Combining names

            # Create and add the new file to the database
            file_path_to_save = "; ".join(file_paths)
            new_file = File(File_Name=filename, File_Type=file_type, File_path=file_path_to_save,
                            Presentation_Content=presentation_content, Content_path=content_path,
                            user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            flash(f"{filename} has been uploaded and processed successfully.")

            return redirect(url_for("File_page"))

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            flash(f"An error occurred while processing files: {str(e)}")
            return redirect(url_for("File_page"))

    return render_template("Files.html", all_files=all_files, form=form)


@app.route('/add_new_tv', methods=['GET', 'POST'])
@login_required
def add_new_tv():
    if not has_permission('TdAdmin'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('TVs_manage_page'))

    form = NewTVForm()
    if form.validate_on_submit():
        try:
            new_tv = TV(
                Serial_Number=form.Serial_Number.data,
                Location=form.Location.data,
                user_id=form.User_id.data  # Assign the selected user ID
            )
            db.session.add(new_tv)
            db.session.commit()
            flash("New TV added successfully!", "success")
        except IntegrityError as e:
            db.session.rollback()  # Roll back the transaction on error
            if 'duplicate key' in str(e.orig).lower():  # Check if the error is due to a duplicate key
                flash("This Serial Number already exists. Please use a unique serial number.", "error")
            else:
                flash("An error occurred while adding the TV. Please try again.", "error")
        except Exception as e:
            db.session.rollback()  # Roll back the transaction on any other error
            flash("An unexpected error occurred. Please try again.", "error")
        return redirect(url_for('add_new_tv'))
    return render_template('Add_TV.html', form=form)



@app.route('/assign_file_to_tv', methods=['POST'])
@login_required
def assign_file_to_tv():
    file_id = request.form.get('file_id')
    tv_serial_number = request.form.get('tv_serial_number')

    file = File.query.get(file_id)
    if not file:
        flash('File not found.', 'danger')
        return redirect(url_for('File_page'))

    tv = TV.query.filter_by(Serial_Number=tv_serial_number).first()
    if not tv:
        flash('TV not found.', 'danger')
        return redirect(url_for('File_page'))

    # Assign the file to the TV as the primary assigned file
    tv.assigned_file_id = file_id
    tv.assigned_file = file

    # Add the file to the many-to-many relationship if it's not already there
    if file not in tv.files:
        tv.files.append(file)

    db.session.commit()  # Save changes to the database
    flash(f'File has been assigned successfully to the TV with serial number: {tv_serial_number}', 'success')
    return redirect(url_for('File_page'))  # Redirect to avoid double posting




@app.route('/update_duration', methods=['POST'])
@login_required
def update_duration():
    data = request.get_json()
    file_id = data.get('fileId')
    new_duration = data.get('newDuration')

    if not file_id or not new_duration:
        return jsonify({'error': 'Invalid data provided'}), 400

    try:
        new_duration = int(new_duration)
    except ValueError:
        return jsonify({'error': 'Duration must be a number'}), 400

    if not 2 <= new_duration:
        return jsonify({'error': 'Min Duration: 2s'}), 400

    file_to_update = File.query.get(file_id)
    if not file_to_update:
        return jsonify({'error': 'File not found'}), 404

    try:
        file_to_update.slide_duration = new_duration
        db.session.commit()
        return jsonify({'message': 'Duration updated successfully!', 'status': 'success'}), 200
    except Exception as e:
        db.session.rollback()


@app.route('/remove_tv/<int:tv_id>', methods=['POST'])
@login_required
def remove_tv(tv_id):
    tv_to_remove = TV.query.get_or_404(tv_id)

    try:
        db.session.delete(tv_to_remove)
        db.session.commit()
        flash("TV got removed successfully.", category='success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while removing the TV: {str(e)}", category='danger')

    return redirect(url_for('TVs_manage_page'))



ALLOWED_EXTENSIONS = {'pdf', 'pptx', 'jpg', 'jpeg', 'png', 'mp4'}




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/default_upload', methods=['GET', 'POST'])
def default_upload():
    form = Uni_UploadForm()
    if form.validate_on_submit():
        # Define the path for the default presentation
        default_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'default')

        # Clear the default folder
        if os.path.exists(default_folder):
            shutil.rmtree(default_folder)
        os.makedirs(default_folder)

        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Save the file in the new 'default' directory
            file_path = os.path.join(default_folder, filename)
            file.save(file_path)
            flash('Default presentation uploaded successfully!', 'success')
        else:
            flash('Invalid file type. Allowed types are pdf, pptx, jpg, jpeg, png, mp4.', 'danger')

    return redirect(url_for('File_page'))
from werkzeug.utils import secure_filename
import os

@app.route('/default_presentation', methods=['GET'])
def default_show():
    tv_id = request.args.get('tv_id')
    if not tv_id:
        flash("TV ID not provided", 'danger')
        return redirect(url_for('TV_display_page'))

    tv = TV.query.get_or_404(tv_id)
    try:
        default_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'default')
        default_files = os.listdir(default_folder)
        if not default_files:
            flash("No default file available.", 'danger')
            return redirect(url_for('TV_display_page'))

        default_file_name = default_files[0]  # Assuming there is only one default file
        file_path = os.path.join(default_folder, default_file_name)
        file_type = default_file_name.split('.')[-1].lower()

        presentation_content = ""
        if file_type == 'pptx':
            output_dir = os.path.join(app.config['CONVERTED_FILES_FOLDER'], str(uuid.uuid4()))
            os.makedirs(output_dir, exist_ok=True)
            # Assuming convert_ppt_to_images_and_videos is a defined function
            test_list = convert_ppt_to_images_and_videos(file_path, output_dir)
            # Assuming generate_presentation_html is a defined function that generates HTML content
            presentation_content = generate_presentation_html(test_list)

        elif file_type in ['mp4', 'mov', 'avi', 'wmv']:
            # Generate HTML content for video files
            presentation_content = generate_video_html(url_for('static', filename=f'Upload/files/default/{secure_filename(default_file_name)}'))

        elif file_type == 'pdf':
            # Generate HTML content for PDF files
            presentation_content = generate_pdf_html(url_for('static', filename=f'Upload/files/default/{secure_filename(default_file_name)}'))

        elif file_type in ['jpg', 'jpeg', 'png']:
            # Assuming adjust_image_resolution is a defined function
            adjust_image_resolution(file_path)
            presentation_content = generate_image(url_for('static', filename=f'Upload/files/default/{secure_filename(default_file_name)}'))

        else:
            flash("Unsupported file type.", 'danger')
            return redirect(url_for('TV_display_page'))

        current_content_hash = hashlib.md5(presentation_content.encode()).hexdigest()
        return render_template("Presentation.html", presentation_content=presentation_content,
                               current_content_hash=current_content_hash, tv_id=tv_id)

    except Exception as e:
        flash(f"Error displaying default content: {str(e)}", 'danger')
        return redirect(url_for('TV_display_page'))
