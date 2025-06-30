from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId
import random
import json

app = Flask(__name__)
app.secret_key = '1879a49b06ff9b4ef1efd9b63dbd911df26b566d1d0769dd5726607d63d0ct55'

# MongoDB connection
client = MongoClient('mongodb+srv://lsriram208:ZWXpeGPNnnumulxy@cluster0.qb4hnq8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['travel_booking_db']

# Collections
users_collection = db['users']
flights_collection = db['flights']
trains_collection = db['trains']
bookings_collection = db['bookings']
hotels_collection = db['hotels']

# --- Sample Data Insertion Functions ---
def insert_sample_train_data():
    if trains_collection.count_documents({}) == 0:
        sample_trains = [
            {"_id": ObjectId(), "name": "Duronto Express", "train_number": "12285", "source": "Hyderabad", "destination": "Delhi", "departure_time": "07:00 AM", "arrival_time": "05:00 AM (next day)", "price": 1800, "date": "2025-07-10"},
            {"_id": ObjectId(), "name": "AP Express", "train_number": "12723", "source": "Hyderabad", "destination": "Vijayawada", "departure_time": "09:00 AM", "arrival_time": "03:00 PM", "price": 450, "date": "2025-07-10"},
            {"_id": ObjectId(), "name": "Gouthami Express", "train_number": "12737", "source": "Guntur", "destination": "Hyderabad", "departure_time": "08:00 PM", "arrival_time": "06:00 AM (next day)", "price": 600, "date": "2025-07-10"},
            {"_id": ObjectId(), "name": "Chennai Express", "train_number": "12839", "source": "Bengaluru", "destination": "Chennai", "departure_time": "10:30 AM", "arrival_time": "05:30 PM", "price": 750, "date": "2025-07-11"},
            {"_id": ObjectId(), "name": "Mumbai Mail", "train_number": "12101", "source": "Hyderabad", "destination": "Mumbai", "departure_time": "06:00 PM", "arrival_time": "09:00 AM (next day)", "price": 1200, "date": "2025-07-10"},
            {"_id": ObjectId(), "name": "Godavari Express", "train_number": "12720", "source": "Vijayawada", "destination": "Hyderabad", "departure_time": "05:00 PM", "arrival_time": "11:00 PM", "price": 400, "date": "2025-07-10"},
        ]
        trains_collection.insert_many(sample_trains)
        print("Sample train data inserted into MongoDB.")

def insert_sample_flight_data():
    if flights_collection.count_documents({}) == 0:
        sample_flights = [
            {"_id": ObjectId(), "airline": "IndiGo", "flight_number": "6E 2345", "source": "Delhi", "destination": "Mumbai", "departure_time": "10:00 AM", "arrival_time": "12:00 PM", "price": 5000, "date": "2025-07-15"},
            {"_id": ObjectId(), "airline": "Air India", "flight_number": "AI 400", "source": "Mumbai", "destination": "Bengaluru", "departure_time": "03:00 PM", "arrival_time": "05:00 PM", "price": 6500, "date": "2025-07-15"},
            {"_id": ObjectId(), "airline": "SpiceJet", "flight_number": "SG 876", "source": "Bengaluru", "destination": "Chennai", "departure_time": "08:00 AM", "arrival_time": "09:00 AM", "price": 3000, "date": "2025-07-16"},
            {"_id": ObjectId(), "airline": "Vistara", "flight_number": "UK 990", "source": "Chennai", "destination": "Hyderabad", "departure_time": "11:00 AM", "arrival_time": "12:30 PM", "price": 4500, "date": "2025-07-16"},
        ]
        flights_collection.insert_many(sample_flights)
        print("Sample flight data inserted into MongoDB.")

def insert_sample_hotel_data():
    if hotels_collection.count_documents({}) == 0:
        sample_hotels = [
            {"_id": ObjectId(), "name": "The Grand Hotel", "location": "Mumbai", "price_per_night": 4000},
            {"_id": ObjectId(), "name": "City Centre Inn", "location": "Delhi", "price_per_night": 2500},
            {"_id": ObjectId(), "name": "Royal Residency", "location": "Bengaluru", "price_per_night": 3500},
            {"_id": ObjectId(), "name": "Seaside Resort", "location": "Chennai", "price_per_night": 5000},
        ]
        hotels_collection.insert_many(sample_hotels)
        print("Sample hotel data inserted into MongoDB.")

def insert_default_user():
    default_email = "lsriram208@gmail.com"
    default_password = "123r"
    default_fullname = "lingineni sriam"
    user = users_collection.find_one({'email': default_email})
    if not user:
        hashed_password = generate_password_hash(default_password)
        users_collection.insert_one({'fullname': default_fullname, 'email': default_email, 'password': hashed_password})
        print("Default user inserted.")
    elif user.get('fullname') != default_fullname:
        users_collection.update_one(
            {'email': default_email},
            {'$set': {'fullname': default_fullname}}
        )
        print(f"Default user '{default_email}' fullname updated to '{default_fullname}'.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match!')
        if users_collection.find_one({'email': email}):
            return render_template('register.html', error='Email already exists!')
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'fullname': fullname, 'email': email, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['email'] = email
            session['fullname'] = user.get('fullname', email)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message='Invalid email or password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('fullname', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    user_email = session['email']
    user_fullname = session.get('fullname', user_email)

    # Fetch bookings for the current user, excluding those with 'Cancelled' status
    user_bookings = list(bookings_collection.find(
        {'user_email': user_email, 'status': {'$ne': 'Cancelled'}}
    ).sort('booking_date', -1))

    for booking in user_bookings:
        # Convert ObjectId to string for template rendering
        if '_id' in booking and isinstance(booking['_id'], ObjectId):
            booking['booking_id'] = str(booking['_id'])
        else:
            booking['booking_id'] = None # Or handle cases where _id might be missing/invalid

        # Ensure 'status' field exists, default to 'Confirmed' if not present for older bookings
        if 'status' not in booking:
            booking['status'] = 'Confirmed' # Default status if not set in DB
            # Optional: Update the document in DB to set this default if you want persistence
            # bookings_collection.update_one({'_id': booking['_id']}, {'$set': {'status': 'Confirmed'}})

        # Populate display fields based on booking type
        booking_type_lower = booking.get('booking_type', '').lower()
        booking['booking_type'] = booking_type_lower.capitalize() # For display: e.g., 'Bus', 'Hotel'

        if booking_type_lower == 'flight':
            booking['airline'] = booking.get('airline', 'N/A')
            booking['flight_number'] = booking.get('flight_number', 'N/A')
            booking['origin'] = booking.get('source', 'N/A') # Renamed for clarity in HTML
            booking['destination'] = booking.get('destination', 'N/A')
            booking['departure_time'] = booking.get('departure_time', 'N/A')
            booking['arrival_time'] = booking.get('arrival_time', 'N/A')
            booking['num_persons'] = booking.get('num_persons', 'N/A')
            booking['selected_seats'] = booking.get('selected_seats', [])
        elif booking_type_lower == 'hotel':
            booking['hotel_name'] = booking.get('hotel_name', 'N/A')
            booking['location'] = booking.get('location', 'N/A')
            booking['check_in_date'] = booking.get('check_in_date', 'N/A')
            booking['check_out_date'] = booking.get('check_out_date', 'N/A')
            booking['num_nights'] = booking.get('num_nights', 'N/A')
            booking['num_rooms'] = booking.get('num_rooms', 'N/A')
            booking['num_guests'] = booking.get('num_guests', 'N/A')
            # Assuming 'selected_rooms' might be a list of room numbers/types if applicable
            booking['selected_rooms'] = booking.get('selected_rooms', [])
        elif booking_type_lower == 'bus':
            booking['name'] = booking.get('name', 'N/A')
            booking['source'] = booking.get('source', 'N/A')
            booking['destination'] = booking.get('destination', 'N/A')
            booking['time'] = booking.get('time', 'N/A')
            booking['num_persons'] = booking.get('num_persons', 'N/A')
            booking['selected_seats'] = booking.get('selected_seats', [])
            booking['travel_date'] = booking.get('travel_date', 'N/A') # Use travel_date for consistency
        elif booking_type_lower == 'train':
            booking['name'] = booking.get('name', 'N/A')
            booking['train_number'] = booking.get('train_number', 'N/A')
            booking['source'] = booking.get('source', 'N/A')
            booking['destination'] = booking.get('destination', 'N/A')
            booking['departure_time'] = booking.get('departure_time', 'N/A')
            booking['arrival_time'] = booking.get('arrival_time', 'N/A')
            booking['num_persons'] = booking.get('num_persons', 'N/A')
            booking['selected_seats'] = booking.get('selected_seats', [])
            booking['travel_date'] = booking.get('travel_date', 'N/A') # Use travel_date for consistency

    return render_template('dashboard.html', name=user_fullname, bookings=user_bookings)

# --- Bus Search and Booking Flow ---
@app.route('/bus')
def bus():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('bus.html')

@app.route('/confirm_bus_booking', methods=['POST'])
def confirm_bus_booking():
    if 'email' not in session:
        return redirect(url_for('login'))
    name = request.form.get('name')
    source = request.form.get('source')
    destination = request.form.get('destination')
    time = request.form.get('time')
    bus_type = request.form.get('type')
    travel_date = request.form.get('date')
    try:
        price_per_person = float(request.form.get('price'))
        num_persons = int(request.form.get('persons'))
    except (TypeError, ValueError):
        return redirect(url_for('bus'))
    total_price = price_per_person * num_persons
    booking_details = {
        'name': name,
        'source': source,
        'destination': destination,
        'time': time,
        'type': bus_type,
        'price_per_person': price_per_person,
        'travel_date': travel_date,
        'num_persons': num_persons,
        'total_price': total_price,
        'booking_type': 'bus',
        'user_email': session['email'],
        'status': 'Confirmed' # Set default status for new bookings
    }
    session['pending_booking'] = booking_details
    return redirect(url_for('select_seats'))

# --- Train Search and Booking Flow ---
@app.route('/train')
def train():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('train.html')

@app.route('/confirm_train_booking', methods=['POST'])
def confirm_train_booking():
    if 'email' not in session:
        return redirect(url_for('login'))
    name = request.form.get('name')
    train_number = request.form.get('trainNumber')
    source = request.form.get('source')
    destination = request.form.get('destination')
    departure_time = request.form.get('departureTime')
    arrival_time = request.form.get('arrivalTime')
    travel_date = request.form.get('date')
    try:
        price_per_person = float(request.form.get('price'))
        num_persons = int(request.form.get('persons'))
    except (TypeError, ValueError):
        return redirect(url_for('train'))
    total_price = price_per_person * num_persons
    booking_details = {
        'name': name,
        'train_number': train_number,
        'source': source,
        'destination': destination,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'price_per_person': price_per_person,
        'travel_date': travel_date,
        'num_persons': num_persons,
        'total_price': total_price,
        'booking_type': 'train',
        'user_email': session['email'],
        'status': 'Confirmed' # Set default status for new bookings
    }
    session['pending_booking'] = booking_details
    return redirect(url_for('select_seats'))

# --- Flight Search and Booking Flow ---
@app.route('/flight', methods=['GET', 'POST'])
def flight():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('flight.html')

@app.route('/confirm_flight_booking', methods=['POST'])
def confirm_flight_booking():
    if 'email' not in session:
        return redirect(url_for('login'))
    airline = request.form.get('airline')
    flight_number = request.form.get('flightNumber')
    source = request.form.get('source')
    destination = request.form.get('destination')
    departure_time = request.form.get('departureTime')
    arrival_time = request.form.get('arrivalTime')
    travel_date = request.form.get('date')
    try:
        price_per_person = float(request.form.get('price'))
        num_persons = int(request.form.get('persons'))
    except (TypeError, ValueError):
        return redirect(url_for('flight'))
    total_price = price_per_person * num_persons
    booking_details = {
        'airline': airline,
        'flight_number': flight_number,
        'source': source,
        'destination': destination,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'price_per_person': price_per_person,
        'travel_date': travel_date,
        'num_persons': num_persons,
        'total_price': total_price,
        'booking_type': 'flight',
        'user_email': session['email'],
        'status': 'Confirmed' # Set default status for new bookings
    }
    session['pending_booking'] = booking_details
    return redirect(url_for('select_seats'))

# --- Seat Selection and Confirmation Step ---
@app.route('/select_seats', methods=['GET'])
def select_seats():
    if 'email' not in session:
        return redirect(url_for('login'))
    booking_details = session.get('pending_booking')
    if not booking_details:
        return redirect(url_for('dashboard'))
    all_seats = [f"{row}{num}" for row in ['A', 'B', 'C', 'D', 'E'] for num in range(1, 7)]
    dummy_booked_seats = random.sample(all_seats, k=random.randint(5, 10))
    vehicle_type = "N/A"
    if booking_details.get('booking_type') == 'bus':
        vehicle_type = booking_details.get('type', 'Bus')
    elif booking_details.get('booking_type') == 'train':
        vehicle_type = "Train"
    elif booking_details.get('booking_type') == 'flight':
        vehicle_type = "Flight"
    time_display = booking_details.get('time')
    if booking_details.get('departure_time') and booking_details.get('arrival_time'):
        time_display = f"{booking_details.get('departure_time')} - {booking_details.get('arrival_time')}"
    return render_template(
        'seat.html',
        name=booking_details.get('name', booking_details.get('airline')),
        booking_type=booking_details.get('booking_type'),
        source=booking_details.get('source'),
        destination=booking_details.get('destination'),
        time=time_display,
        vehicle_type=vehicle_type,
        price_per_person=booking_details.get('price_per_person'),
        travel_date=booking_details.get('travel_date'),
        num_persons=booking_details.get('num_persons'),
        booked_seats=dummy_booked_seats
    )

@app.route('/book_selected_seats', methods=['POST'])
def book_selected_seats():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401
    data = request.get_json()
    booking_data = session.pop('pending_booking', None)
    if not booking_data:
        return jsonify({'success': False, 'message': 'No pending booking found for seat selection.'}), 400
    if not data or 'selectedSeats' not in data:
        return jsonify({'success': False, 'message': 'No seats selected.'}), 400
    selected_seats = data.get('selectedSeats', [])
    booking_data['selected_seats'] = selected_seats
    booking_data['total_price'] = booking_data['price_per_person'] * booking_data['num_persons']
    session['final_booking'] = booking_data  # Store for confirmation

    # Decide which confirmation page to use
    if booking_data['booking_type'] == 'bus':
        redirect_url = url_for('confirm_seat_booking')
    elif booking_data['booking_type'] == 'train':
        redirect_url = url_for('confirm_train_seat_booking')
    elif booking_data['booking_type'] == 'flight':
        redirect_url = url_for('confirm_flight_seat_booking')
    else:
        redirect_url = url_for('dashboard')

    return jsonify({
        'success': True,
        'message': 'Seats selected! Redirecting to confirmation...',
        'redirect': redirect_url
    })

# --- Confirmation Pages for Seat Bookings ---
@app.route('/confirm_seat_booking')
def confirm_seat_booking():
    booking = session.get('final_booking')
    if not booking:
        return redirect(url_for('dashboard'))
    return render_template('confirm.html', booking=booking)

@app.route('/confirm_train_seat_booking')
def confirm_train_seat_booking():
    booking = session.get('final_booking')
    if not booking:
        return redirect(url_for('dashboard'))
    return render_template('confirmtrain.html', booking=booking)

@app.route('/confirm_flight_seat_booking')
def confirm_flight_seat_booking():
    booking = session.get('final_booking')
    if not booking:
        return redirect(url_for('dashboard'))
    return render_template('confirmflight.html', booking=booking)

# --- Final Confirmation Endpoints ---
@app.route('/final_confirm_seat_booking', methods=['POST'])
def final_confirm_seat_booking():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401
    booking_data = session.pop('final_booking', None)
    if not booking_data:
        return jsonify({'success': False, 'message': 'No booking to confirm.', 'redirect': url_for('dashboard')}), 400
    try:
        booking_data['booking_date'] = datetime.now().isoformat()
        bookings_collection.insert_one(booking_data)
        return jsonify({'success': True, 'message': 'Booking confirmed!', 'redirect': url_for('dashboard')})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to confirm booking: {str(e)}', 'redirect': url_for('dashboard')}), 500

@app.route('/final_confirm_train_seat_booking', methods=['POST'])
def final_confirm_train_seat_booking():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401
    booking_data = session.pop('final_booking', None)
    if not booking_data:
        return jsonify({'success': False, 'message': 'No booking to confirm.', 'redirect': url_for('dashboard')}), 400
    try:
        booking_data['booking_date'] = datetime.now().isoformat()
        bookings_collection.insert_one(booking_data)
        return jsonify({'success': True, 'message': 'Train booking confirmed!', 'redirect': url_for('dashboard')})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to confirm booking: {str(e)}', 'redirect': url_for('dashboard')}), 500

@app.route('/final_confirm_flight_seat_booking', methods=['POST'])
def final_confirm_flight_seat_booking():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401
    booking_data = session.pop('final_booking', None)
    if not booking_data:
        return jsonify({'success': False, 'message': 'No booking to confirm.', 'redirect': url_for('dashboard')}), 400
    try:
        booking_data['booking_date'] = datetime.now().isoformat()
        bookings_collection.insert_one(booking_data)
        return jsonify({'success': True, 'message': 'Flight booking confirmed!', 'redirect': url_for('dashboard')})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to confirm booking: {str(e)}', 'redirect': url_for('dashboard')}), 500

# --- Hotel Search and Booking Flow ---
# Corrected route from '/hostel' to '/hotel'
@app.route('/hotel')
def hotel():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('hotel.html')

@app.route('/confirm_hotel_booking', methods=['POST'])
def confirm_hotel_booking():
    if 'email' not in session:
        return redirect(url_for('login'))
    hotel_name = request.form.get('hotelName')
    location = request.form.get('location')
    check_in_date = request.form.get('checkInDate')
    check_out_date = request.form.get('checkOutDate')
    try:
        num_rooms = int(request.form.get('numRooms'))
        num_guests = int(request.form.get('numGuests'))
        price_per_night = float(request.form.get('pricePerNight'))
        num_nights = int(request.form.get('numNights'))
    except (TypeError, ValueError):
        # Corrected redirect to '/hotel'
        return redirect(url_for('hotel'))
    total_price = price_per_night * num_rooms * num_nights
    booking_details = {
        'hotel_name': hotel_name,
        'location': location,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'num_rooms': num_rooms,
        'num_guests': num_guests,
        'price_per_night': price_per_night,
        'num_nights': num_nights,
        'total_price': total_price,
        'booking_type': 'hotel',
        'user_email': session['email'],
        'status': 'Confirmed' # Set default status for new bookings
    }
    session['pending_booking'] = booking_details
    return render_template('confirmhotel.html', booking=booking_details)

@app.route('/final_confirm_hotel_booking', methods=['POST'])
def final_confirm_hotel_booking():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401
    booking_data = session.pop('pending_booking', None)
    if not booking_data:
        return jsonify({'success': False, 'message': 'No pending booking to confirm.', 'redirect': url_for('dashboard')}), 400
    try:
        booking_data['booking_date'] = datetime.now().isoformat()
        bookings_collection.insert_one(booking_data)
        return jsonify({
            'success': True,
            'message': 'Hotel booking confirmed successfully!',
            'redirect': url_for('dashboard')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to confirm hotel booking: {str(e)}', 'redirect': url_for('dashboard')}), 500

# --- Cancel Booking Route ---
# Changed route name from '/cancel' to '/cancel_booking' to match HTML form action
@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    # Ensure user is logged in
    if 'email' not in session:
        return redirect(url_for('login'))

    # Get the booking_id from the form submission
    booking_id_str = request.form.get('booking_id')
    user_email = session['email']

    if not booking_id_str:
        # If no booking ID is provided, redirect back to dashboard
        return redirect(url_for('dashboard'))

    try:
        # Convert the string booking_id to ObjectId for MongoDB query
        object_id_to_update = ObjectId(booking_id_str)

        # Define the query to find the specific booking for the logged-in user
        query = {'_id': object_id_to_update, 'user_email': user_email}

        # Define the update operation: set the 'status' field to 'Cancelled'
        update_operation = {'$set': {'status': 'Cancelled'}}

        # Perform the update
        result = bookings_collection.update_one(query, update_operation)

        # Check if the booking was found and modified
        if result.modified_count > 0:
            print(f"Booking {booking_id_str} status updated to 'Cancelled'.")
        else:
            print(f"Booking {booking_id_str} not found or not owned by user {user_email}, or already cancelled.")
            # You might want to add a flash message here for the user
            # flash("Could not cancel booking. It may not exist or belong to you.")

    except InvalidId:
        print(f"Invalid booking ID format: {booking_id_str}")
        # flash("Invalid booking ID provided.")
    except Exception as e:
        print(f"An error occurred during cancellation: {e}")
        # flash("An unexpected error occurred during cancellation.")

    # Redirect back to the dashboard to show the updated status
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    insert_sample_train_data()
    insert_sample_flight_data()
    insert_sample_hotel_data()
    insert_default_user()
    app.run(debug=True)