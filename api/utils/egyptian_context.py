"""
Egyptian-specific utilities and constants
"""

EGYPTIAN_GOVERNORATES = [
    'Cairo', 'Giza', 'Alexandria', 'Dakahlia', 'Sharqia',
    'Qalyubia', 'Kafr El Sheikh', 'Gharbia', 'Monufia', 'Beheira',
    'Ismailia', 'Port Said', 'Suez', 'North Sinai', 'South Sinai',
    'Faiyum', 'Beni Suef', 'Minya', 'Asyut', 'Sohag',
    'Qena', 'Luxor', 'Aswan', 'Red Sea', 'New Valley',
    'Matrouh', 'Damietta'
]

EGYPTIAN_HOLIDAYS_2024_2026 = [
    '2024-01-07',  # Coptic Christmas
    '2024-01-25',  # Revolution Day
    '2024-03-11',  # Ramadan Start
    '2024-04-10',  # Eid al-Fitr
    '2024-04-25',  # Sinai Liberation
    '2024-05-01',  # Labor Day
    '2024-06-17',  # Eid al-Adha
    '2024-06-30',  # June 30 Revolution
    '2024-07-23',  # July Revolution
    '2024-10-06',  # Armed Forces Day
    '2025-01-07',
    '2025-01-25',
    '2025-03-01',
    '2025-03-30',
    '2025-06-06',
]

def is_egyptian_phone(phone: str) -> bool:
    """Validate Egyptian phone number format"""
    import re
    pattern = r'^\+20 1[012][0-9] [0-9]{3} [0-9]{4}$'
    return bool(re.match(pattern, phone))

def format_currency_egp(amount: float) -> str:
    """Format amount as Egyptian Pounds"""
    return f"{amount:,.2f} EGP"

def get_governorate_region(governorate: str) -> str:
    """Get region for a governorate"""
    upper_egypt = ['Minya', 'Asyut', 'Sohag', 'Qena', 'Luxor', 'Aswan']
    lower_egypt = ['Cairo', 'Giza', 'Alexandria', 'Qalyubia', 'Dakahlia', 'Sharqia']
    
    if governorate in upper_egypt:
        return 'Upper Egypt'
    elif governorate in lower_egypt:
        return 'Lower Egypt'
    else:
        return 'Other'
