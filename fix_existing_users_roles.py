"""
Fix Existing Users - Assign Admin Role
This script assigns ADMIN role to all existing users who don't have a role
"""
import psycopg2
from datetime import datetime

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "packoptima_db",
    "user": "packoptima_user",
    "password": "packoptima_password_change_in_production"
}

def fix_user_roles():
    """Assign ADMIN role to all users without a role"""
    print("\n" + "="*70)
    print("  Fixing Existing User Roles")
    print("="*70 + "\n")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Find users without roles
        cursor.execute("""
            SELECT u.id, u.email 
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            WHERE ur.id IS NULL
        """)
        
        users_without_roles = cursor.fetchall()
        
        if not users_without_roles:
            print("✓ All users already have roles assigned")
            cursor.close()
            conn.close()
            return
        
        print(f"Found {len(users_without_roles)} user(s) without roles:\n")
        
        # Assign ADMIN role to each user
        for user_id, email in users_without_roles:
            cursor.execute("""
                INSERT INTO user_roles (user_id, role, granted_at)
                VALUES (%s, %s, %s)
            """, (user_id, 'ADMIN', datetime.utcnow()))
            
            print(f"✓ Assigned ADMIN role to: {email}")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ Successfully assigned ADMIN role to {len(users_without_roles)} user(s)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = fix_user_roles()
    
    print("\n" + "="*70)
    if success:
        print("  ✓ COMPLETE: All users now have ADMIN role")
    else:
        print("  ✗ FAILED: Could not fix user roles")
    print("="*70 + "\n")
