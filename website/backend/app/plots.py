import io
import matplotlib.pyplot as plt

def generate_forecast(sorted_data):
    months_sorted, meanC_sorted, highC_sorted, lowC_sorted = zip(*sorted_data)

    plt.figure(figsize=(10, 6))
    plt.plot(months_sorted, meanC_sorted, marker='o', linestyle='-', label='Mean Temperature', color='skyblue', linewidth=2)
    plt.plot(months_sorted, highC_sorted, marker='o', linestyle='--', label='High Temperature', color='orange', linewidth=2)
    plt.plot(months_sorted, lowC_sorted, marker='o', linestyle=':', label='Low Temperature', color='purple', linewidth=2)
    plt.xlabel('Month')
    plt.ylabel('Temperature (Celsius)')
    plt.title('Monthly Temperatures')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    temperature_chart = io.BytesIO()
    plt.savefig(temperature_chart, format='png')
    temperature_chart.seek(0)
    plt.close()
    
    return temperature_chart

def generate_precipitation(sorted_data):
    months_sorted, precipDays_sorted, precipMm_sorted = zip(*sorted_data)

    fig, ax1 = plt.subplots(figsize=(10, 6))
    plt.title('Monthly Precipitation')

    ax1.bar(months_sorted, precipDays_sorted, color='skyblue', alpha=0.7, label='Precipitation Days')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Precipitation Days', color='skyblue')
    ax1.tick_params(axis='y', labelcolor='skyblue')

    ax2 = ax1.twinx()
    ax2.plot(months_sorted, precipMm_sorted, color='purple', marker='o', label='Precipitation (mm)')
    ax2.set_ylabel('Precipitation (mm)', color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')

    fig.tight_layout()

    precipitation_chart = io.BytesIO()
    plt.savefig(precipitation_chart, format='png')
    precipitation_chart.seek(0)
    plt.close()
    
    return precipitation_chart
