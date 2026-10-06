from app.services.ingestion import ingest_directory


if __name__ == "__main__":
    result = ingest_directory("data/documents")
    print(result)
