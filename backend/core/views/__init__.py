from .auth_views import EmailVerificationView, ActivateView
from .comment_views import CommentViewset
from .contact_views import ContactAPIView
from .customer_views import (
    CustomerListView, CustomerRegisterAPIView, 
    CustomerRetrieveView, CustomerUpdateAPIView
)
from .employee_views import EmployeerAPIView


__all__ = (
    "EmailVerificationView",
    "ActivateView",
    "CommentViewset",
    "ContactAPIView",
    "CustomerListView",
    "CustomerRegisterAPIView",
    "CustomerRetrieveView",
    "CustomerUpdateAPIView",
    "EmployeerAPIView",
)
