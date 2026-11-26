"""ПР4, завдання 2: крок квантування АЦП і похибка для 12 і 8 біт."""
VREF = 3.3
DIVIDER = 20 / 30            # подільник 10к/20к
AMPS_PER_VOLT = 20 / 5.0     # модель датчика: 0..5 В = 0..20 А
RAW = [32, 865, 1729, 2638, 3551, 4095]   # мої значення з Serial Monitor (Wokwi)

step12, step8 = VREF / 4096, VREF / 256
print(f"крок 12 біт: {step12*1000:.3f} мВ   крок 8 біт: {step8*1000:.2f} мВ\n")
print(f"{'raw':>5} {'V АЦП':>8} {'I, А':>7} {'похибка 12б, А':>15} {'похибка 8б, А':>14}")
for r in RAW:
    v = r / 4095 * VREF
    i = v / DIVIDER * AMPS_PER_VOLT
    e12 = step12 / 2 / DIVIDER * AMPS_PER_VOLT   # макс. похибка квантування = пів кроку
    e8 = step8 / 2 / DIVIDER * AMPS_PER_VOLT
    print(f"{r:5} {v:8.3f} {i:7.2f} {e12:15.4f} {e8:14.3f}")
