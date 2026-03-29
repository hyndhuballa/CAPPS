"""
services/user_service.py
Handles all user-related logic:
  - Calculating age from DOB
  - Assigning age category/mode
  - Building a UserCategory object for downstream use
"""

from datetime import date
from models.models import UserInput, UserCategory


def calculate_age(dob: date) -> int:
    """
    Calculates the current age in full years from a date of birth.
    
    Args:
        dob: Date of birth as a date object.
    
    Returns:
        Integer age in years.
    """
    today = date.today()
    age = today.year - dob.year
    # Subtract 1 if birthday hasn't occurred yet this year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return age


def get_user_category(user: UserInput) -> UserCategory:
    """
    Classifies a user into one of three modes based on their age.

    Age rules:
      ≤ 18  → "kid"     (strict safety filtering)
      19–59 → "adult"   (standard recommendations)
      ≥ 60  → "elderly" (comfort-focused, familiar brands)

    Args:
        user: A UserInput object with DOB and region info.

    Returns:
        UserCategory with age, mode, region, and preferences populated.
    
    Raises:
        ValueError: If DOB is in the future.
    """
    age = calculate_age(user.dob)

    if age < 0:
        raise ValueError(f"Invalid DOB {user.dob}: results in negative age.")

    if age <= 18:
        mode = "kid"
    elif age <= 59:
        mode = "adult"
    else:
        mode = "elderly"

    return UserCategory(
        user_id=user.user_id,
        age=age,
        mode=mode,
        region=user.region,
        preferences=user.preferences,
    )
