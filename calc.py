import pandas as pd
import numpy as np
import sys

def calc_efficiency(f):
   df = pd.read_csv(f)

   # Get instant power readings
   power_w = df[['time', 'HV EV Battery Power (kW)']][ pd.notna(df['HV EV Battery Power (kW)'])]
   power_w['time'] = pd.to_datetime(power_w['time'])
   power_w = power_w.to_numpy().T
   power_w[1] *= 1000

   # Integrate over time
   diff = power_w[0, 1:] - power_w[0, : -1]
   helper = np.vectorize(lambda x: x.total_seconds())
   diff = np.vstack((helper(diff), power_w[1, :-1])).astype(np.float64)
   # Adjust for 95% charging efficiency
   diff[1] *= (np.ones_like(diff[1]) - (diff[1] < 0) * 0.05)
   energy_used_wh = diff[0] * diff[1] / 3600
   energy_used_wh = energy_used_wh.cumsum()

   # Get distance reading
   dist = df[['time', 'Distance travelled (miles)']][pd.notna(df['Distance travelled (miles)'])]
   dist['time'] = pd.to_datetime(dist['time'])
   dist = dist.to_numpy().T

   # Calculate trip efficiency
   energy_wh_mi = energy_used_wh[-1] / dist[1, -1]
   print(f"{f} :\nDistance travelled: {round(dist[1, -1], 3)} mi\nEnergy efficiency: {round(energy_wh_mi, 3)} wh/mi\n")

if __name__ == "__main__":
   if len(sys.argv) == 1:
      print('Usage: python calc.py <log file 0>, <log file 1>, ...')
      exit(1)

   for f in sys.argv[1:]:
      calc_efficiency(f)

