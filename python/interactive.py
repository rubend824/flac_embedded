import os
from python.classes.flac_processor import FLACImageReprocessor

def request_data():
    path = None
    while not path:
        print('Input a valid path (search will be recursive)')
        path = input()
        path = path if os.path.exists(path) else None
    print('Files type to search (default: *.flac): ')
    search_string = input()
    search_string = search_string if bool(search_string) else '*.flac'

    print('Save as JPEG progressive (1) or baseline (0)? (default: 0 for walkman compatibility): ')
    progressive = input()
    progressive = True if progressive == '1' else False

    print('Image quality (values: 1-100; default: 100): ')
    quality_string = input()
    try:
        quality = int(quality_string)
        quality = quality if 0 <= quality <= 100 else 100
    except:
        quality = 100

    return path, search_string, progressive, quality


if __name__ == '__main__':
    path, search_string, progressive, quality = request_data()
    print("Files will be processed with the following characteristics:")
    print(f"Base path: {path}")
    print(f"Search string: {search_string}")
    print(f"Progressive or baseline: {'progressive' if progressive else 'baseline'}")
    print(f"Image quality: {quality}")
    processor = FLACImageReprocessor(
        base_path=path,
        file_search_string=search_string,
        progressive=progressive,
        quality=quality
    )
    processor.run()

