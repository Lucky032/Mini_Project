from db_connection import get_db_connection

def test_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Test querying the PlayerProfile table
        cursor.execute("SELECT TOP 1 * FROM PlayerProfile")  # Change table name if necessary
        row = cursor.fetchone()

        if row:
            print("Connection successful! Row retrieved from PlayerProfile table:", row)
        else:
            print("No rows found in PlayerProfile table.")

    except Exception as e:
        print("Connection failed:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_connection()
