from django.conf import settings


class UnknownLabImageKey(ValueError):
    pass


def normalize_image_key(image_key: str) -> str:
    return (image_key or "").strip().lower()


def resolve_lab_image(image_key: str) -> str:
    normalized_key = normalize_image_key(image_key)
    image_map = getattr(settings, "LAB_DOCKER_IMAGE_MAP", {})
    resolved_image = image_map.get(normalized_key)
    if not resolved_image:
        raise UnknownLabImageKey(f"Unknown docker image key: {image_key}")
    return resolved_image
