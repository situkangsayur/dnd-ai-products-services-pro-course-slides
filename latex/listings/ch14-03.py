zip_path = keras.utils.get_file(
    origin="https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz",
    fname="imdb",
    extract=True,
)
imdb_extract_dir = pathlib.Path(zip_path) / "aclImdb"

for path in imdb_extract_dir.glob("*/*"):
    if path.is_dir():
        print(path)
