print("Please input the num of oils by the type of float:")
galons = float(input())
kg = galons * 3.785412
towers = galons / 19.5
cabd = galons * 20.0
acol = galons * 115000.0 / 75700.0
price = galons * 3.0
print("Numbers of kg are %.3f" %kg)
print("towers of oils are %.3f" %towers)
print("Get out %.3f CO2" %cabd)
print("The energy is the same to %.3f acol" %acol)
print("Cost %.3f dollars" %price)