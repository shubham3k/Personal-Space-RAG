"""Image validation, hashing, and thumbnail helpers."""

from pathlib import Path

from config.settings import settings


def validate_image(path: Path) -> dict:
    from PIL import Image

    with Image.open(path) as image:
        return {"width": image.width, "height": image.height, "format": image.format}


def perceptual_hash(path: Path) -> str:
    try:
        import imagehash
        from PIL import Image

        with Image.open(path) as image:
            return str(imagehash.phash(image))
    except Exception:
        return ""


def create_thumbnail(path: Path, output_dir: str | None = None, size: int | None = None) -> str:
    from PIL import Image

    target_dir = Path(output_dir or settings.thumbnail_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output = target_dir / f"{path.stem}.jpg"
    with Image.open(path) as image:
        image.thumbnail((size or settings.thumbnail_size, size or settings.thumbnail_size))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        image.save(output, "JPEG", quality=85)
    return str(output)
