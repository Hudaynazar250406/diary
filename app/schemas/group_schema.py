from marshmallow import Schema, fields, validate


class GroupSchema(Schema):
    id = fields.Integer(dump_only=True)
    group_name = fields.String(required=True, validate=validate.Length(min=1))
    year = fields.Integer(required=True, validate=validate.Range(min=1))
