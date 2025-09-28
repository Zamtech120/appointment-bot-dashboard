from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

app = FastAPI()

# ---------- Models ----------
class SlotRequest(BaseModel):
    date_from: str
    date_to: str

class SlotResponse(BaseModel):
    slots: List[str]

# ---------- Dummy logic ----------
def fetch_busy_between(start: str, end: str):
    # Example: block 1–2 PM every day
    return [(f"{start[:10]}T13:00", f"{start[:10]}T14:00")]

def generate_slots(date_from: str, date_to: str):
    start_date = datetime.fromisoformat(date_from)
    end_date = datetime.fromisoformat(date_to)
    slots = []

    while start_date <= end_date:
        for hour in range(9, 18):  # 9 AM - 5 PM
            slot_start = start_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_end = slot_start + timedelta(hours=1)

            busy = fetch_busy_between(date_from, date_to)
            if not any(b[0] <= slot_start.isoformat() < b[1] for b in busy):
                slots.append(slot_start.isoformat())
        start_date += timedelta(days=1)

    return slots

# ---------- API ----------
@app.post("/available-slots", response_model=SlotResponse)
async def available_slots(q: SlotRequest):
    slots = generate_slots(q.date_from, q.date_to)
    return {"slots": slots}

# ---------- Realistic UI ----------
@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Appointment Booking</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body {
          background: #f4f6f9;
        }
        .container {
          max-width: 600px;
          margin-top: 60px;
          background: white;
          padding: 30px;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        h2 {
          color: #333;
          margin-bottom: 20px;
        }
        #slots li {
          background: #e9f7ef;
          border-left: 4px solid #28a745;
          padding: 8px;
          margin-bottom: 6px;
          border-radius: 6px;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h2 class="text-center">Book Your Appointment</h2>
        <form id="slotForm">
          <div class="mb-3">
            <label for="from" class="form-label">From Date</label>
            <input type="date" class="form-control" id="from" required>
          </div>
          <div class="mb-3">
            <label for="to" class="form-label">To Date</label>
            <input type="date" class="form-control" id="to" required>
          </div>
          <button type="submit" class="btn btn-primary w-100">Check Availability</button>
        </form>
        <div class="mt-4">
          <h4>Available Slots</h4>
          <ul id="slots" class="list-unstyled"></ul>
        </div>
      </div>

      <script>
        document.getElementById('slotForm').onsubmit = async (e) => {
          e.preventDefault();
          let from = document.getElementById('from').value;
          let to = document.getElementById('to').value;
          let res = await fetch('/available-slots', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({date_from: from, date_to: to})
          });
          let data = await res.json();
          let ul = document.getElementById('slots');
          ul.innerHTML = "";
          if (data.slots.length === 0) {
            ul.innerHTML = "<li class='text-danger'>No slots available in this range.</li>";
          } else {
            data.slots.forEach(s => {
              let li = document.createElement('li');
              li.textContent = new Date(s).toLocaleString();
              ul.appendChild(li);
            });
          }
        }
      </script>
    </body>
    </html>
    """
