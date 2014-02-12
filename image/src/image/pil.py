
__all__ = ['Image', 'ImageQt']

try:
    import Image, ImageQt
except ImportError:
    try:
        from PIL import Image, ImageQt
    except ImportError:
        raise ImportError, "PIL not found. Please install PIL or pillow"

