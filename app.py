import pandas as pd
import requests
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

def get_categories():
    response = requests.get(f"{API_BASE_URL}/categories")
    return response.json()

def get_recipes(cuisine: str = None, difficulty: str = None):
    params = {}
    if cuisine:
        params['cuisine'] = cuisine
    if difficulty:
        params['difficulty'] = difficulty

    response = requests.get(f"{API_BASE_URL}/recipes")
    return response.json()

def create_recipe(name, description, ingredients, instructions, cuisine, difficulty,
                  category_id):
    response = requests.post(f"{API_BASE_URL}/recipes/", json={
        "name": name,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions,
        "cuisine": cuisine,
        "difficulty": difficulty,
        "category_id": category_id
    })
    return response.json()


def update_recipe(recipe_id, recipe_name, description, ingredients, instructions, cuisine, difficulty, category_id):
    """
    Sends a request to update an existing recipe.

    Returns:
        dict: The response from the API, typically containing the updated recipe details.
    """
    response = requests.put(f"{API_BASE_URL}/recipes/{recipe_id}", json={
        "name": recipe_name,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions,
        "cuisine": cuisine,
        "difficulty": difficulty,
        "category_id": category_id
    })
    return response.json()

def delete_recipe(recipe_id):
    """
    Sends a request to delete an existing recipe.

    Returns:
        dict: The response from the API confirming the deletion of the recipe.
    """
    response = requests.delete(f"{API_BASE_URL}/recipes/{recipe_id}")
    return response.json()


st.title("Online Recipe Book")

menu = ["Dashboard", "Manage Recipes", "Manage Categories"]
selected_menu = st.sidebar.selectbox("Menu", menu)

if selected_menu == "Dashboard":
    st.header("Dashboard")

    st.subheader("Recipes")
    recipe_list = get_recipes()
    if recipe_list:
        df_recipes = pd.DataFrame(recipe_list)

        if 'id' in df_recipes.columns:
            df_recipes = df_recipes.drop(columns=['id'])

        df_recipes.reset_index(drop=True, inplace=True)
        df_recipes.index += 1
        st.dataframe(df_recipes)


    st.subheader("Categories")
    category_list = get_categories()

    if category_list:
        df_categories = pd.DataFrame(category_list)

        if 'id' in df_categories.columns:
            df_categories = df_categories.drop(columns=['id'])

        df_categories.reset_index(drop=True, inplace=True)
        df_categories.index += 1
        st.dataframe(df_categories)
    else:
        st.info("No categories found!")

elif selected_menu == "Manage Recipes":
    st.header("Manage Recipes")

    st.subheader("Add a new Recipe")
    recipe_name = st.text_input("Recipe Name")
    recipe_desc = st.text_area("Description")
    recipe_ingredients = st.text_area("Ingredients")
    recipe_instructions = st.text_area("Instructions")
    recipe_cuisine = st.text_input("Cuisine")
    recipe_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    category_list = get_categories()
    if category_list:
        category_names = [cat["name"] for cat in category_list]
        selected_category_name = st.selectbox("Category", category_names)
        selected_category_id = next(cat['id'] for cat in category_list if cat['name'] == selected_category_name)
    else:
        st.error("Failed to retrieve categories")
        selected_category_id = None

    if st.button("Add Recipe", key="add_recipe_button"):
        if all([recipe_name, recipe_ingredients, recipe_instructions, recipe_cuisine,
                recipe_difficulty, selected_category_id is not None]):
            create_recipe(recipe_name, recipe_desc, recipe_ingredients, recipe_instructions,
                          recipe_cuisine, recipe_difficulty, selected_category_id)
            st.success(f"Recipe {recipe_name} added successfully!")
        else:
            st.error("All fields must be filled!")

    st.subheader("Update or Delete a Recipe")
    recipe_list = get_recipes()
    if recipe_list:
        recipe_names = [recipe['name'] for recipe in recipe_list]
        manage_action = st.radio("Choose action", ["Edit", "Delete"], key="manage_recipe_action")

        if manage_action == "Edit":
            recipe_to_edit = st.selectbox("Select a recipe to edit", recipe_names, key="edit_recipe_select")
            if recipe_to_edit:
                selected_recipe = next(recipe for recipe in recipe_list if recipe['name'] == recipe_to_edit)
                st.subheader(f"Edit Recipe: {selected_recipe['name']}")
                edit_name = st.text_input("Recipe Name", value=selected_recipe['name'], key="edit_recipe_name")
                edit_description = st.text_area("Description", value=selected_recipe['description'],
                                                key="edit_recipe_description")
                edit_ingredients = st.text_area("Ingredients", value=selected_recipe['ingredients'],
                                                key="edit_recipe_ingredients")
                edit_instructions = st.text_area("Instructions", value=selected_recipe['instructions'],
                                                 key="edit_recipe_instructions")
                edit_cuisine = st.text_input("Cuisine", value=selected_recipe['cuisine'], key="edit_recipe_cuisine")
                edit_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"],
                                               index=["Easy", "Medium", "Hard"].index(selected_recipe['difficulty']),
                                               key="edit_recipe_difficulty")

                category_list = get_categories()
                if category_list:
                    category_names = [cat['name'] for cat in category_list]
                    edit_category_name = st.selectbox("Category", category_names, index=category_names.index(
                        next(cat['name'] for cat in category_list if cat['id'] == selected_recipe['category_id'])),
                                                      key="edit_recipe_category")
                    edit_category_id = next(cat['id'] for cat in category_list if cat['name'] == edit_category_name)
                else:
                    st.error("Failed to retrieve categories.")
                    edit_category_id = None

                if st.button("Update Recipe", key="update_recipe_button"):
                    if all([edit_name, edit_ingredients, edit_instructions, edit_cuisine, edit_difficulty,
                            edit_category_id is not None]):
                        update_recipe(selected_recipe['id'], edit_name, edit_description, edit_ingredients,
                                      edit_instructions, edit_cuisine, edit_difficulty, edit_category_id)
                        st.success(f"Recipe '{edit_name}' updated successfully!")
                    else:
                        st.error("All fields must be filled and category selected to update a recipe.")

        elif manage_action == "Delete":
            recipe_to_delete = st.selectbox("Select a recipe to delete", recipe_names, key="delete_recipe_select")
            if recipe_to_delete:
                selected_recipe = next(recipe for recipe in recipe_list if recipe['name'] == recipe_to_delete)
                if st.button(f"Delete {selected_recipe['name']}", key="delete_recipe_button"):
                    delete_recipe(selected_recipe['id'])
                    st.success(f"Recipe '{selected_recipe['name']}' deleted successfully!")
        else:
            st.info("No recipes available to manage.")