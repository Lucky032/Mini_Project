from flask import Flask, render_template, redirect, url_for, flash,abort, request, session
from db_connection import get_db_connection  # Ensure this is set up correctly to connect to MSSQL
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory

app = Flask(__name__, template_folder='../frontend/template', static_folder='../frontend/static')
app.secret_key = 'your_secret_key'  # Update with your own secret key

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # 'coach' or 'player'

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if role == 'coach':
                cursor.execute(
                    'INSERT INTO Coach (Username, Email, Password) VALUES (?, ?, ?)',
                    (username, email, password)
                )
            elif role == 'player':
                cursor.execute(
                    'INSERT INTO Player (Username, Email, Password) VALUES (?, ?, ?)',
                    (username, email, password)
                )
            conn.commit()
            flash(f'{role.capitalize()} registered successfully!', 'success')
            return redirect(url_for('login', role==role))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    role = request.args.get('role', 'login')  # Default to 'login' if no role is provided
    return render_template('index.html', role=role)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check login credentials for Coach
            cursor.execute('SELECT * FROM Coach WHERE Username = ? AND Password = ?', (username, password))
            coach = cursor.fetchone()

            if coach:
                session['user'] = {'username': username, 'role': 'coach'}
                return redirect(url_for('base'))

            # Check login credentials for Player
            cursor.execute('SELECT * FROM Player WHERE Username = ? AND Password = ?', (username, password))
            player = cursor.fetchone()

            if player:
                session['user'] = {'username': username, 'role': 'player'}
                return redirect(url_for('base'))

            flash('Invalid username or password.', 'danger')

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')

        finally:
            cursor.close()
            conn.close()

    return render_template('base.html', role='login')

# Base route (for logged-in users)
@app.route('/base', methods=['GET', 'POST'])
def base():
    if 'user' in session:
        username = session['user']['username']
        role = session['user']['role']
        player_profiles = []  # Initialize an empty list for player profiles

        if role == 'coach' and request.method == 'POST':
            conn = None
            cursor = None
            try:
                conn = get_db_connection()  # Establish the database connection
                cursor = conn.cursor()

                # Execute the query to fetch all player profiles
                cursor.execute('SELECT * FROM PlayerProfile')
                player_profiles = cursor.fetchall()  # Fetch all results

                # Debugging: print fetched player profiles
                print("Fetched Player Profiles:", player_profiles)

            except Exception as e:
                # Log the error and provide feedback
                print(f"An error occurred while fetching player profiles: {e}")
                abort(500, description="Error fetching player profiles: " + str(e))

            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        return render_template('base.html', username=username, role=role, player_profiles=player_profiles)
    else:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))  # Redirect to login if not logged in
 # Redirect to login if not logged in


@app.route('/coach_dashboard')
def coach_dashboard():
    if 'user' not in session or session['user']['role'] != 'coach':
        return redirect(url_for('home'))
    return render_template('coach_dashboard.html')

# Player dashboard
@app.route('/player_dashboard')
def player_dashboard():
    if 'user' not in session or session['user']['role'] != 'player':
        return redirect(url_for('home'))
    return render_template('player_dashboard.html')



# View coach profile route
@app.route('/view_coach_profile', methods=['GET'])
def view_coach_profile():
    conn = None
    cursor = None
    coach_profiles = []
    current_profile = None
    profile_index = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM CoachProfile')
        coach_profiles = cursor.fetchall()

        # Validate profile index
        profile_index = int(request.args.get('index', 0))
        if profile_index < 0 or profile_index >= len(coach_profiles):
            abort(404, description="Profile not found")

        current_profile = coach_profiles[profile_index]
        # Convert pyodbc.Row object to dictionary
        current_profile = {
            'first_name': current_profile[1],
            'last_name': current_profile[2],
            'date_of_birth': current_profile[3],
            'gender': current_profile[4],
            'home_address': current_profile[5],
            'city': current_profile[6],  # Removed 'street_address'
            'state': current_profile[7],
            'pincode': current_profile[8],
            'playing_experience': current_profile[9],
            'coaching_experience': current_profile[10],
            'teams_played': current_profile[11],
            'game': current_profile[12],
            'height': current_profile[13],
            'weight': current_profile[14],
            'resume': current_profile[15],
            'profile_photo': current_profile[16],
            'certificates': current_profile[17],
            'comments': current_profile[18]
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        abort(500, description="Error fetching coach profiles")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('view_coach_profile.html', 
                           coach_profile=current_profile, 
                           profile_index=profile_index, 
                           total_profiles=len(coach_profiles))



@app.route('/uploads1/<filename>')
def uploads1(filename):
    file_path = os.path.join('uploads1', filename)
    if not os.path.isfile(file_path):
        return f"File not found: {filename}"
    return send_from_directory('uploads1', filename)




@app.route('/view_player_profile', methods=['GET', 'POST'])
def view_player_profile():
    conn = None
    cursor = None
    player_profiles = []
    current_profile = None
    profile_index = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all player profiles
        cursor.execute('SELECT * FROM PlayerProfile')
        player_profiles = cursor.fetchall()

        # Get the current profile index from the request args
        profile_index = int(request.args.get('index', 0))

        # Check if the index is within bounds
        if profile_index < 0 or profile_index >= len(player_profiles):
            abort(404, description="Profile not found")

        # Get the current player profile
        current_profile = player_profiles[profile_index]

        # Convert pyodbc.Row object to dictionary
        current_profile = {
            'first_name': current_profile[1],
            'last_name': current_profile[2],
            'date_of_birth': current_profile[3],
            'gender': current_profile[4],
            'home_address': current_profile[5],
            'street_address': current_profile[6],
            'city': current_profile[7],
            'state': current_profile[8],
            'pincode': current_profile[9],
            'playing_experience': current_profile[10],
            'teams_played': current_profile[11],
            'game': current_profile[12],
            'height': current_profile[13],
            'weight': current_profile[14],
            'resume': current_profile[15],
            'profile_photo': current_profile[16],
            'player_video': current_profile[17],
            'certificates': current_profile[18],
            'comments': current_profile[19]
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        abort(500, description="Error fetching player profiles")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('view_player_profile.html', 
                           player_profile=current_profile, 
                           profile_index=profile_index, 
                           total_profiles=len(player_profiles))



@app.route('/<path:filename>/')
def uploads(filename):
    print(f"Requested filename: {filename}")
    file_path = filename.split('/')[-1]  # Remove uploads/ prefix
    print(f"File path: {file_path}")
    
    if not os.path.isfile(os.path.join('uploads', file_path)):
        return f"File not found: {file_path}"
    
    return send_from_directory('uploads', file_path)









        
# Submit coach profile route
@app.route('/submit_coach_profile', methods=['POST'])
def submit_coach_profile():
    if 'user' not in session or session['user']['role'] != 'coach':
        return redirect(url_for('home'))

    # Extract data from form
    first_name = request.form.get('first_name', '')
    last_name = request.form.get('last_name', '')
    dob = request.form.get('dob', '')
    gender = request.form.get('gender', '')
    home_address = request.form.get('home_address', '')
    city = request.form.get('city','')
    state = request.form.get('state', '')
    pincode = request.form.get('pincode', '')
    playing_experience = request.form.get('playing_experience', '')
    coaching_experience = request.form.get('coaching_experience', '')
    teams_played = request.form.get('teams_played', '')
    game = request.form.get('game', '')
    height = request.form.get('height', '')
    weight = request.form.get('weight', '')
    resume = request.files.get('resume')
    profile_photo = request.files.get('profile_photo')
    sports_certificates = request.files.getlist('sports_certificates')
    health_certificates = request.files.getlist('health_certificates')
    comments = request.form.get('comments', '')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Define the upload folder and ensure it exists
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)

        # Save the resume, profile photo, and certificates
        resume_filename = secure_filename(resume.filename) if resume else ''
        profile_photo_filename = secure_filename(profile_photo.filename) if profile_photo else ''
        sports_certificates_filenames = [secure_filename(certificate.filename) for certificate in sports_certificates]
        health_certificates_filenames = [secure_filename(certificate.filename) for certificate in health_certificates]

        resume_path = os.path.join(upload_folder, resume_filename) if resume else ''
        profile_photo_path = os.path.join(upload_folder, profile_photo_filename) if profile_photo else ''
        sports_certificates_paths = [os.path.join(upload_folder, filename) for filename in sports_certificates_filenames]
        health_certificates_paths = [os.path.join(upload_folder, filename) for filename in health_certificates_filenames]

        if resume:
            resume.save(resume_path)
        if profile_photo:
            profile_photo.save(profile_photo_path)
        for certificate, path in zip(sports_certificates, sports_certificates_paths):
            certificate.save(path)
        for certificate, path in zip(health_certificates, health_certificates_paths):
            certificate.save(path)

        certificates_paths = ','.join(sports_certificates_paths + health_certificates_paths)

        # Insert the form data into the CoachProfile table
        cursor.execute(''' 
            INSERT INTO CoachProfile 
            (FirstName, LastName, DOB, Gender, HomeAddress, City, State, Pincode, PlayingExperience, CoachingExperience, TeamsPlayed, Game, Height, Weight, Resume, ProfilePhoto, Certificates, Comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        ''', (first_name, last_name, dob, gender, home_address, city, state, pincode, playing_experience, coaching_experience, teams_played, game, height, weight, resume_path, profile_photo_path, certificates_paths, comments))

        conn.commit()
        flash('Profile submitted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('base'))

# Submit player profile route
@app.route('/submit_player_profile', methods=['POST'])
def submit_player_profile():
    if 'user' not in session or session['user']['role'] != 'player':
        return redirect(url_for('home'))

    # Extract data from form
    first_name = request.form.get('first_name', '')
    last_name = request.form.get('last_name', '')
    dob = request.form.get('dob', '')
    gender = request.form.get('gender', '')
    home_address = request.form.get('home_address', '')
    street_address = request.form.get('street_address', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    pincode = request.form.get('pincode', '')
    playing_experience = request.form.get('playing_experience', '')
    teams_played = request.form.get('teams_played', '')
    game = request.form.get('game', '')
    height = request.form.get('height', '')
    weight = request.form.get('weight', '')
    resume = request.files.get('resume')
    profile_photo = request.files.get('profile_photo')
    sports_certificates = request.files.getlist('sports_certificates')
    health_certificates = request.files.getlist('health_certificates')
    player_video = request.files.get('player_video')  # Corrected typo from request.files.geta

    comments = request.form.get('comments', '')

    # Log the data being submitted for debugging
    print("Submitting Player Profile:", {
        'FirstName': first_name,
        'LastName': last_name,
        'DOB': dob,
        'Gender': gender,
        'HomeAddress': home_address,
        'StreetAddress': street_address,
        'City': city,
        'State': state,
        'Pincode': pincode,
        'PlayingExperience': playing_experience,
        'TeamsPlayed': teams_played,
        'Game': game,
        'Height': height,
        'Weight': weight,
        'Comments': comments,
        'Resume': resume.filename if resume else None,
        'ProfilePhoto': profile_photo.filename if profile_photo else None,
        'PlayerVideo': player_video.filename if player_video else None,
        'SportsCertificates': [cert.filename for cert in sports_certificates],
        'HealthCertificates': [cert.filename for cert in health_certificates]
    })

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Define the upload folder and ensure it exists
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)

        # Save the files (resume, profile photo, certificates, player video)
        resume_filename = secure_filename(resume.filename) if resume else ''
        profile_photo_filename = secure_filename(profile_photo.filename) if profile_photo else ''
        player_video_filename = secure_filename(player_video.filename) if player_video else ''
        sports_certificates_filenames = [secure_filename(certificate.filename) for certificate in sports_certificates]
        health_certificates_filenames = [secure_filename(certificate.filename) for certificate in health_certificates]

        resume_path = os.path.join(upload_folder, resume_filename) if resume else ''
        profile_photo_path = os.path.join(upload_folder, profile_photo_filename) if profile_photo else ''
        player_video_path = os.path.join(upload_folder, player_video_filename) if player_video else ''
        sports_certificates_paths = [os.path.join(upload_folder, filename) for filename in sports_certificates_filenames]
        health_certificates_paths = [os.path.join(upload_folder, filename) for filename in health_certificates_filenames]

        if resume:
            resume.save(resume_path)
        if profile_photo:
            profile_photo.save(profile_photo_path)
        if player_video:
            player_video.save(player_video_path)
        for certificate, path in zip(sports_certificates, sports_certificates_paths):
            certificate.save(path)
        for certificate, path in zip(health_certificates, health_certificates_paths):
            certificate.save(path)

        certificates_paths = ','.join(sports_certificates_paths + health_certificates_paths)

        # Insert the form data into the PlayerProfile table
        cursor.execute(''' 
            INSERT INTO PlayerProfile 
            (FirstName, LastName, DOB, Gender, HomeAddress, StreetAddress, City, State, Pincode, PlayingExperience, TeamsPlayed, Game, Height, Weight, Resume, ProfilePhoto, VideoPath, Certificates, Comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        ''', (first_name, last_name, dob, gender, home_address, street_address, city, state, pincode, playing_experience, teams_played, game, height, weight, resume_path, profile_photo_path, player_video_path, certificates_paths, comments))

        conn.commit()
        flash('Profile submitted successfully!', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('base'))



@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    # Redirect to the home page after logout
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)  

# if __name__ == '__main__':
#     app.run(host='0.0.0.0',port=5000)  
 