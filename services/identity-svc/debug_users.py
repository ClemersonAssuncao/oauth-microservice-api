import sqlite3

conn = sqlite3.connect('identity.db')
cursor = conn.cursor()
cursor.execute('SELECT username, email, hashed_password FROM users')
print('Users in database:')
for row in cursor.fetchall():
    print(f'Username: {row[0]}, Email: {row[1]}, Hash: {row[2][:60]}...')
conn.close()
