from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def fetch_movie_thumbnail(movie_name):
    # Replace 'YOUR_API_KEY' with your actual OMDB API key
    api_key = "d5f946f9"
    base_url = "http://www.omdbapi.com/"

    # Prepare the API request
    params = {
        "t": movie_name,
        "apikey": api_key
    }

    try:
        # Send a GET request to the API
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Parse the JSON response
        movie_data = response.json()
        if movie_data.get("Response") == "True":
            # Get the poster URL
            poster_url = movie_data.get("Poster")
            if poster_url and poster_url != "N/A":
                # Fetch the poster image
                poster_response = requests.get(poster_url)
                poster_response.raise_for_status()

                # Return the image bytes
                image = Image.open(BytesIO(poster_response.content))
                img_io = BytesIO()
                image.save(img_io, 'JPEG')
                img_io.seek(0)
                return img_io, "image/jpeg"
            else:
                return {"error": "No thumbnail found"}, "application/json"
        else:
            return {"error": f"Movie not found: {movie_name}"}, "application/json"
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching movie details: {e}"}, "application/json"

@app.route('/movie_thumbnail', methods=['GET'])
def movie_thumbnail():
    movie_name = request.args.get('movie_name')
    if not movie_name:
        return jsonify({"error": "movie_name parameter is required"}), 400

    result, content_type = fetch_movie_thumbnail(movie_name)
    if content_type == "application/json":
        return jsonify(result), 404  # Return error JSON
    else:
        return send_file(result, mimetype=content_type)  # Return image


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
