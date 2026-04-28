import cv2
import os
import tempfile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

def generate_video_thumbnail(video_file, thumbnail_field, timestamp_ms=1000):
    """
    Extracts a frame from the video and saves it to the thumbnail field.
    
    Args:
        video_file: The Video FileField object.
        thumbnail_field: The ImageField object to save the thumbnail to.
        timestamp_ms: Time in milliseconds to extract the frame from (default 1s).
    """
    if not video_file:
        return

    try:
        # Create a temporary file to store the video content for OpenCV
        # OpenCV needs a file path, it cannot read from Django's File object directly if it's in memory/S3
        suffix = os.path.splitext(video_file.name)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_video:
            for chunk in video_file.chunks():
                temp_video.write(chunk)
            temp_video_path = temp_video.name

        cap = cv2.VideoCapture(temp_video_path)
        
        # Set the position to timestamp_ms
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        
        success, frame = cap.read()
        if not success:
            # Fallback to the first frame if timestamp fails
            cap.set(cv2.CAP_PROP_POS_MSEC, 0)
            success, frame = cap.read()

        if success:
            # Convert frame to image bytes
            _, buffer = cv2.imencode('.jpg', frame)
            content = ContentFile(buffer.tobytes())
            
            # Generate thumbnail name
            video_name = os.path.basename(video_file.name)
            thumb_name = f"thumb_{os.path.splitext(video_name)[0]}.jpg"
            
            # Save to field
            thumbnail_field.save(thumb_name, content, save=False)
            logger.info(f"Generated thumbnail for {video_file.name}")
        else:
            logger.warning(f"Could not extract frame from video {video_file.name}")

        cap.release()
        # Clean up temp file
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

    except Exception as e:
        logger.error(f"Error generating thumbnail for {video_file.name}: {str(e)}")
