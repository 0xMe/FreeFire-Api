import requests
import Proto.compiled.PlayerPersonalShow_pb2
import Proto.compiled.PlayerStats_pb2
import Proto.compiled.PlayerCSStats_pb2
import Proto.compiled.SearchAccountByName_pb2
from Utilities.until import encode_protobuf, decode_protobuf
import json
from Configuration.APIConfiguration import RELEASEVERSION, DEBUG



def search_account_by_keyword(server_url, auth_token, keyword):
    """
    Perform a fuzzy account search by keyword.

    Args:
        server_url (str): Base URL of the API server.
        auth_token (str): Bearer token used for authentication.
        keyword (str): Search term to match player names.

    Returns:
        dict: Parsed JSON response containing matching accounts.

    Raises:
        ConnectionError: If network connection fails or times out.
        ValueError: If protobuf encoding or decoding fails.
        RuntimeError: For invalid or empty API responses.
    """
    try:
        # --- Endpoint & Payload ---
        endpoint = f"{server_url}/FuzzySearchAccountByName"
        try:
            payload = encode_protobuf(
                {"keyword": str(keyword)},
                Proto.compiled.SearchAccountByName_pb2.request()
            )
        except Exception as e:
            raise ValueError(f"Failed to encode protobuf payload: {e}")

        # --- Request Headers ---
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; A063 Build/TKQ1.221220.001)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Expect": "100-continue",
            "Authorization": f"Bearer {auth_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": RELEASEVERSION,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # --- Execute Request ---
        try:
            response = requests.post(endpoint, data=payload, headers=headers, timeout=15)
            response.raise_for_status()
            if DEBUG:
                print("[I] RES:", response.content, "\n")
        except requests.exceptions.Timeout:
            raise ConnectionError("Request timed out while contacting server.")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Failed to connect to the server.")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"HTTP error {response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request error: {e}")

        if not response.content:
            raise RuntimeError("Empty response received from server.")

        # --- Decode Response ---
        try:
            decoded = decode_protobuf(
                response.content,
                Proto.compiled.SearchAccountByName_pb2.response
            )
        except Exception as e:
            raise ValueError(f"Failed to decode protobuf response: {e}")

        return json.loads(json.dumps(decoded, default=str))

    except Exception as e:
        # Catch any unexpected runtime issues
        raise RuntimeError(f"Unhandled error in search_account_by_keyword: {e}")

def get_player_personal_show(serverurl, authorization, account_id, need_gallery_info=False, call_sign_src=7):
    """
    Get player personal show data
    
    Args:
        authorization (str): Bearer token for authentication
        account_id (int): Player account ID
        need_gallery_info (bool): Whether to include gallery info, default False
        call_sign_src (int): Call sign source, default 7
    
    Returns:
        dict: JSON response data
    """
    url = f"{serverurl}/GetPlayerPersonalShow"

    encrypted_payload = encode_protobuf({
        "accountId": account_id,
        "callSignSrc": call_sign_src,
        "needGalleryInfo": need_gallery_info,
    }, Proto.compiled.PlayerPersonalShow_pb2.request())

    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; A063 Build/TKQ1.221220.001)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'Authorization': f"Bearer {authorization}",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': RELEASEVERSION,
        'Content-Type': "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, data=encrypted_payload, headers=headers)
    if DEBUG:
        print("[I] RES:", response.content, "\n")
    try:
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Decode protobuf response
        message = decode_protobuf(response.content, Proto.compiled.PlayerPersonalShow_pb2.response)
        
        # Convert to JSON
        json_data = json.loads(json.dumps(message, default=str))
        return json_data
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {response.text}")
        return None
    except Exception as e:
        print(f"Error processing response: {e}")
        return None

def get_player_stats(authorization, serverurl, mode, uid, match_type="CAREER"):
    """
    Get player statistics for BR or CS mode
    
    Args:
        mode (str): "br" or "cs"
        uid (int): Player account ID
        match_type (str): "CAREER", "NORMAL", or "RANKED"
    
    Returns:
        dict: Player statistics data
    
    Raises:
        ValueError: For invalid input parameters
        ConnectionError: For network-related errors
        ProtobufError: For protobuf encoding/decoding errors
        APIError: For API response errors
    """
    
    try:
        # Validate inputs
        if not isinstance(uid, (int, str)) or not str(uid).isdigit():
            raise ValueError(f"Invalid UID: {uid}. Must be a numeric value.")
        
        uid = int(uid)  # Convert to int if it's a numeric string
        
        mode = mode.lower()
        if mode not in ["br", "cs"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'br' or 'cs'")
        
        match_type = match_type.upper()
        if match_type not in ["CAREER", "NORMAL", "RANKED"]:
            raise ValueError(f"Invalid match type: {match_type}. Must be 'CAREER', 'NORMAL', or 'RANKED'")
        
        # Map match type to numeric values
        if mode == "br":
            type_mapping = {
                "CAREER": 0,
                "NORMAL": 1, 
                "RANKED": 2
            }
            url = f"{serverurl}/GetPlayerStats"
            proto_module = Proto.compiled.PlayerStats_pb2
        else:  # cs mode
            type_mapping = {
                "CAREER": 0,
                "NORMAL": 1,
                "RANKED": 6
            }
            url = f"{serverurl}/GetPlayerTCStats"
            proto_module = Proto.compiled.PlayerCSStats_pb2
        
        matchmode = type_mapping[match_type]
        
        # Prepare payload based on mode
        if mode == "br":
            payload_data = {
                "accountid": uid,
                "matchmode": matchmode,
            }
        else:  # cs mode
            payload_data = {
                "accountid": uid,
                "gamemode": 15,  # CS mode
                "matchmode": matchmode,
            }
        
        # Encode payload
        try:
            encrypted_payload = encode_protobuf(payload_data, proto_module.request())
        except Exception as e:
            raise ProtobufError(f"Failed to encode protobuf payload: {str(e)}")
        
        # Prepare headers
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; A063 Build/TKQ1.221220.001)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Expect': "100-continue",
            'Authorization': f"Bearer {authorization}",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': RELEASEVERSION,
            'Content-Type': "application/x-www-form-urlencoded"
        }
        
        # Make request with timeout
        try:
            response = requests.post(url, data=encrypted_payload, headers=headers, timeout=30)
            response.raise_for_status()  # Raises HTTPError for bad status codes
            if DEBUG:
                print("[I] RES:", response.content, "\n")
        except requests.exceptions.Timeout:
            raise ConnectionError("Request timed out after 30 seconds")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Failed to connect to the server")
        except requests.exceptions.HTTPError as e:
            raise APIError(f"HTTP error {response.status_code}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {str(e)}")
        
        # Check if response content is valid
        if not response.content:
            raise APIError("Empty response from server")
        
        # Decode response
        try:
            message = decode_protobuf(response.content, proto_module.response)
        except Exception as e:
            raise ProtobufError(f"Failed to decode protobuf response: {str(e)}")
        
        return message
        
    except (ValueError, ConnectionError, ProtobufError, APIError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise APIError(f"Unexpected error: {str(e)}")