from database import db

# Get all FAQs
async def get_faqs():
    cursor = db.faq.find()
    return await cursor.to_list(length=None)

# Add a new FAQ
async def add_faq(question, answer):
    await db.faq.insert_one({
        "question": question,
        "answer": answer
    })
