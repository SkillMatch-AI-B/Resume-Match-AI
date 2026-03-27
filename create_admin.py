import core.auth as auth

print("Injecting Master Admin Account...")

# Uses the exact same secure hashing we use for normal users
success = auth.register_user("boss@gmail.com", "admin123", "Admin") 

if success:
    print("✅ Admin account created successfully! You can now log in.")
else:
    print("⚠️ Admin account already exists in the database.")