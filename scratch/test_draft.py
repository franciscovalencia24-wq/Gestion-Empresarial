from src.stonex_onboarding.draft_manager import save_draft, load_draft

# Test data
step_test = 2
data_test = {"nombre_completo": "Test User", "rut": "123456-7"}

print("Saving draft...")
token = save_draft(step_test, data_test)
print(f"Token generated: {token}")

print("Loading draft...")
loaded_step, loaded_data = load_draft(token)
print(f"Loaded step: {loaded_step}")
print(f"Loaded data: {loaded_data}")

assert loaded_step == step_test
assert loaded_data["nombre_completo"] == "Test User"
print("Success!")
