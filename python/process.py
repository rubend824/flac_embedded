from python.classes.flac_processor import FLACImageReprocessor
base = '/Volumes/Untitled/'
flac_processor = FLACImageReprocessor(base, replace_images=False)
flac_processor.run()
for f in flac_processor.failed:
    print(f"Failed files: {f}")