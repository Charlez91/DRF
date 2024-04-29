from .customer_serializers import CustomUserSerializer
from .contact_serializers import ContactSerializer
from .comment_serializers import CommentSerializer
from .customer_serializers import (
        CustomerSerializer,
        CustomerRegisterSerializer, 
        CustomerUpdateSerializer,
)
from .employee_serializers import (
        EmployeeSerializer,
        EmployeeRegisterSerializer,
        EmployeeUpdateSerializer,
)

__all__ = (
    "CustomUserSerializer",
    "ContactSerializer",
    "CommentSerializer",
    "CustomerSerializer",
    "CustomerRegisterSerializer",
    "CustomerUpdateSerializer",
    "EmployeeSerializer",
    "EmployeeRegisterSerializer",
    "EmployeeUpdateSerializer",
)