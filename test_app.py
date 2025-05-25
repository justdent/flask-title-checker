import unittest
from app import app, db, User
from flask import url_for

class UserLoginTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Add a sample user to the test database
            sample_user = User(username='testuser', email='test@example.com')
            sample_user.set_password('password123')
            db.session.add(sample_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # TC8.1: Verify user can successfully log in
    def test_valid_login(self):
        response = self.app.post('/user_login', data=dict(email='test@example.com', password='password123'))
        self.assertIn(b'Login successful!', response.data)

    # TC8.2: Verify error message on invalid login credentials
    def test_invalid_login(self):
        response = self.app.post('/user_login', data=dict(email='test@example.com', password='wrongpassword'))
        self.assertIn(b'Invalid credentials!', response.data)

    # TC8.3: Verify account lock after multiple failed attempts (if implemented)
    # You can add logic here once account locking is in place.

if __name__ == '__main__':
    unittest.main()
