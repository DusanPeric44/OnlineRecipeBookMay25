import sqlite3

from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT

from database import get_db_connection
from models.category import Category, CategoryCreate
from typing import List
router = APIRouter()

# Ruta da vrati sve kategorije
@router.get('/categories/', response_model=List[Category])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    conn.close()

    category_list = [
        {
            "id": category[0],
            "name": category[1]
        }
        for category in categories
    ]
    return category_list

@router.post('/categories/', response_model=Category)
def create_category(category: CategoryCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category.name,))
        conn.commit()
        category_id = cursor.lastrowid
        return Category(id=category_id, name=category.name)
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"The category with name {category.name} already exists."
        )
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}"
        )
    finally:
        conn.close()

@router.put("/categories/{category_id}", response_model=Category)
def update_category(category_id: int, category: CategoryCreate):
    """
    Update the name of an existing category.

    This endpoint updates the name of a category identified by its ID. If the
    category ID does not exist, it raises a 404 error.

    Returns:
        Category: The updated Category object.

    Raises:
        HTTPException: 404 Not Found if the category ID does not exist.
    """
    # Establish a database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    # Execute SQL query to update the category name
    cursor.execute("UPDATE categories SET name = ? WHERE id = ?", (category.name, category_id))
    if cursor.rowcount == 0:
        # Handle case where the category ID does not exist
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found")
    conn.commit()
    conn.close()
    return Category(id=category_id, name=category.name)


# Route to delete a category by ID
@router.delete("/categories/{category_id}", response_model=dict)
def delete_category(category_id: int):
    """
    Delete a category from the database by ID.

    This endpoint deletes a category identified by its ID. If the category ID does
    not exist, it raises a 404 error.

    Returns:
        dict: A dictionary with a detail message indicating the category has been deleted.

    Raises:
        HTTPException: 404 Not Found if the category ID does not exist.
    """
    # Establish a database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    # Execute SQL query to delete the category
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    if cursor.rowcount == 0:
        # Handle case where the category ID does not exist
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found")
    conn.commit()
    conn.close()
    return {"detail": "Category deleted"}