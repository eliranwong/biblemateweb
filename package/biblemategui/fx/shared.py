import sqlite3, os
import base64
from typing import Optional
from biblemategui import BIBLEMATEGUI_DATA

def get_image_data_uri(module_table: str, image_path_key: str, mime_type: str = "image/png") -> Optional[str]:
    """
    Retrieves image BLOB from SQLite, encodes it to base64, and formats it as a Data URI.

    Args:
        module_table (str): Path to the SQLite table.
        image_path_key (str): The unique 'path' value (e.g., file name) to retrieve.
        mime_type (str): The MIME type of the stored image (e.g., 'image/png', 'image/jpeg').

    Returns:
        Optional[str]: The complete Data URI string, or None if the image is not found.
    """
    db_path = os.path.join(BIBLEMATEGUI_DATA, "images.sqlite")
    conn = None
    try:
        # 1. Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 2. Retrieve the BLOB data
        # Use a parameterized query to prevent SQL injection
        cursor.execute(f"SELECT image FROM {module_table} WHERE path = ?", (image_path_key,))
        
        row = cursor.fetchone()
        
        if row is None:
            print(f"Error: No image found with path: {image_path_key}")
            return None
            
        # The BLOB data is the first (and only) element in the row tuple
        image_blob = row[0]
        
        # 3. Encode the BLOB data to base64
        # b64encode converts binary data to a bytes-like object containing base64 data
        base64_bytes = base64.b64encode(image_blob)
        
        # 4. Decode the bytes to a string for use in HTML
        base64_string = base64_bytes.decode('utf-8')
        
        # 5. Format as a Data URI
        # The format is: data:[<MIME-type>];base64,<data>
        data_uri = f"data:{mime_type};base64,{base64_string}"
        
        return data_uri

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    finally:
        if conn:
            conn.close()