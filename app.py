
from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
import os

app = Flask(__name__, static_folder="frontend")

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['bitm_chatbot_db']

# Serve frontend files
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# Chatbot API endpoint
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message', '').strip().lower()

    # Greetings
    if user_input in ["hi", "hello", "hey", "heyy","hii"]:
        return jsonify({"response": "Hi! I'm BITM admission chatbot.... I can help you with: Admission Process, Admission, and Placements."})
    elif user_input == "placements":
        return jsonify({"response": "Placement options available for: MCA, MBA, BE.\nPlease specify one (e.g., 'placement BE')."})
    # Admission Process
    elif user_input == "admission process":
        process = db['admission_process'].find_one({}, {"_id": 0})
        return jsonify({"response": process['details'] if process else "No admission process info available."})

    # Admission Programs
    elif user_input == "admission":
        return jsonify({"response": "Available programs: MCA, MBA, BE."})

    # Program Details (MCA, MBA, BE)
    elif user_input in ["mca", "mba", "be"]:
        if user_input == "be":
            branches = db['branches'].find({"program": "BE"}, {"_id": 1})
            branch_list = [branch['_id'].lower() for branch in branches]
            return jsonify({"response": f"Available branches for BE: {', '.join(branch_list)}."})
        else:
            program = db['programs'].find_one({"_id": user_input.upper()}, {"_id": 0, "details": 1})
            return jsonify({"response": program['details'] if program else f"No info available for {user_input.upper()}."})

    
    elif user_input in ["cse", "aiml", "eee", "ece", "civil", "mech", "cs-ds", "cs-ai"]:
        branch = db['branches'].find_one({"_id": user_input.upper()}, {"_id": 0, "details": 1})
        if branch:
            placements = db['placements'].find({"branch": user_input.upper()}, {"_id": 0, "year": 1, "stats": 1}).sort("year", -1).limit(4)
            placement_list = [
                f"Year: {placement['year']}, Stats: {placement['stats']}" 
                for placement in placements
            ]
            placement_response = "\n".join(placement_list) if placement_list else "No placement info available."
            return jsonify({"response": f"{branch['details']}\n\nPlacement Info:\n{placement_response}"})
        else:
            return jsonify({"response": f"No info available for {user_input.upper()}."})
        
    # Placement Info
    elif user_input.startswith("placement "):
        query = user_input.replace("placement ", "").strip()
        
        if query in ["mca", "mba"]:
            placements = db['placements'].find({"program": query.upper()}, {"_id": 0, "year": 1, "stats": 1}).sort("year", -1).limit(4)
            placement_list = [f"Year: {placement['year']}, Stats: {placement['stats']}" for placement in placements]
            return jsonify({"response": "\n".join(placement_list) if placement_list else f"No placement info available for {query.upper()}."})
        elif query in ["be"]:
             return jsonify({"response": "Placement options available for BE are:cse,aiml,eee,ece,civil,mech,cs-ai,cs-ds.\nPlease specify one (e.g., 'placement cse')."})

        elif query in ["cse", "aiml", "eee", "ece", "civil", "mech", "cs-ds", "cs-ai"]:
            placements = db['placements'].find({"branch": query.upper()}, {"_id": 0, "year": 1, "stats": 1}).sort("year", -1).limit(4)
            placement_list = [f"Year: {placement['year']}, Stats: {placement['stats']}" for placement in placements]
            return jsonify({"response": "\n".join(placement_list) if placement_list else f"No placement info available for {query.upper()}."})

        else:
            return jsonify({"response": "Invalid program or branch specified. Please try again."})


    # Default response for unrecognized input
    else:
        return jsonify({"response": "Sorry, I couldn't understand that...Please enter a correct keyword...(OR) For more info, visit www.bitm.edu.in."})


if __name__ == '__main__':
    app.run(debug=True)
