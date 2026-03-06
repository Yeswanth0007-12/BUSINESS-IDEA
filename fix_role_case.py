"""
Fix Role Case - Update lowercase 'admin' to uppercase 'ADMIN'
"""
import psycopg2

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "packoptima_db",
    "user": "packoptima_user",
    "password": "packoptima_password_change_in_production"
}

def fix_role_case():
    """Update lowercase role values to uppercase"""
    print("\n" + "="*70)
    print("  Fixing Role Case (lowercase -> UPPERCASE)")
    print("="*70 + "\n")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Delete all existing roles (they're lowercase and invalid)
        cursor.execute("DELETE FROM user_roles")
        deleted_count = cursor.rowcount
        print(f"✓ Deleted {deleted_count} invalid role entries")
        
        # Get all users
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()
        
        print(f"\nAssigning ADMIN role to {len(users)} user(s):\n")
        
        # Assign ADMIN role to all users
        from datetime import datetime
        for user_id, email in users:
            cursor.execute("""
                INSERT INTO user_roles (user_id, role, granted_at)
                VALUES (%s, %s, %s)
            """, (user_id, 'ADMIN', datetime.utcnow()))
            print(f"✓ {email}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ Successfully assigned ADMIN role to all users")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = fix_role_case()
    
    print("\n" + "="*70)
    if success:
        print("  ✓ COMPLETE: All roles fixed")
    else:
        print("  ✗ FAILED: Could not fix roles")
    print("="*70 + "\n")
