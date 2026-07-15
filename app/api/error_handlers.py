from __future__ import annotations

from http import HTTPStatus

from flask import Flask, jsonify, render_template, request
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.errors import AppError


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        if _is_api_request():
            return (
                jsonify(
                    {
                        "error": {
                            "code": error.code,
                            "message": error.message,
                            "details": error.details,
                        }
                    }
                ),
                error.status_code,
            )
        return _render_page_error(error.status_code)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        return _json_error(
            status_code=400,
            code="validation_error",
            message="Invalid request data",
            details=error.messages,
        )

    @app.errorhandler(422)
    def handle_webargs_validation_error(error):
        details = {}
        if isinstance(error, HTTPException):
            details = _extract_serializable_error_details(
                getattr(error, "data", {}) or {}
            )
        return _json_error(
            status_code=400,
            code="validation_error",
            message="Invalid request data",
            details=details,
        )

    @app.errorhandler(404)
    def handle_not_found(_error):
        if _is_api_request():
            return _json_error(
                status_code=404,
                code="not_found",
                message="Resource not found",
            )
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.exception("Unhandled server error", exc_info=error)
        if _is_api_request():
            return _json_error(
                status_code=500,
                code="internal_error",
                message="Internal server error",
            )
        return render_template("errors/500.html"), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        if not _is_api_request():
            return error

        status_code = error.code or 500
        code_map = {
            400: "validation_error",
            404: "not_found",
            409: "conflict",
        }
        return _json_error(
            status_code=status_code,
            code=code_map.get(status_code, "http_error"),
            message=error.description or HTTPStatus(status_code).phrase,
            details=_extract_serializable_error_details(
                getattr(error, "data", {}) or {}
            ),
        )


def _json_error(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict | None = None,
):
    return (
        jsonify(
            {
                "error": {
                    "code": code,
                    "message": message,
                    "details": details or {},
                }
            }
        ),
        status_code,
    )


def _is_api_request() -> bool:
    return request.path.startswith("/api")


def _render_page_error(status_code: int):
    if status_code == 404:
        return render_template("errors/404.html"), 404
    return render_template("errors/500.html"), status_code


def _extract_serializable_error_details(raw_details: dict) -> dict:
    if "messages" in raw_details:
        return {"messages": raw_details["messages"]}
    return {}
