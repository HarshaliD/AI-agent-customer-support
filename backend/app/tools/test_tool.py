from order_tools import get_order

print("Tool name:", get_order.name)
print("Tool description:", get_order.description)

print("Tool schema:", get_order.args_schema)
print("Schema JSON:", get_order.args_schema.model_json_schema())