from marshmallow import Schema, fields, validates, ValidationError
from typing import Dict, Any
import re

class DealSchema(Schema):
    title = fields.Str(required=True)
    dispensary = fields.Str(required=True)
    location = fields.Str(required=True)
    original_price = fields.Float(required=True)
    discounted_price = fields.Float(required=True)
    image_url = fields.Url(allow_none=True)
    
    @validates('original_price')
    def validate_original_price(self, value: float):
        if value <= 0:
            raise ValidationError('Original price must be greater than 0')

    @validates('discounted_price')
    def validate_discounted_price(self, value: float):
        if value <= 0:
            raise ValidationError('Discounted price must be greater than 0')

class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    name = fields.Str()
    role = fields.Str()
    
    @validates('password')
    def validate_password(self, value: str):
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', value):
            raise ValidationError('Password must contain at least one number') 