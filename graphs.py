import numpy as np
import matplotlib.pyplot as plt

# Vin–Vout data from your sheet
vin  = [0.0,0.2,0.4,0.6,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.2,3.4,3.6,3.8,4.0,4.5,5.0,5.5,6.0]
vout = [5.990,5.9901,5.9899,5.9899,5.9898,5.9894,5.9873,5.9784,5.9419,5.9419,5.8006,5.3333,4.0501,1.36557,0.096970,0.049729,0.034715,0.027385,0.023128,0.020417,0.018525,0.017136,0.016071,0.015225,0.014551,0.014001,0.013553,0.012891,0.012444,0.012130,0.011901,0.011727,0.011428,0.011237,0.011107,0.011010]

plt.figure(figsize=(6,4))
plt.plot(vin, vout, marker='o')
plt.xlabel("Vin (V)")
plt.ylabel("Vout (V)")
plt.title("Input–Output Characteristic (Vin vs Vout)")
plt.grid(True)
plt.tight_layout()
plt.savefig("vin_vout_curve.png", dpi=200)
plt.show()
