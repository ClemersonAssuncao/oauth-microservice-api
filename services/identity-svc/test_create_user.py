import asyncio
from interfaces.api.container import Container
from domain.entities.user import UserRole

async def test():
    container = Container()
    await container.database.create_tables()
    
    print("Creating admin user...")
    try:
        admin_user = await container.auth_service.register_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            roles=[UserRole.ADMIN, UserRole.USER]
        )
        print(f"✅ Admin user created: {admin_user.username}")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
    
    print("\nCreating test user...")
    try:
        test_user = await container.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="test123"
        )
        print(f"✅ Test user created: {test_user.username}")
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
    
    # Check database
    import sqlite3
    conn = sqlite3.connect('identity.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email FROM users')
    print('\n📋 Users in database:')
    for row in cursor.fetchall():
        print(f'  - Username: {row[0]}, Email: {row[1]}')
    conn.close()
    
    await container.database.close()

if __name__ == "__main__":
    asyncio.run(test())
