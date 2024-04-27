from json import JSONDecodeError

from django.test import TestCase, Client
from rest_framework.test import APIClient, APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from .models import Contact

# Create your tests here.
class ContactTestCase(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.data = {
            "name": "Charles Okeke",
            "email": "okekecharles91@gmail.com",
            "message": "This is a test message"
        }
        self.url = "/api/v1/contact/"
    
    def test_create_contact(self):
        '''
        test ContactViewSet create method using post method
        '''
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, HTTP_200_OK, "Wrong Status Code")
        self.assertEqual(Contact.objects.count(), 1, "Database contains other values")
        self.assertEqual(Contact.objects.first().title, "Charles Okeke", "Wrong Title")
    
    def test_create_contact_without_name(self):
        '''
        test ContactViewSet create method when name is not in data
        '''
        data = self.data
        data.pop("name")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, "Wrong Status code from request")

    def test_create_contact_with_name_blank(self):
        '''
        test contactViewSet create method when name is blank
        '''
        data = self.data
        data["name"]= ""
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, "Wrong Status code from request")

    def test_create_contact_without_message(self):
        '''
        test ContactViewSet create method when message is not in data
        '''
        data = self.data
        data.pop("message")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, "Wrong status code from request")
    
    def test_create_contact_when_message_equals_blank(self):
        '''
        test ContactViewSet create method when message is blank
        '''
        data = self.data
        data["message"] = ""
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_contact_without_email(self):
        '''
        test ContactViewSet create method when email is not in data
        '''
        data = self.data
        data.pop("email")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_create_contact_when_email_equals_blank(self):
        '''
        test ContactViewSet create method when email is blank
        '''
        data = self.data
        data["email"] = ""
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_contact_when_email_equals_non_email(self):
        '''
        test ContactViewSet create method when email is not email
        '''
        data = self.data
        data["email"] = "test"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, "Wrong Statuscode")

    '''
    def test_decode_error(self):
        
        #Testing JsonDecodeError Exception when request is not Json
        
        with self.assertRaises(JSONDecodeError):
            data = self.data
            self.client = Client()
            response = self.client.post(self.url, data, "text/plain")
    '''
