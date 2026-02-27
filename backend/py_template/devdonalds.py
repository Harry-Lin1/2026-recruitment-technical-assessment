from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int

# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = []

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) 

    name = recipeName.replace('-', ' ')
    name = name.replace('_', ' ')

    clean_name = ""
    for char in name:
        if char.isalpha() or char.isspace():
            clean_name = clean_name + char
    
    words = clean_name.split()

    formatted_words = []
    for word in words:
        capitalized_word = word.capitalize()
        formatted_words.append(capitalized_word)
       
    result = " ".join(formatted_words)
   
    if len(result) > 0:
        return result
    else:
        return None

# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook

@app.route('/entry', methods=['POST'])
def create_entry():
    data = request.get_json()
    
    if data['type'] not in ["recipe", "ingredient"]:
        return "Invalid type", 400

    for entry in cookbook:
        if entry['name'] == data['name']:
            return "Name must be unique", 400

    if data['type'] == "ingredient":
        if data.get('cookTime', 0) < 0:
            return "CookTime must be >= 0", 400

    if data['type'] == "recipe":
        seen_names = set()
        for item in data.get('requiredItems', []):
            if item['name'] in seen_names:
                return "Duplicate required items", 400
            seen_names.add(item['name'])

    cookbook.append(data)
    return "", 200

# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name

@app.route('/summary', methods=['GET'])
def summary():
    target_name = request.args.get('name')
   
    root_recipe = None
    for entry in cookbook:
        if entry['name'] == target_name:
            root_recipe = entry
            break

    if root_recipe is None:
        return "Recipe not found", 400

    if root_recipe.get('type') != 'recipe':
        return "Target item is an ingredient, not a recipe", 400

    # recursive section
    ingredient_counts = {}
    total_cook_time = 0

    def find_ingredients_recursive(item_name, multiplier):
        nonlocal total_cook_time
       
        # find items in cookbook
        item_details = None
        for entry in cookbook:
            if entry['name'] == item_name:
                item_details = entry
                break
       
        if item_details is None:
            raise ValueError("Missing component")

        # case 1: base ingredient 
        if item_details['type'] == 'ingredient':
            # Add 
            total_cook_time += item_details.get('cookTime', 0) * multiplier
            ingredient_counts[item_name] = ingredient_counts.get(item_name, 0) + multiplier
       
        # case 2: another recipe 
        else:
            required_items = item_details.get('requiredItems', [])
            for sub_item in required_items:
                new_multiplier = multiplier * sub_item['quantity']
                find_ingredients_recursive(sub_item['name'], new_multiplier)

    # search inside root recipe
    try:
        for item in root_recipe.get('requiredItems', []):
            find_ingredients_recursive(item['name'], item['quantity'])
    except ValueError:
        return "Recipe contains items not in cookbook", 400

    final_ingredients_list = [
        {"name": name, "quantity": qty}
        for name, qty in ingredient_counts.items()
    ]

    return jsonify({
        "name": target_name,
        "cookTime": total_cook_time,
        "ingredients": final_ingredients_list
    }), 200
# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
