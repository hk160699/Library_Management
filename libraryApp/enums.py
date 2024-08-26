from enum import Enum
from django.db import models

class Role(Enum):
    USER = 'user'
    LIBRARIAN = 'librarian'

    @classmethod
    def choices(cls):
    #    breakpoint()
    #    import pdb;pdb.set_trace()
       return [(key.value, key.name.capitalize()) for key in cls]

class BorrowedStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.capitalize()) for key in cls]   

class PaymentStatus(Enum):
    UNPAID = 'unpaid'
    PAID = 'paid'
    DISCARD = 'discard'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.capitalize()) for key in cls]
