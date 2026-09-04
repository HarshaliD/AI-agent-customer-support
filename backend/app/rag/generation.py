from backend.app.services.chat_service import model


def generate_answer(prompt):
    response = model.invoke(prompt)

    return response.text