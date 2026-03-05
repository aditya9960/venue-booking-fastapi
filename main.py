from fastapi import FastAPI, HTTPException
from src.api.v1.routes import router, booking_db

app = FastAPI(title="Venue Booking Service")

app.include_router(router)

