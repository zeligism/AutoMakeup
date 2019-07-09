
import time
import requests
import os

# The file where image_urls will be exported to
DATASET_DIR = "raw"
IMAGE_URLS = "image_urls.csv"

# Get absolute path of this file and force relative-to-file paths
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
DATASET_DIR = os.path.join(FILE_DIR, DATASET_DIR)
IMAGE_URLS = os.path.join(FILE_DIR, IMAGE_URLS)

# Create dataset directory if it doesn't exist
if not os.path.isdir(DATASET_DIR): os.mkdir(DATASET_DIR)

TRY_AGAIN = False  # retry previously failed requests
ERROR_TAG = b"(error)"
IMAGE_HAS_ERROR = lambda f: f.read()[:len(ERROR_TAG)] == ERROR_TAG

def download_image(image_url, image_path="untitled"):

    # Download image in chunks
    try:
        with requests.get(image_url, stream=True, timeout=30) as image_response:
            image_response.raise_for_status()
            with open(image_path, 'wb') as f:
                chunk_size = 1 << 10
                for chunk in image_response.iter_content(chunk_size):
                    f.write(chunk)
            return "Success"
    except Exception as e:
        # Image will be text describing the error message
        with open(image_path, 'w') as f:
            f.write("(error) {}".format(e))
        return e


def download_images(image_urls, dataset_dir=DATASET_DIR):

    # Download images
    for index, image_url in enumerate(image_urls):

        # Create image name and path
        image_name = "{:05d}".format(index)
        image_path = os.path.join(dataset_dir, image_name)

        # If a file called 'image_name' already exists, open it and find whether
        # it has an '(error)' tag in it. If it doesn't, then we already downloaded
        # it successfully, so we skip it. If it does, then we skip it only if we
        # don't want to try downloading it again.
        if os.path.exists(image_path):
            with open(image_path, "rb") as image:
                if not IMAGE_HAS_ERROR(image):
                    continue  # skip because we already downloaded this image
                if not TRY_AGAIN:
                    continue  # skip because we don't want to try again

        # Download image and check download success
        print("[{:05d}]  Downloading {} ... ".format(index, image_url), end="")
        status = download_image(image_url, image_path)

        # Add image url to dataset metadata (can add more metadata later)
        print(status)


def delete_error_images(num_image_urls, dataset_dir=DATASET_DIR):
    
    # Create image name and path
    index = 0
    num_errors = 0
    image_name = "{:05d}".format(index)
    image_path = os.path.join(dataset_dir, image_name)

    while index < num_image_urls:
        if os.path.exists(image_path):
            # Delete image if it has an error
            with open(image_path, "rb") as image:
                if IMAGE_HAS_ERROR(image):
                    print("Removing %s" % image_name)
                    num_errors+=1
                    os.remove(image_path)
        # Next image
        index += 1
        image_name = "{:05d}".format(index)
        image_path = os.path.join(dataset_dir, image_name)

    print(num_errors)


def main():

    start_time = time.time()

    # Download images
    with open(IMAGE_URLS, "r") as image_urls:
        download_images(image_url.rstrip() for image_url in image_urls)

    print("Time elapsed = {:.3f}".format(time.time() - start_time))


if __name__ == '__main__':
    main()
