from flask import Blueprint, request, jsonify

from app.services.student_service import StudentService

students_bp = Blueprint("students", __name__, url_prefix="/students")


@students_bp.post("")
def create_student():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    student, error = StudentService.create(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(student.to_dict()), 201


@students_bp.get("")
def list_students():
    group_id = request.args.get("group_id", type=int)
    students = StudentService.list_all(group_id=group_id)
    return jsonify([s.to_dict() for s in students]), 200


@students_bp.get("/<int:student_id>")
def get_student(student_id):
    student = StudentService.get_by_id(student_id)
    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student.to_dict()), 200
