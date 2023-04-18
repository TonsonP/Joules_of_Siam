def calculate_electricity_charge(monthly_usage, ft_rate):
    # Define the base tariff rates in Baht/kWh
    tariff_0_15 = 2.3483
    tariff_16_25 = 2.9882
    tariff_26_35 = 3.2405
    tariff_36_100 = 3.6237
    tariff_101_150 = 3.7171
    tariff_151_400 = 4.2218
    tariff_above_400 = 4.4217

    # Define the tax rate as a fraction
    tax_rate = 0.07
    
    # monthly_usage = int(monthly_usage)
    # ft_rate = int(ft_rate)

    # Calculate the base tariff charge
    if monthly_usage <= 15:
        base_tariff = monthly_usage * tariff_0_15
    elif monthly_usage <= 25:
        base_tariff = 15 * tariff_0_15 + (monthly_usage - 15) * tariff_16_25
    elif monthly_usage <= 35:
        base_tariff = 15 * tariff_0_15 + 10 * tariff_16_25 + (monthly_usage - 25) * tariff_26_35
    elif monthly_usage <= 100:
        base_tariff = 15 * tariff_0_15 + 10 * tariff_16_25 + 10 * tariff_26_35 + (monthly_usage - 35) * tariff_36_100
    elif monthly_usage <= 150:
        base_tariff = 15 * tariff_0_15 + 10 * tariff_16_25 + 10 * tariff_26_35 + 65 * tariff_36_100 + (monthly_usage - 100) * tariff_101_150
    elif monthly_usage <= 400:
        base_tariff = 15 * tariff_0_15 + 10 * tariff_16_25 + 10 * tariff_26_35 + 65 * tariff_36_100 + 50 * tariff_101_150 + (monthly_usage - 150) * tariff_151_400
    else:
        base_tariff = 15 * tariff_0_15 + 10 * tariff_16_25 + 10 * tariff_26_35 + 65 * tariff_36_100 + 50 * tariff_101_150 + 250 * tariff_151_400 + (monthly_usage - 400) * tariff_above_400

    service_charge = 8.19
    base_tariff = base_tariff + service_charge

    # Calculate the Ft charge
    ft_charge = monthly_usage * ft_rate
    
    # Calculate the tax
    tax = (base_tariff + ft_charge) * tax_rate
    
    # Calculate the total bill
    total_bill = base_tariff + ft_charge + tax
    
    return total_bill

if __name__ == '__main__':
    total_bill = calculate_electricity_charge(1000,2)
    print(total_bill)