import time
import mss
import bettercam

def capture_screenshots(n: int = 10):
    """Captures n screenshots and measures the performance."""

    TOP = 0
    LEFT = 0
    RIGHT = 1600
    BOTTOM = 900
    region = (LEFT, TOP, RIGHT, BOTTOM)
    title = "[BetterCam] FPS benchmark"
    start_time = time.perf_counter()


    fps = 0
    camera = bettercam.create(max_buffer_len=2)

    camera.start(region=region, target_fps=60)
    start = time.perf_counter()
    while fps < 500:
        frame = camera.get_latest_frame()
        if frame is not None:
            fps += 1

    end_time = time.perf_counter() - start

    print(f"{title}: {fps/end_time}")
    camera.release()

    with mss.mss() as sct:
        monitor = {
            "top": 0,
            "left": 0,
            "width": 1600,
            "height": 900
        }
        
        times = []
        for _ in range(n):
            start_time = time.time()
            sct.grab(monitor)
            end_time = time.time()
            
            times.append(end_time - start_time)
        
    return times

def main():
    num_screenshots = 1000  # Number of screenshots to capture
    times = capture_screenshots(num_screenshots)
    
    total_time = sum(times)
    avg_time = total_time / num_screenshots
    max_time = max(times)
    min_time = min(times)
    
    print(f"Total time for {num_screenshots} screenshots: {total_time:.4f} seconds")
    print(f"Average time per screenshot: {avg_time:.6f} seconds")
    print(f"Fastest capture time: {min_time:.6f} seconds")
    print(f"Slowest capture time: {max_time:.6f} seconds")

if __name__ == "__main__":
    main()
