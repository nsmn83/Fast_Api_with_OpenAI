from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

#   class that contains types of requested information in the first method (/generate-dish-propositions/)
class DishRequest(BaseModel):
    num_propositions: int = Query(..., title="Number of Dish Propositions", description="Enter the number of dish propositions you want.")
    ingredients: str = Query(..., title="Ingredients", description="Comma-separated list of ingredients.")

#   class that takes from the user index of prevoiously generated dish
class DishInstructionsRequest(BaseModel):
    selected_dish_index: int = Query(..., title="Selected Dish Index", description="Index of the selected dish from the generated propositions.")

# API key to connect to gpt-3.5-turbo
openai = OpenAI(api_key="PUT_YOUR_API_KEY_HERE")


# variable to containt generated propositions
generated_propositions = []

# variable to containt used ingredients
ingredients = ""

# method that generates dish propositions and stores them in global variable generated_propositions
# ingredients are stored in global variable named ingredients
@app.post("/generate-dish-propositions/")
async def generate_dish_propositions(request: DishRequest):

    global ingredients
    ingredients = request.ingredients
    messages = [
        {"role": "system", "content": "You are someone who gives dishes propositions."},
        {"role": "user", "content": f"Give me {request.num_propositions} dish propositions - only their names, that contain: {request.ingredients}."},
    ]

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )

    global generated_propositions
    generated_propositions = [{"name": name.strip()} for name in response.choices[0].message.content.split("\n")]
    return {"generated_propositions": generated_propositions}

# in this method we ask user to give us index of prevoiusly generated meal, and we give him ingredients and instruciotn how to do said meal
@app.post("/generate-dish-instructions/")
async def generate_dish_instructions(request: DishInstructionsRequest):
    selected_dish_index = request.selected_dish_index

    if not (0 <= selected_dish_index < len(generated_propositions)):
        raise HTTPException(status_code=400, detail="Invalid selected dish index.")

    selected_dish = generated_propositions[selected_dish_index-1]["name"]

    messages = [
        {"role": "system", "content": "You are someone who gives cooking instructions."},
        {"role": "user", "content": f"Give me instructions for {selected_dish} that contain {ingredients}. Put *** between list of ingredients and recipe"},
    ]

    response2 = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )

    return {"generated_instruction": response2.choices[0].message.content}