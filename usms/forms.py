"""Tiny helpers for reading plain HTML form fields."""
from datetime import date


class FormError(ValueError):
    pass


def required(form, name, label=None):
    value = (form.get(name) or "").strip()
    if not value:
        raise FormError(f"{label or name.replace('_', ' ').capitalize()} is required.")
    return value


def optional(form, name):
    value = (form.get(name) or "").strip()
    return value or None


def parse_date(form, name, label=None, required_=True):
    raw = (form.get(name) or "").strip()
    if not raw:
        if required_:
            raise FormError(f"{label or name.replace('_', ' ').capitalize()} is required.")
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise FormError(f"{label or name} must be a valid date.")
