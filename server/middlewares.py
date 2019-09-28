import zlib


def compresion_middleware(func):
    def wrapper(request, *args, **kwargs):
        b_request = zlib.decompressobj().decompress(request)
        b_response = func(b_request, *args, **kwargs)
        return zlib.compress(b_response)
    return wrapper
