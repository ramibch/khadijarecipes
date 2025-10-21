### **Recipe Breaking Issues**
- **Coral Chips (Recipe 9)** - Using powdered sugar instead of sepia ink/food coloring (WRONG INGREDIENT)
- **Turkish Pita Bread** - Missing "black cumin" ingredient (mentioned in steps)
- **Strudel Dough** - Missing "butter/margarine" ingredient
- **Duplicate ingredients** - Same ingredient appearing multiple times in one recipe

### **Data Loading**
- **Load order must be**: Units → Ingredients → Recipes → Steps
- **Test loading** - Load small batches first to catch errors early

## 💡 **IMPROVEMENT SUGGESTIONS** (Fix When Possible)

### **Content Quality**
- **Image paths** - Add actual image URLs instead of null values
- **Category accuracy** - Review if "snack" vs "appetizer" assignments make sense
- **Language coverage** - Fill missing Spanish/Italian translations

### **User Experience**
- **Prep times** - Verify 24-hour recipes are correctly labeled as "hard" difficulty
- **Alternative ingredients** - Mark clearly which ingredients are optional/substitutes
- **Quantity formatting** - Use whole numbers where possible (170 instead of 170.00)

### **Quick Checks**
```bash
# Run these before loading:
python manage.py shell
from recipes.models import Unit, Ingredient
print("Duplicate units:", Unit.objects.values('name_de').annotate(count=Count('id')).filter(count__gt=1))
print("Duplicate ingredients:", Ingredient.objects.values('name_de').annotate(count=Count('id')).filter(count__gt=1))
```

**Priority**: Fix the 4 recipe-breaking issues first, then handle database constraints.


**Alternative ingredient**
