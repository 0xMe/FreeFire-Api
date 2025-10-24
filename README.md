<div align="center">
  <img src="https://raw.githubusercontent.com/0xMe/FreeFire-Api/refs/heads/main/API.png" alt="API Screenshot">
</div>

# FreeFire-Api

FreeFire-Api is a lightweight Python project that interacts with internal Free Fire APIs using compiled Protocol Buffers. It enables structured API communication, making it easier to parse, encode, and serve game-related data such as player profiles, regions, and server details.

## Features

- Interacts directly with Free Fire's internal game APIs.
- Uses Protocol Buffers for serialization and deserialization of network messages.
- Provides endpoints for player statistics, personal show data, and more.
- Implements encryption for secure API communication.
- Built with Flask for easy RESTful API deployment.

## Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/0xMe/FreeFire-Api.git
   cd FreeFire-Api
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Add your account credentials to `./Configuration/AccountConfiguration.json` for each supported server.
   - Make sure your protobuf files are compiled and available in `Proto/compiled/`.

4. **Run the API server**
   ```sh
   python app.py
   ```
   The API will run on `http://0.0.0.0:5000`.

## Usage

### REST Endpoints

#### Get Player Stats

`GET /get_player_stats`

Query Parameters:
- `server` (default: "IND") — The server region.
- `uid` — The player UID.
- `gamemode` (default: "br") — Game mode (`br`, `cs`).
- `matchmode` (default: "CAREER") — Match mode. (`CAREER`, `NORMAL`, `RANKED`)

Example:
    https://freefire-api-six.vercel.app/get_player_stats?server=ind&uid=11959685790&matchmode=RANKED&gamemode=br

#### Get Player Personal Show

`GET /get_player_personal_show`

Query Parameters:
- `server` (default: "IND") — The server region.
- `uid` — The player UID.
- `need_gallery_info` (optional) — Whether to include gallery info.
- `call_sign_src` (default: 7) — Call sign source.

Example:
    https://freefire-api-six.vercel.app/get_player_personal_show?server=ind&uid=1633864660

### API Responses

Responses are in JSON format. Example error messages are provided for invalid parameters, authentication failures, and data not found.

## Project Structure

- `app.py` — Flask application with REST endpoints.
- `Api/Account.py` — Garena authentication and login functions.
- `Api/InGame.py` — Game data retrieval functions.
- `Utilities/until.py` — Utility functions for encryption and protocol buffer handling.
- `Configuration/` — Contains configuration files, including AES keys and API version.

## Requirements

- Python
- Flask
- pycryptodome
- protobuf

Refer to `requirements.txt` for additional dependencies.

## Contributing

Feel free to fork and submit pull requests. Open issues for bug reports and feature requests.

## Author

[0xMe](https://github.com/0xMe)
