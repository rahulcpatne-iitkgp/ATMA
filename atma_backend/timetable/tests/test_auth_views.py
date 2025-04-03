from django.test import TestCase, Client
from django.urls import reverse
from timetable.models import User, Department

class AuthViewsTestCase(TestCase):
    """Tests for authentication views"""
    
    def setUp(self):
        self.client = Client()
        # Create a test department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            role='student',
            department=self.department
        )
    
    def test_login_view_get(self):
        """Test that login page loads correctly"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')
    
    def test_login_view_post_success(self):
        """Test successful login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, reverse('home'))
        
        # Check that user is authenticated
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
    
    def test_login_view_post_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page
        self.assertFormError(response.context['form'], None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
    
    def test_signup_view_get(self):
        """Test that signup page loads correctly"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/signup.html')
    
    def test_signup_view_post_success(self):
        """Test successful signup"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complex_password_123',
            'password2': 'complex_password_123',
            'role': 'student',
            'department': self.department.id
        })
        self.assertRedirects(response, reverse('home'))
        
        # Check that new user exists in the database
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check that user is authenticated
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
    
    def test_signup_view_post_invalid_data(self):
        """Test signup with invalid data (password mismatch)"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complex_password_123',
            'password2': 'different_password_456',
            'role': 'student',
            'department': self.department.id
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page
        self.assertFormError(response.context['form'], 'password2', "The two password fields didn’t match.")
        
        # Check that user was not created
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_logout_view(self):
        """Test logout functionality"""
        # First login
        self.client.login(username='testuser', password='testpassword123')
        
        # Then logout
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        
        # Check that user is no longer authenticated
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_check_username_ajax(self):
        """Test the AJAX username availability check"""
        # Test with existing username
        response = self.client.post(reverse('check_username'), {'username': 'testuser'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Username already taken', response.content.decode())
        
        # Test with new username
        response = self.client.post(reverse('check_username'), {'username': 'brandnewuser'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Username available', response.content.decode())
        
        # Test with empty username
        response = self.client.post(reverse('check_username'), {'username': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "")
