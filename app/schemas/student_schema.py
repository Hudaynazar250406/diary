from marshmallow import Schema, fields, validate


class StudentSchema(Schema):
    id = fields.Integer(dump_only=True)
    full_name = fields.String(required=True, validate=validate.Length(min=1))
    group_id = fields.Integer(required=True, validate=validate.Range(min=1))
    email = fields.Email(required=False, load_default=None, allow_none=True)
