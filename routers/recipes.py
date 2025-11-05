from fastapi import APIRouter, HTTPException
from typing import List
from models.recipe import Recipe, RecipeCreate
from database import get_db_connection

# Create an APIRouter instance for recipe-related routes
router = APIRouter()


def category_exists(category_id: int) -> bool:
    """
    Check if a category with the given ID exists in the database.

    Returns:
        bool: True if the category exists, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM categories WHERE id = ?", (category_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


@router.get("/recipes/", response_model=List[Recipe])
def get_recipes(cuisine: str = None, difficulty: str = None):
    """
    Retrieve recipes from the database with optional filters for cuisine and difficulty.

    Returns:
        List[Recipe]: A list of Recipe objects matching the specified filters.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM recipes WHERE 1=1"
    params = []

    if cuisine:
        query += " AND cuisine = ?"
        params.append(cuisine)
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)

    cursor.execute(query, params)
    recipes = cursor.fetchall()
    conn.close()

    return [Recipe(id=row[0], name=row[1], description=row[2], ingredients=row[3],
                   instructions=row[4], cuisine=row[5], difficulty=row[6],
                   category_id=row[7]) for row in recipes]


@router.post("/recipes/", response_model=Recipe)
def create_recipe(recipe: RecipeCreate):
    """
    Create a new recipe in the database.

    Returns:
        Recipe: The created Recipe object with its generated ID.

    Raises:
        HTTPException: 400 Bad Request if the specified category does not exist.
    """
    if not category_exists(recipe.category_id):
        raise HTTPException(status_code=400, detail="Category does not exist")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recipes (name, description, ingredients, instructions, cuisine, difficulty, category_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (recipe.name, recipe.description, recipe.ingredients, recipe.instructions,
         recipe.cuisine, recipe.difficulty, recipe.category_id))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()

    return Recipe(id=recipe_id, name=recipe.name, description=recipe.description,
                  ingredients=recipe.ingredients, instructions=recipe.instructions,
                  cuisine=recipe.cuisine, difficulty=recipe.difficulty, category_id=recipe.category_id)


@router.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, recipe: RecipeCreate):
    """
    Update an existing recipe in the database.

    Returns:
        Recipe: The updated Recipe object.

    Raises:
        HTTPException: 400 Bad Request if the specified category does not exist.
        HTTPException: 404 Not Found if the recipe ID does not exist.
    """
    if not category_exists(recipe.category_id):
        raise HTTPException(status_code=400, detail="Category does not exist")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE recipes SET name = ?, description = ?, ingredients = ?, instructions = ?, cuisine = ?, difficulty = ?, category_id = ? WHERE id = ?",
        (recipe.name, recipe.description, recipe.ingredients, recipe.instructions,
         recipe.cuisine, recipe.difficulty, recipe.category_id, recipe_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    conn.commit()
    conn.close()

    return Recipe(id=recipe_id, name=recipe.name, description=recipe.description,
                  ingredients=recipe.ingredients, instructions=recipe.instructions,
                  cuisine=recipe.cuisine, difficulty=recipe.difficulty, category_id=recipe.category_id)


@router.delete("/recipes/{recipe_id}", response_model=dict)
def delete_recipe(recipe_id: int):
    """
    Delete a recipe from the database by ID.

    Returns:
        dict: A dictionary with a detail message indicating the recipe has been deleted.

    Raises:
        HTTPException: 404 Not Found if the recipe ID does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    conn.commit()
    conn.close()

    return {"detail": "Recipe deleted"}