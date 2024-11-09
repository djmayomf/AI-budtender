from marshmallow import Schema, fields, validates, ValidationError
import re

class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    name = fields.Str(required=True)
    phone = fields.Str()

    @validates('password')
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain lowercase letter')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError('Password must contain special character')
