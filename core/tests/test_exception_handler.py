from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.test import APIRequestFactory

from core.exceptions.exceptions import ServiceError
from core.exceptions.handlers import custom_exception_handler


def _context():
    return {"request": APIRequestFactory().get("/"), "view": None}


def test_application_error_maps_to_its_own_status_and_code():
    response = custom_exception_handler(ServiceError("Bad input", "VALIDATION_ERROR"), _context())

    assert response.status_code == 400
    assert response.data["success"] is False
    assert response.data["error"]["code"] == "VALIDATION_ERROR"


def test_drf_not_found_maps_to_not_found_code():
    response = custom_exception_handler(NotFound(), _context())

    assert response.status_code == 404
    assert response.data["error"]["code"] == "NOT_FOUND"


def test_drf_permission_denied_maps_to_permission_denied_code():
    response = custom_exception_handler(PermissionDenied(), _context())

    assert response.status_code == 403
    assert response.data["error"]["code"] == "PERMISSION_DENIED"


def test_drf_validation_error_flattens_field_errors():
    response = custom_exception_handler(
        ValidationError({"phone_number": ["Enter a valid phone number."]}), _context()
    )

    assert response.status_code == 400
    assert "phone_number" in response.data["error"]["message"]


def test_unmapped_exception_returns_internal_error_without_leaking_traceback():
    response = custom_exception_handler(RuntimeError("boom"), _context())

    assert response.status_code == 500
    assert response.data["error"]["code"] == "INTERNAL_ERROR"
    assert "boom" not in response.data["error"]["message"]
