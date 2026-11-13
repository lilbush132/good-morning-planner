"""Good Morning Planner: picks a random breakfast and times your coffee cooling."""
from dataclasses import dataclass
from bakery import assert_equal
import numpy as np  # NumPy np.exp() computes e^x, used in Newton's law of cooling.
from drafter import *
import random

ROOM_TEMP = 70.0  # constant avg temp of room

@dataclass
class Breakfast:
    """One menu item: name, price, allergens, calories."""
    breakfast: str
    price: float
    allergy: str
    calories: int


@dataclass
class goodmorning:
    """Website state: user info, coffee settings, and the breakfast menu."""
    coffie: bool
    name: str
    temp: float
    fin_temp: float
    minutes: float
    k: float
    unit: str
    breakfasts: list[Breakfast]  
    selected_breakfast: str

def make_starting_breakfasts():
    """Return the starting menu."""
    return [
        Breakfast("Cereal and milk", 2.00, "Dairy, Gluten", 250),
        Breakfast("Yogurt and fruit", 2.50, "Dairy", 200),
        Breakfast("Banana and peanut butter", 1.50, "Peanuts", 300),
        Breakfast("Bagel and cream cheese", 3.00, "Dairy, Gluten", 350),
        Breakfast("Instant oatmeal", 1.00, "Gluten", 160),
        Breakfast("Toast and peanut butter", 1.25, "Peanuts, Gluten", 280),
        Breakfast("Oatmeal on the stove", 1.50, "Gluten", 300),
        Breakfast("Smoothie", 3.50, "Dairy", 220),
        Breakfast("Avocado toast", 4.00, "Gluten", 320),
        Breakfast("Cheese quesadilla", 2.50, "Dairy, Gluten", 400),
        Breakfast("Fried egg sandwich", 3.00, "Eggs, Gluten", 380),
        Breakfast("Scrambled eggs", 2.00, "Eggs", 220),
        Breakfast("Breakfast burrito", 4.50, "Eggs, Dairy, Gluten", 550),
        Breakfast("Waffles", 2.50, "Eggs, Dairy, Gluten", 350),
        Breakfast("French toast", 3.00, "Eggs, Dairy, Gluten", 400),
        Breakfast("Omelette with veggies", 3.50, "Eggs, Dairy", 300),
        Breakfast("Pancakes", 2.50, "Eggs, Dairy, Gluten", 450),
    ]

def find_breakfast(name: str, items: list[Breakfast]) -> Breakfast:
    """Return the Breakfast matching name (first item if none match)."""
    for item in items:
        if item.breakfast == name:
            return item
    return items[0]

def choice(rando: list[Breakfast]) -> str:
    """Return the name of a random Breakfast."""
    return random.choice(rando).breakfast 

def coffee_temp(start: float, constant: float, minn: float) -> float:
    """Return coffee temp after minn minutes (Newton's law of cooling)."""
    return ROOM_TEMP + (start - ROOM_TEMP) * np.exp(-constant * minn)

@route
def index(state: goodmorning) -> Page:
    """Home page: ask for the user's name."""
    return Page(state, [
        "Good morning! What is your name?",
        TextBox("name", state.name),
        Button("I'm hungry!!!", question_1)
    ])

@route
def question_1(state: goodmorning, name: str) -> Page:
    """Save the name, then ask about coffee."""
    if name.strip() == "":
        state.name = "friend"
    else:
        state.name = name.strip()
    return Page(state, [
        "Do you want coffee?",
        Button("Yes", yes_coffee),
        Button("No", no_coffee)
    ])

@route
def no_coffee(state: goodmorning) -> Page:
    state.coffie = False
    return whoshungry(state)

@route
def yes_coffee(state: goodmorning) -> Page:
    state.coffie = True
    return whoshungry(state)

@route
def whoshungry(state: goodmorning) -> Page:
    """Pick and show a random breakfast with its details."""
    state.selected_breakfast = choice(state.breakfasts)
    item = find_breakfast(state.selected_breakfast, state.breakfasts)
    next_page = coffie_time
    if state.coffie == False:
        next_page = final
    return Page(state, [
        "This is your breakfast:",
        item.breakfast,
        f"Price: ${item.price:.2f}",  # 2f formats a number with 2 decimal places 
        f"Allergens: {item.allergy}",
        f"Calories: {item.calories}",
        Button("reroll", whoshungry),
        Button("next", next_page),
        Button("Add a breakfast", add_page)
    ])

@route
def add_page(state: goodmorning) -> Page:
    """Form for adding a new breakfast."""
    return Page(state, [
        "Add a breakfast to the menu",
        "Name:", TextBox("new_name", ""),
        "Price:", TextBox("new_price", ""),
        "Allergens:", TextBox("new_allergy", ""),
        "Calories:", TextBox("new_calories", ""),
        Button("Add", add_breakfast),
        Button("Back", index)
    ])

@route
def add_breakfast(state: goodmorning, new_name: str, new_price: str,
                  new_allergy: str, new_calories: str) -> Page:
    """Validate the form and add the new Breakfast to the menu."""
    new_name = new_name.strip()
    if new_name == "":
        return Page(state, ["Name can't be empty.", Button("Try again", add_page)])
    for item in state.breakfasts:  # loop over an attribute of the list of Breakfast objects
        if item.breakfast.lower() == new_name.lower():
            return Page(state, ["That breakfast is already on the menu.",
                                Button("Try again", add_page)])
    # try/except catches bad number input so the site doesn't crash.
    # If float() or int() fails, Python jumps to the except block instead of erroring.
    try:
        price = float(new_price)
        calories = int(new_calories)
    except ValueError:
        return Page(state, ["Price and calories must be numbers.",
                            Button("Try again", add_page)])
    state.breakfasts.append(Breakfast(new_name, price, new_allergy.strip(), calories))
    return Page(state, [f"Added {new_name}!", Button("Back to start", index)])

@route
def coffie_time(state: goodmorning) -> Page:
    """Coffee timer page: ask for current and desired temps."""
    return Page(state, [
        "calculate how long before coffie is ready",
        "Current coffee temperature:",
        TextBox("temp", str(state.temp)),
        "Desired Temp:",
        TextBox("fin_temp", str(state.fin_temp)),
        Button("Calculate Time", calculate_result)
    ])

@route
def calculate_result(state: goodmorning, temp: str, fin_temp: str) -> Page:
    """Validate temps, then count minutes until the coffee reaches the target."""
    #  try/except again, so letters in the temperature boxes don't crash the site
    try:
        state.temp = float(temp)
        state.fin_temp = float(fin_temp)
    except ValueError:
        return Page(state, ["Temperatures must be numbers.",
                            Button("Try again", coffie_time)])
    if state.fin_temp <= ROOM_TEMP or state.fin_temp >= state.temp:
        return Page(state, [
            "Desired temp must be above room temp and below the current temp.",
            Button("Try again", coffie_time)
        ])
    minutes = 0
    while coffee_temp(state.temp, state.k, minutes) > state.fin_temp:
        minutes += 1
    state.minutes = float(minutes)
    return Page(state, [
        f"Your coffee starts at {state.temp}°F and you want it at {state.fin_temp}°F.",
        f"It will take about {state.minutes} minutes.",
        Button("next", final2)
    ])

@route
def final(state: goodmorning) -> Page:
    """Final page (no coffee)."""
    return Page(state, [
        f"Enjoy your morning, {state.name}!",
        f"Breakfast: {state.selected_breakfast}",
        Button("Start Over", index)
    ])

@route
def final2(state: goodmorning) -> Page:
    """Final page (with coffee wait time)."""
    return Page(state, [
        f"Enjoy your morning, {state.name}!",
        f"Breakfast: {state.selected_breakfast}",
        f"Coffee is done in {state.minutes} minutes.",
        Button("Start Over", index)
    ])
set_website_title("Good Morning Planner")
set_site_information(
    author="Jon Bush",
    description="Picks a random breakfast and tells you how long until your coffee is drinkable.",
    sources="the Drafter docs and NumPy docs.",
    planning=["plan.pdf"],
    links=["https://github.com/your-username/your-repository"]
)
hide_debug_information()
set_website_framed(False)


start_server(goodmorning(True, "", 180.0, 0.0, 0.0, 0.1, "F", make_starting_breakfasts(), ""))
