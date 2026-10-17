"""
viz_phone_pipeline_bilingual.py

Билингвальная визуализация конвейера: Датчик → Fog → Курьер → Телефон.
Bilingual visualization of the pipeline: Sensor → Fog → Courier → Phone.
"""
import random, statistics
import matplotlib.pyplot as plt

PIPELINE_RU = "Датчик → Fog → Курьер → Телефон"
PIPELINE_EN = "Sensor → Fog → Courier → Phone"

def simulate(n_tasks=30, seed=7):
    random.seed(seed)
    # Processing times (ms) per stage / Времена обработки (мс) на каждом этапе:
    sensor  = [random.randint(20, 60) for _ in range(n_tasks)]   # Sensor / Датчик
    
    # === НАСТРОЙКА ДЛЯ СИНЕЙ КРИВОЙ ===
    fog     = [random.randint(30, 80) for _ in range(n_tasks)]   # Fog node / Fog‑узел
    
    # === НАСТРОЙКА ДЛЯ КРАСНОЙ КРИВОЙ ===
    fog2    = [random.randint(10, 40) for _ in range(n_tasks)]   # Оптимизированный Fog-узел
    
    courier = [random.randint(10, 40) for _ in range(n_tasks)]   # Courier / Курьер

    # Расчет сквозной задержки для синей кривой
    latencies = [s + f + c for s, f, c in zip(sensor, fog, courier)]
    
    # Расчет сквозной задержки для красной кривой
    latencies2 = [s + f + c for s, f, c in zip(sensor, fog2, courier)]

    # Phone buffer: phone "reads" messages every read_interval_ms
    read_interval_ms = 120
    time = 0
    buffer_sizes = []
    buf = 0
    for L in latencies:
        time += L
        reads = time // read_interval_ms
        for _ in range(int(reads)):
            if buf > 0:
                buf -= 1
        buf += 1
        buffer_sizes.append(buf)

    # === РАСЧЕТ МЕТРИК ДЛЯ СИНЕЙ КРИВОЙ ===
    avg_latency = statistics.mean(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]  # ~95-й перцентиль

    # === РАСЧЕТ МЕТРИК ДЛЯ КРАСНОЙ КРИВОЙ ===
    avg_latency2 = statistics.mean(latencies2)
    p95_2 = statistics.quantiles(latencies2, n=20)[18]  # ~95-й перцентиль для красной кривой

    return latencies, buffer_sizes, avg_latency, p95, latencies2, avg_latency2, p95_2

def plot(latencies, buffer_sizes, latencies2):
    # Plot 1: end‑to‑end latency (RU/EN)
    plt.figure(figsize=(8, 4.5))
    x = range(1, len(latencies)+1)
    
    # Исходная синяя кривая (зависит от fog)
    plt.plot(x, latencies, marker='o', label='Исходная задержка (Синяя)')
    
    # Добавленная красная кривая (зависит от fog2)
    plt.plot(x, latencies2, color='red', marker='o', label='Оптимизированная задержка (Красная)') 
    
    plt.title(f"Сквозная задержка {PIPELINE_RU}\nEnd-to-End Latency {PIPELINE_EN}")
    plt.xlabel("Номер задачи / Task #")
    plt.ylabel("Задержка, мс / Latency, ms")
    plt.legend() # Добавляем легенду на график
    
    # Пояснение прямо на графике:
    plt.text(0.02, 0.92,
             "Путь задержки / Latency path:\nДатчик→Fog→Курьер→Телефон\nSensor→Fog→Courier→Phone",
             transform=plt.gca().transAxes, fontsize=9, va='top')
    plt.tight_layout()
    plt.show()

    # Plot 2: phone buffer over arrivals (RU/EN)
    plt.figure(figsize=(8, 4.5))
    plt.plot(range(1, len(buffer_sizes)+1), buffer_sizes, marker='s')
    plt.title("Буфер телефона по задачам / Phone Buffer Size over Tasks")
    plt.xlabel("Порядок прибытия задач / Arrival order (Task #)")
    plt.ylabel("Сообщений в буфере / Messages in buffer")
    plt.tight_layout()
    plt.show()

def main():
    # Принимаем новые метрики из функции симуляции
    latencies, buffer_sizes, avg_latency, p95, latencies2, avg_latency2, p95_2 = simulate() 

    # ИЗМЕНЕННЫЙ ВЫВОД В КОНСОЛЬ
    print("=== Метрики (RU) ===")
    print(f"Конвейер: {PIPELINE_RU}")
    print("-" * 40)
    print("СИНЯЯ КРИВАЯ (Исходный туман):")
    print(f"  Средняя сквозная задержка (мс): {avg_latency:.2f}")
    print(f"  ~95-й перцентиль задержки (мс): {p95:.2f}")
    print("-" * 40)
    print("КРАСНАЯ КРИВАЯ (Оптимизированный туман):")
    print(f"  Средняя сквозная задержка (мс): {avg_latency2:.2f}")
    print(f"  ~95-й перцентиль задержки (мс): {p95_2:.2f}")
    print("-" * 40)

    # Передаем данные в функцию построения графиков
    plot(latencies, buffer_sizes, latencies2) 

if __name__ == '__main__':
    main()
