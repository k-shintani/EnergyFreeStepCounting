import numpy as np
import csv
import time
import matplotlib.pyplot as plt
import bisect
from collections import deque
from scipy import interpolate
from scipy.signal import find_peaks

total_steps_buf = []

def synchronize_data(left_file, right_file):
    left_data = []
    right_data = []
    
    with open(left_file, 'r') as left_csv:
        left_reader = csv.reader(left_csv)
        for row in left_reader:
            left_data.append([float(row[0]), int(row[1]), int(row[2])])
    
    with open(right_file, 'r') as right_csv:
        right_reader = csv.reader(right_csv)
        for row in right_reader:
            right_data.append([float(row[0]), int(row[1]), int(row[2])])
    
    left_timestamps = np.array([row[0] for row in left_data])
    right_timestamps = np.array([row[0] for row in right_data])
    
    right_interp_func1 = interpolate.interp1d(right_timestamps, [row[1] for row in right_data], fill_value="extrapolate")
    right_interp_func2 = interpolate.interp1d(right_timestamps, [row[2] for row in right_data], fill_value="extrapolate")
    
    right_interpolated = [[t, int(right_interp_func1(t)), int(right_interp_func2(t))] for t in left_timestamps]
    
    return left_data, right_interpolated

def process_steps(peaks_left, peaks_right, timestamps):
    final_steps = []
    last_step_time = -float('inf')
    min_step_interval = 0.2  # Minimum time interval between steps
    
    sorted_peaks = sorted([(timestamps[p], 'L') for p in peaks_left] + [(timestamps[p], 'R') for p in peaks_right])
    
    last_step = None
    for time, foot in sorted_peaks:
        if time - last_step_time < min_step_interval:
            continue  # Skip steps that are too close
        
        if last_step is None:
            final_steps.append((time, foot))
        else:
            last_time, last_foot = last_step
            if foot == last_foot:
                intermediate_time = (last_time + time) / 2
                final_steps.append((intermediate_time, 'L' if last_foot == 'R' else 'R'))
        
        final_steps.append((time, foot))
        last_step = (time, foot)
        last_step_time = time
    
    return final_steps

def merge_realtime(left_file, right_file, buffer_size=100, output_file="realtime_output.csv"):
    left_data, right_data = synchronize_data(left_file, right_file)
    buffer = deque(maxlen=buffer_size)
    total_steps = 0
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Time", "Left_Center", "Left_Outside", "Right_Center", "Right_Outside", "Total Steps"])
        
        for left_row, right_row in zip(left_data, right_data):
            buffer.append([left_row[0], left_row[1], left_row[2], right_row[1], right_row[2]])
            merged_data = list(buffer)
            
            processed_steps = process_realtime(merged_data)
            
            time.sleep(0.05)

prev_total = None
def process_realtime(data):
    time_vals = [x[0] for x in data]
    left_center = [x[1] for x in data]
    right_center = [x[3] for x in data]
    
    if len(time_vals) < 5:
        return None  # Not enough data to process
    
    method = interpolate.interp1d
    fitted_left = method(time_vals, left_center, fill_value='extrapolate')
    fitted_right = method(time_vals, right_center, fill_value='extrapolate')
    
    x_latent = np.linspace(min(time_vals), max(time_vals), len(time_vals))
    tmp_left = fitted_left(x_latent)
    tmp_right = fitted_right(x_latent)
    
    peaks_left, _ = find_peaks(-tmp_left, prominence=8, distance=20)
    peaks_right, _ = find_peaks(-tmp_right, prominence=8, distance=20)
    
    min_step_interval = 0.2  # Minimum time interval between steps
    final_steps = process_steps(peaks_left, peaks_right, x_latent)
    for t, foot in final_steps:
        idx = bisect.bisect_left(total_steps_buf, t)
        if len(total_steps_buf) == 0: 
            total_steps_buf.insert(idx, t)
            continue
        if len(total_steps_buf) != idx and abs(total_steps_buf[idx] - t) < min_step_interval:
            continue
        elif idx != 0 and abs(total_steps_buf[idx-1] - t) < min_step_interval:
            continue
        total_steps_buf.insert(idx, t)
    global prev_total
    if prev_total is None or prev_total != len(total_steps_buf):
        if prev_total is not None and len(total_steps_buf) - prev_total == 2:
            print(f"Complemented one missing step")
        print(f"Total Steps Updated: {len(total_steps_buf)}")
    prev_total = len(total_steps_buf)
    

    plt.clf()
    plt.plot(x_latent, tmp_left, label="Left", color='red')
    plt.plot(x_latent, tmp_right, label="Right", color='blue')
    
    for t, f in final_steps:
        idx = bisect.bisect_left(x_latent, t)
        if f == 'L':
            plt.scatter(x_latent[idx], tmp_left[idx], color='red', marker='x', label="Left Steps" if 'Left Steps' not in plt.gca().get_legend_handles_labels()[1] else "")
        else:
            plt.scatter(x_latent[idx], tmp_right[idx], color='blue', marker='x', label="Right Steps" if 'Right Steps' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    plt.legend(loc='upper left')
    plt.xlabel("Time")
    plt.ylabel("Sensor Readings")
    plt.title("Step Detection")
    plt.pause(0.001)
    
    return final_steps

if __name__ == "__main__":
    plt.ion()
    merge_realtime("left.csv", "right.csv", buffer_size=100)
