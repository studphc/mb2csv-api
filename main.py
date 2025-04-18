from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import io, base64
from mb2csv import mb2df     # ← 기존 파서

app = FastAPI()

@app.post("/mb2csv")
async def convert(file: bytes):
    """
    Body: 바이너리 (.MB)  ※ Content-Type: application/octet-stream
    Return: text/csv
    """
    df = mb2df(io.BytesIO(file))
    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode()
    return StreamingResponse(io.BytesIO(csv_bytes),
                             media_type="text/csv",
                             headers={"Content-Disposition":
                                      "attachment; filename=output.csv"})
