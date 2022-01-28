one_time_for_family = input("你是一户一表吗?【y or n】\n")
if one_time_for_family == 'y' or one_time_for_family == "Y":
    step_one = 2.20
elif one_time_for_family == 'n' or one_time_for_family == "N":
    step_one = 2.30
total_for_year = int(input("一年的总用水量是？\n"))
tax_one = 260 * step_one
tax_two = tax_one + 160 * (step_one + 0.66)
tax_three = tax_two + (step_one + 2.86)
tax_final = max(tax_one, tax_two, tax_three)
if 0 <= total_for_year <= 260:
    tax_one = total_for_year * step_one
    tax_final = tax_one
elif 261 <= total_for_year <= 360:
    tax_two = tax_one + (total_for_year - 260) * (step_one + 0.66)
    tax_final = tax_two
elif total_for_year >= 361:
    tax_three = tax_one + tax_two + (total_for_year - 360) * (step_one + 2.86)
    tax_final = tax_three
tax_other = total_for_year * 1.10
tax_total = tax_final + tax_other
print(tax_total)



