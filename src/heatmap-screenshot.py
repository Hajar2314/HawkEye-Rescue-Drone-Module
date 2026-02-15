import time
import board
import busio
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt
import os

# Initialize I2C communication
i2c = busio.I2C(board.SCL, board.SDA)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ  # Set to a feasible refresh rate

# Create figure for live plotting
plt.ion()
fig, ax = plt.subplots(figsize=(12, 7))
therm1 = ax.imshow(np.zeros((24, 32)), vmin=0, vmax=60)
cbar = fig.colorbar(therm1)
cbar.set_label('Temperature [$^{\circ}$C]', fontsize=14)

# Create a folder to save images if it doesn't exist
if not os.path.exists("heatmap_images"):
    os.makedirs("heatmap_images")

frame = np.zeros((24*32,))
t_array = []
max_retries = 5
photo_counter = 0  # Counter for saving photos

while True:
    t1 = time.monotonic()
    retry_count = 0
    while retry_count < max_retries:
        try:
            mlx.getFrame(frame)  # Get the thermal data
            data_array = np.reshape(frame, (24, 32))  # Reshape the data into a 24x32 array
            therm1.set_data(np.fliplr(data_array))  # Flip data to match orientation
            therm1.set_clim(vmin=np.min(data_array), vmax=np.max(data_array))  # Set color limits
            fig.canvas.draw()  # Redraw the figure to update the plot and colorbar
            fig.canvas.flush_events()
            plt.pause(0.001)

            # Save the current heatmap as an image
            photo_counter += 1
            photo_filename = f"heatmap_images/heatmap_{photo_counter:04d}.png"
            plt.savefig(photo_filename)  # Save the current figure as a PNG file
            print(f"Saved heatmap to {photo_filename}")

            # Record frame rate stats
            t_array.append(time.monotonic() - t1)
            print(f'Sample Rate: {len(t_array)/np.sum(t_array):.1f} fps')

            break
        except ValueError:
            retry_count += 1
        except RuntimeError as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Failed after {max_retries} retries with error: {e}")
                break
