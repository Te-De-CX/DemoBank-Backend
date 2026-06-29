def calculate_emi(principal, annual_rate, months):
    monthly_rate = (annual_rate / 100) / 12
    if monthly_rate == 0:
        return round(principal / months, 2)
    emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    return round(emi, 2)

def calculate_total_payable(emi, months):
    return round(emi * months, 2)