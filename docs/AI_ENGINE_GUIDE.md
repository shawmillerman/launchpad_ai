# AI Engine Implementation Guide

## Overview
The AI Engine is the foundational module for the Launchpad AI project. It provides core functionality for recipe management, reformulation, and interactive cooking guidance.

## Core Components

### 1. **Ingredient Class**
Represents a single ingredient in a recipe.

```python
ingredient = Ingredient(name="flour", amount="2", unit="cups")
print(ingredient)  # Output: 2 cups of flour
```

**Attributes:**
- `name`: Name of the ingredient
- `amount`: Quantity
- `unit`: Unit of measurement

### 2. **CookingStep Class**
Represents a single step in the cooking process.

```python
step = CookingStep(
    step_number=1,
    instruction="Boil water",
    duration_minutes=5,
    temperature="212F",
    alerts=["Watch for boiling over"]
)
```

**Attributes:**
- `step_number`: Step sequence
- `instruction`: Cooking instruction
- `duration_minutes`: Time to complete (optional)
- `temperature`: Temperature requirement (optional)
- `alerts`: Safety and timing alerts

### 3. **Recipe Class**
Manages a complete recipe with ingredients and cooking steps.

```python
recipe = Recipe("Spaghetti Carbonara", servings=4)
recipe.add_ingredient(Ingredient("spaghetti", "1", "lb"))
recipe.add_step(CookingStep(1, "Boil water"))

# Convert to JSON
json_output = recipe.to_json()
```

**Methods:**
- `add_ingredient(ingredient)`: Add an ingredient
- `add_step(step)`: Add a cooking step
- `to_dict()`: Convert to dictionary
- `to_json()`: Convert to JSON string

### 4. **RecipeReformulator Class**
Reformulates recipes with different formats and flavor profiles.

```python
reformulated = RecipeReformulator.reformulate(recipe, RecipeFormat.SIMPLIFIED)
enhanced = RecipeReformulator.enhance_flavor(recipe, "spicy")
```

**Supported Formats:**
- `STANDARD`: Standard recipe format
- `SIMPLIFIED`: Easy version with fewer steps
- `GOURMET`: Advanced version with professional techniques

**Flavor Enhancements:**
- `spicy`: Add chili and heat
- `umami`: Add depth and savory notes
- `herbaceous`: Add fresh herbs and aromatics

### 5. **CookingGuidance Class**
Provides interactive step-by-step cooking guidance.

```python
session = CookingGuidance(recipe)
current_step = session.get_current_step()
alerts = session.get_alerts_for_step()
progress = session.get_progress()
session.move_to_next_step()
```

**Methods:**
- `get_current_step()`: Get current cooking step
- `move_to_next_step()`: Advance to next step
- `get_alerts_for_step()`: Get alerts for current step
- `get_progress()`: Get cooking progress percentage

### 6. **AIEngine Class**
Main engine coordinating all AI functionality.

```python
engine = AIEngine()
recipe = engine.create_recipe("Pasta", 4)
recipe.add_ingredient(Ingredient("pasta", "1", "lb"))
recipe.add_step(CookingStep(1, "Boil water"))

# Reformulate
simplified = engine.reformulate_recipe("Pasta", RecipeFormat.SIMPLIFIED)

# Start cooking session
session = engine.start_cooking_session("Pasta")
```

**Methods:**
- `create_recipe(title, servings)`: Create a new recipe
- `get_recipe(title)`: Retrieve a recipe
- `reformulate_recipe(title, format)`: Reformulate a recipe
- `enhance_recipe_flavor(title, enhancement)`: Enhance flavor profile
- `start_cooking_session(title)`: Start interactive cooking session

## Usage Examples

### Creating and Running a Complete Recipe

```python
from src.ai_engine import AIEngine, Ingredient, CookingStep, RecipeFormat

# Initialize engine
engine = AIEngine()

# Create recipe
recipe = engine.create_recipe("Chocolate Chip Cookies", 24)

# Add ingredients
recipe.add_ingredient(Ingredient("flour", "2.25", "cups"))
recipe.add_ingredient(Ingredient("butter", "1", "cup"))
recipe.add_ingredient(Ingredient("sugar", "0.75", "cup"))
recipe.add_ingredient(Ingredient("eggs", "2", "count"))
recipe.add_ingredient(Ingredient("vanilla extract", "1", "tsp"))
recipe.add_ingredient(Ingredient("baking soda", "1", "tsp"))
recipe.add_ingredient(Ingredient("salt", "1", "tsp"))
recipe.add_ingredient(Ingredient("chocolate chips", "2", "cups"))

# Add cooking steps
recipe.add_step(CookingStep(1, "Preheat oven to 375F", temperature="375F"))
recipe.add_step(CookingStep(2, "Cream butter and sugar", duration_minutes=3))
recipe.add_step(CookingStep(3, "Beat in eggs and vanilla", duration_minutes=2))
recipe.add_step(CookingStep(4, "Mix in dry ingredients", duration_minutes=1))
recipe.add_step(CookingStep(5, "Fold in chocolate chips", duration_minutes=1))
recipe.add_step(CookingStep(
    6, 
    "Bake for 9-11 minutes", 
    duration_minutes=10,
    temperature="375F",
    alerts=["Watch for golden brown edges"]
))

# Display recipe
print(recipe.to_json())

# Simplify recipe
simplified = engine.reformulate_recipe("Chocolate Chip Cookies", RecipeFormat.SIMPLIFIED)
print(f"Simplified difficulty: {simplified.difficulty}")

# Start cooking session
session = engine.start_cooking_session("Chocolate Chip Cookies")
print(f"Progress: {session.get_progress()}")
```

## Testing

All components are fully tested with 24 unit tests covering:
- Ingredient creation and representation
- Cooking step management
- Recipe composition and serialization
- Recipe reformulation
- Cooking guidance and progress tracking
- Engine functionality

To run tests:
```bash
python3 -m unittest tests.test_ai_engine -v
```

## Future Enhancements

1. **Image Recognition**: OCR and ML models for recipe image processing
2. **Natural Language Processing**: Parse recipe text and convert to structured format
3. **Nutritional Information**: Calculate calories, macros, and allergenic ingredients
4. **User Preferences**: Dietary restrictions and cooking skill levels
5. **Real-time Alerts**: Timer integration and notifications
6. **Cloud Storage**: Store and sync recipes across devices
7. **Social Features**: Share recipes and cooking sessions with others
