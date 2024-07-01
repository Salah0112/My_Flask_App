from spire.presentation import Presentation, IVideo
from PIL import Image
import cv2
import numpy as np
from sklearn.cluster import KMeans


def get_dominant_color(image, k=3):
    # Resize the image for faster processing
    img = cv2.resize(image, (50, 50))
    # Reshape the image to a 2D array of pixels
    img = img.reshape((img.shape[0] * img.shape[1], 3))

    # Number of unique colors in the image
    unique_colors = np.unique(img, axis=0).shape[0]
    k = min(k, unique_colors)  # Adjust k to be at most the number of unique colors

    if k <= 1:
        # If only one unique color, return it directly
        return img[0]

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(img)

    # Cluster centers (centroids)
    colors = kmeans.cluster_centers_
    # Labels for each pixel
    labels = kmeans.labels_

    # Count the number of pixels in each cluster
    counts = np.bincount(labels)

    # Find the index of the largest cluster
    dominant_color = colors[np.argmax(counts)]

    # Return the dominant color as an integer array
    return dominant_color.astype(int)


def remove_watermark(image_path):
    # Read the image
    img = cv2.imread(image_path)
    height, width, _ = img.shape

    # Define the watermark dimensions
    watermark_height = 60
    watermark_width = int(0.58 * width)

    # Define the number of sections to divide the watermark area into
    num_vertical_sections = 5
    num_horizontal_sections = 6
    vertical_section_width = watermark_width // num_vertical_sections
    horizontal_section_height = watermark_height // num_horizontal_sections
    overlap = 10  # Pixels of overlap

    # Mask to accumulate all single-section masks for final inpainting
    full_mask = np.zeros(img.shape[:2], dtype="uint8")

    for j in range(num_horizontal_sections):
        for i in range(num_vertical_sections):
            section_start_x = max(0, i * vertical_section_width - overlap)
            section_end_x = min(width, (
                                                   i + 1) * vertical_section_width + overlap if i < num_vertical_sections - 1 else watermark_width)
            section_start_y = max(0, j * horizontal_section_height - overlap)
            section_end_y = min(height, (
                                                    j + 1) * horizontal_section_height + overlap if j < num_horizontal_sections - 1 else watermark_height)

            # Extract the section
            section = img[section_start_y:section_end_y, section_start_x:section_end_x]
            # Get the dominant color for the section
            dominant_color = get_dominant_color(section)
            # Fill the section with the dominant color
            img[section_start_y:section_end_y, section_start_x:section_end_x] = dominant_color

            # Update the full mask
            full_mask[section_start_y:section_end_y, section_start_x:section_end_x] = 255

    # Apply global inpainting once all sections are processed
    img = cv2.inpaint(img, full_mask, 3, cv2.INPAINT_TELEA)

    # Optionally apply a gentle blur to the entire watermark area for further smoothing
    img[:watermark_height, :watermark_width] = cv2.GaussianBlur(img[:watermark_height, :watermark_width], (5, 5), 0)

    # Save the cleaned image
    cv2.imwrite(image_path.replace(".jpg", "_cleaned.jpg"), img)


def convert_ppt_to_images_and_videos(pptx_file, output_dir, image_resolution=(1920, 1080), image_quality=95):

    # Create a Presentation instance
    presentation = Presentation()

    # Load the PowerPoint presentation
    presentation.LoadFromFile(pptx_file)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize a list to store slide images and video information
    slide_info_list = []

    # Initialize the overall slide index
    overall_slide_index = 0

    # Process the presentation in chunks of 9 slides
    while presentation.Slides.Count > 0:
        # Process the next 9 slides or remaining slides if less than 9
        for current_slide_index in range(min(9, presentation.Slides.Count)):
            # Get the current slide
            slide = presentation.Slides[0]

            # Specify the output file name for the slide image
            slide_image_file = os.path.join(output_dir, f'slide_{overall_slide_index}.png')

            # Save the slide as a PNG image
            image = slide.SaveAsImage()
            image.Save(slide_image_file)
            image.Dispose()

            # Open the saved image and resize it to the specified resolution
            img = Image.open(slide_image_file)
            img = img.resize(image_resolution, Image.LANCZOS)
            img.save(slide_image_file, quality=image_quality)
            img.close()

            remove_watermark(slide_image_file)

            # Initialize a list to store video information for the current slide
            slide_videos = []

            # Get slide dimensions
            slide_width = presentation.SlideSize.Size.Width
            slide_height = presentation.SlideSize.Size.Height

            # Loop through all shapes on the slide
            video_index = 0
            for shape in slide.Shapes:
                # Check if the shape is an embedded video
                if isinstance(shape, IVideo):
                    # Calculate video position and size as percentages of slide dimensions
                    video_left_percent = (shape.Left / slide_width) * 100
                    video_top_percent = (shape.Top / slide_height) * 100
                    video_width_percent = (shape.Width / slide_width) * 100
                    video_height_percent = (shape.Height / slide_height) * 100

                    # Specify the output file path for the video
                    video_output_file = os.path.join(output_dir, f'video_{overall_slide_index}_{video_index}.mp4')

                    # Save the video to the specified path
                    shape.EmbeddedVideoData.SaveToFile(video_output_file)

                    # Append video information to the list for the current slide
                    slide_videos.append({
                        "left_percent": video_left_percent,
                        "top_percent": video_top_percent,
                        "width_percent": video_width_percent,
                        "height_percent": video_height_percent,
                        "video_file": video_output_file
                    })
                    video_index += 1

            # Append slide image file path and video information to the slide info list
            slide_info_list.append({
                "image_file": slide_image_file,
                "videos": slide_videos
            })

            # Remove the processed slide from the presentation
            presentation.Slides.RemoveAt(0)

            # Increment the overall slide index
            overall_slide_index += 1

    # Dispose of the presentation object
    presentation.Dispose()

    return slide_info_list


"""
    for slide_info in slide_info_list:
        print("Slide Image File:", slide_info["image_file"])
        for video_info in slide_info["videos"]:
            print("Video Information:", video_info)
        print("\n")"""



import os


def generate_presentation_html(slide_info_list):
    from flask import url_for
    html_content = ''  # Start with an empty string

    try:
        for slide in slide_info_list:
            if 'image_file' in slide:
                # Clean up the file path and create the URL
                image_path = url_for('static',
                                     filename=slide['image_file'].replace("TV_Display/static/", "").replace("\\", "/"))

                # Start the section with properly indented HTML
                html_content += f'<section style="background-image: url({image_path}); background-size: cover; background-position: center; height: 100%; min-height: 100vh;">\n'

                # Process any videos included in the slide
                videos = slide.get('videos', [])
                for video_info in videos:
                    video_path = url_for('static',
                                         filename=video_info['video_file'].replace("TV_Display/static/", "").replace(
                                             "\\", "/"))
                    left_vw = video_info.get('left_percent', 50)
                    top_vh = video_info.get('top_percent', 50)
                    width_vw = video_info.get('width_percent', 30)
                    height_vh = video_info.get('height_percent', 20)

                    # Add the video with the specified styles and controls, maintaining indentation
                    html_content += f'''\
                        <div style="position: absolute; left: {left_vw}vw; top: {top_vh}vh; width: {width_vw}vw; height: {height_vh}vh; z-index: 100; display: flex; justify-content: center; align-items: center;">
                            <video controls autoplay style="width: 100%; height: 100%;" loading="lazy">
                                <source src="{video_path}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>\n'''

                # End the section with proper indentation
                html_content += '    </section>\n'
    except Exception as e:
        html_content += f'<p>Error generating slide content: {str(e)}</p>\n'

    return html_content


def generate_video_html(video_file_path):
    return f'''
    <section>
        <video controls autoplay width="100%">
            <source src="{video_file_path}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </section>
    '''
def generate_pdf_html(pdf_file_path):
    return f'''
    <section>
        <iframe src="{pdf_file_path}" width="100%" height="600px"></iframe>
    </section>
    '''


def generate_image(image_file_path):

    return f'''
    <section style="background-image: url({image_file_path}); background-size: cover; background-position: center; height: 100%; min-height: 100vh;">
    </section>\n'''


def adjust_image_resolution(image_file_path, new_resolution=(1920, 1080)):
    """
    Adjust the resolution of an image, attempting to preserve the original quality.

    Args:
    image_file_path (str): The path to the image file.
    new_resolution (tuple): The new resolution as a tuple, e.g., (width, height).

    Returns:
    str: Path to the adjusted image.
    """

    img = Image.open(image_file_path)

        # Resize the image using high-quality resampling
    img = img.resize(new_resolution, Image.LANCZOS)

        # Save the image to the same filepath
    img.save(image_file_path)

    img.close()
from flask import url_for
