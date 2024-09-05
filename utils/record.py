from picamera import PiCamera
from time import time, sleep
from datetime import datetime
import traceback
import os
import argparse
import logging
import sys

HOME_DIR = os.path.expanduser("~")
DEFAULT_OUTPUT_DIR = os.path.join(HOME_DIR, ".recordings")

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", help="output directory", default=DEFAULT_OUTPUT_DIR)
parser.add_argument("-f", "--format", help="encoder format", choices=['h264', 'rgb', 'rgba', 'mjpeg'], default='h264')
parser.add_argument("--frame-rate", help="camera frame rate", type=int, default=30)
parser.add_argument("-r", "--resolution", help="camera resolution --relosution width height", type=int, nargs=2, default=(1280,720))
parser.add_argument("-d", "--duration", help="recording duration in seconds", type=float, default=60.0)
parser.add_argument("--prefix", help="add a prefix to all recording file names eg. --prefix drone_1 drone_1_<timestamp>", default=None)
parser.add_argument("--max-size", help="max recording file size in megabytes", type=int, default=100)
parser.add_argument("-v", "--verbose", help="verbose print", action="store_true")

def setup_logger(level):
    # create logger
    logger = logging.getLogger("recorder")
    
    # set log level
    logger.setLevel(level)
    
    # set handler to stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # set formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # set stream handler
    logger.addHandler(handler)
    
    return logger
    
    

def main():
    # parse args
    args = parser.parse_args()

    # setup logger
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(log_level)
    
    
    # create output directory
    try:
        os.mkdir(args.output)
    except FileExistsError:
        pass
    except Exception:
        traceback.print_exc()
        
    # recoring file name
    output_file_name = f"{args.prefix}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.{args.format}" if args.prefix is not None else f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.{args.format}"
    logger.debug(f"output filename {output_file_name}")
    output_path = os.path.join(args.output, output_file_name)
    logger.debug(f"output path {output_path}")
    
    # create camera
    resolution = tuple(args.resolution)
    logger.debug(f"recording resolution {resolution}")
    camera = PiCamera(resolution=resolution, framerate=args.frame_rate)

    camera.start_recording(output_path)

    start_time = time()
    current_time = time()
    max_size_bytes = args.max_size * 1024 * 1024
    while (current_time - start_time < args.duration and os.path.getsize(output_path) < max_size_bytes):
        logger.debug(os.path.getsize(output_path))
        
        # check for camera exceptions
        try:
            camera.wait_recording()
            sleep(0.1)

            # update current time
            current_time = time()
            
            logger.debug(f"duration: {current_time - start_time}")

        except KeyboardInterrupt:
            logger.info("stopping recording")
            camera.stop_recording()
            exit()
        except Exception as e:
            traceback.print_exc()
            
    logger.info(f"recording complete\n\
                \tpath: {output_path}\n\
                \tsize: {round(os.path.getsize(output_path) / (1024 * 1024), 2)}Mb\n\
                \tduration: {round(current_time - start_time, 2)} seconds")
        

        
if __name__ == "__main__":
    main()