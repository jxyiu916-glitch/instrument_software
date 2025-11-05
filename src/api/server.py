from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from src.app.core import process_records


class Record(BaseModel):
    value: str | None = None


app = FastAPI(title="Interview API")


@app.post("/process")
def process(records: List[Record]):
    # Convert pydantic models to dicts compatible with process_records
    # Pydantic v2: prefer model_dump() over dict()
    dicts = [r.model_dump() for r in records]
    counts = process_records(dicts)
    return counts
