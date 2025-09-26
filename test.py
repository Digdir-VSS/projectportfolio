import json
from utils.model_table import create_table_class
from utils.connect_engine import add_row, engine
with open("tables/new_table_id.json", "r") as file:
    columns = json.load(file)

User = create_table_class("new_table_id", columns)

print(User.schema())


new_user = User(age=30, name="You")
saved = add_row(new_user)
print("Inserted:", saved)