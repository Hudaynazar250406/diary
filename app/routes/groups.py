from flask import Blueprint, request, jsonify

from app.services.group_service import GroupService

groups_bp = Blueprint("groups", __name__, url_prefix="/groups")


@groups_bp.post("")
def create_group():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    group, error = GroupService.create(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(group.to_dict()), 201


@groups_bp.get("")
def list_groups():
    groups = GroupService.list_all()
    return jsonify([g.to_dict() for g in groups]), 200


@groups_bp.get("/<int:group_id>")
def get_group(group_id):
    group = GroupService.get_by_id(group_id)
    if group is None:
        return jsonify({"error": "Group not found"}), 404

    return jsonify(group.to_dict()), 200


@groups_bp.put("/<int:group_id>")
def update_group(group_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    group, error = GroupService.update(group_id, data)
    if error == "Group not found":
        return jsonify({"error": error}), 404
    if error:
        return jsonify({"error": error}), 400

    return jsonify(group.to_dict()), 200


@groups_bp.delete("/<int:group_id>")
def delete_group(group_id):
    success, error = GroupService.delete(group_id)
    if error == "Group not found":
        return jsonify({"error": error}), 404
    if error:
        return jsonify({"error": error}), 400

    return "", 204
