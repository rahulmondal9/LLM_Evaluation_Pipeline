import json
import os
from pathlib import Path

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# --- DATA DEFINITIONS ---

# 1. Chat 01 (The Hallucination Test Case)
chat_01 = {
  "chat_id": 78128,
  "user_id": 77096,
  "conversation_turns": [
    {
      "turn": 1,
      "sender_id": 1,
      "role": "AI/Chatbot",
      "message": "I know what you're going through. Let's talk. I'm here to support you for all your infertility and IVF needs. Please tell me what's on your mind.",
      "created_at": "2025-11-16T17:04:44.000000Z"
    },
    {
      "turn": 5,
      "sender_id": 77096,
      "role": "User",
      "message": "I and my wife are planning to come to India early next month. I am still trying to convince her that since I started with communicating with you eversince, I may be a good idea to come to you in an attempt to solve our infertility problems.",
      "created_at": "2025-11-16T17:06:58.000000Z"
    },
    {
      "turn": 6,
      "sender_id": 1,
      "role": "AI/Chatbot",
      "message": "It's wonderful to hear you are planning to come to India and are considering the Malpani Infertility Clinic to address your infertility problems. We have significant experience with patients coming from overseas, and we strive to make the process as smooth as possible. We can coordinate preliminary tests in your hometown to minimize your time in Mumbai, often requiring only 10 to 20 days at our clinic for an entire IVF cycle. What specific infertility challenges have you both been diagnosed with so far? [](https://www.drmalpani.com/knowledge-center/articles/how-ivf-works-your-complete-guide)",
      "created_at": "2025-11-16T17:07:10.000000Z"
    },
    {
      "turn": 13,
      "sender_id": 77096,
      "role": "User",
      "message": "Do you have an idea how much thier rooms cost per night?",
      "created_at": "2025-11-16T20:42:07.000000Z"
    },
    {
      "turn": 14,
      "sender_id": 1,
      "role": "AI/Chatbot",
      "message": "For Gopal Mansion, an air-conditioned room with TV and bath is Rs 800 per night. We also offer specially subsidized air-conditioned rooms at our clinic for Rs 2000 (US $50) per night, and non-AC rooms for Rs 1500 (US$ 40) per night, including free breakfast. Happy Home Hotel, which is a 5-minute walk from our clinic, offers single rooms for Rs 1400 and double rooms for Rs 2000. To discuss your specific needs and coordinate your visit, you can [book a consultation call](https://pages.razorpay.com/ivfconsultation) with Dr. Malpani.",
      "created_at": "2025-11-16T20:42:16.000000Z",
      "evaluation_note": "Hallucination/Factual Error: The bolded section regarding 'subsidized rooms at our clinic' is explicitly noted as incorrect in the review data."
    }
  ]
}

# 2. Context 01 (The Source of Truth)
context_01 = {
    "status": "success",
    "data": {
        "vector_data": [
            {
                "id": 28960,
                "text": "Hotels Near Malpani Infertility Clinic... Happy Home Hotel... Room Charges 1400/- Single Room 2000/- Double Room. This is a 5 min walk away from the clinic...",
                "source_url": "https://www.drmalpani.com/hotels"
            },
            {
                "id": 27025,
                "text": "Your best choice would be Gopal Mansion... An airconditioned room with TV and bath is only Rs 800 per night...",
                "source_url": "https://www.drmalpani.com/hotels"
            },
            {
                "id": 36699,
                "text": "Most successful IVF centre in Mumbai, India... Patients are able to get treatment that is at par with the rest of the world, but at less than half of the cost in western countries.",
                "source_url": "https://www.drmalpani.com/knowledge-center/articles/most-successful-ivf-centre-in-mumbai-india"
            }
        ]
    }
}

# 3. Chat 02 (Medical Advice)
chat_02 = {
  "chat_id": 53911,
  "user_id": 52599,
  "conversation_turns": [
    {
      "turn": 4,
      "sender_id": 52599,
      "role": "User",
      "message": "My amh 0.68 afc 4 age 34+.doctor advised for donor egg. Should I go with donor egg or self egg",
      "created_at": "2025-05-22T06:00:25.000000Z"
    },
    {
      "turn": 5,
      "sender_id": 1,
      "role": "AI/Chatbot",
      "message": "I understand your situation... We have seen that fresh eggs have slightly higher success rates but are more expensive, while frozen eggs offer more flexibility and lower costs...",
      "created_at": "2025-05-22T06:00:35.000000Z"
    },
    {
        "turn": 16,
        "sender_id": 52599,
        "role": "User",
        "message": "In my case donor option is have better chance.?",
        "created_at": "2025-05-22T06:09:52.000000Z"
    },
    {
        "turn": 17,
        "sender_id": 1,
        "role": "AI/Chatbot",
        "message": "Given your low AMH (0.68) and AFC (4), along with your age, the donor egg option typically offers significantly higher success rates compared to using your own eggs. Our frozen egg bank guarantees mature, high-quality eggs which bypasses the issue of your own ovarian reserve.",
        "created_at": "2025-05-22T06:10:05.000000Z"
    }
  ]
}

# 4. Context 02 (Donor Egg Info)
context_02 = {
    "status": "success",
    "data": {
        "vector_data": [
            {
                "id": 38511,
                "text": "Donor Egg IVF... In case it is found that the quality of the woman’s egg is poor or if the woman doesn’t have any eggs at all, it’s possible for the couple to use donor eggs... Our pregnancy rates with frozen eggs from our egg bank are as good as with fresh eggs...",
                "source_url": "https://www.drmalpani.com/knowledge-center/articles/donor-egg-ivf"
            },
            {
                "id": 37437,
                "text": "Low amh patient fresh or frozen... Frozen eggs offer more flexibility in timing and lower costs but may have slightly lower success rates.",
                "source_url": "https://www.drmalpani.com/knowledge-center/articles/low-amh"
            },
            {
                "id": 36684,
                "text": "How does a low AMH level affect IVF success rates? A low AMH level indicates poor ovarian reserve, which can lower the chances of success with IVF.",
                "source_url": "" 
            }
        ]
    }
}

# --- WRITE FILES ---

def write_json(filename, data):
    filepath = data_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Created normalized file: {filepath}")

if __name__ == "__main__":
    print("Normalizing and generating data files...")
    write_json("sample-chat-conversation-01.json", chat_01)
    write_json("sample_context_vectors-01.json", context_01)
    write_json("sample-chat-conversation-02.json", chat_02)
    write_json("sample_context_vectors-02.json", context_02)