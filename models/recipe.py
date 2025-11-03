from typing import Optional

from pydantic import BaseModel

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None,
    ingredients: str
    instructions: str
    cuisine: str
    difficulty: str
    category_id: Optional[int] = None

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int