import json
import os
import urllib.parse
import boto3
from PIL import Image
import io

# Initialize S3 client
s3_client = boto3.client('s3')

# Target settings
TARGET_PREFIX = "compressed/"
COMPRESSION_QUALITY = 70  # Scale from 1 to 95 (higher is better quality, larger size)

def lambda_handler(event, context):
    try:
        # 1. Parse bucket name and object key from the S3 event
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        
        # Object key can be URL-encoded (e.g., spaces converted to '+')
        raw_key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        print(f"Processing file from bucket: {bucket_name}, key: {raw_key}")
        
        # Safely extract filename
        filename = os.path.basename(raw_key)
        if not filename:
            print("Error: Could not extract filename from key.")
            return
            
        # 2. Download the raw image from S3 into memory
        response = s3_client.get_object(Bucket=bucket_name, Key=raw_key)
        image_content = response['Body'].read()
        
        # 3. Open image using Pillow
        image = Image.open(io.BytesIO(image_content))
        
        # Determine image format (JPEG, PNG, etc.)
        img_format = image.format if image.format else 'JPEG'
        
        # Convert RGBA to RGB if saving as JPEG (JPEGs don't support alpha transparency channels)
        if img_format == 'JPEG' and image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3]) # 3 is the alpha channel
            image = background

        # 4. Compress the image completely in memory (using io.BytesIO)
        buffer = io.BytesIO()
        
        # Apply optimization based on format
        if img_format in ['JPEG', 'JPG']:
            image.save(buffer, format='JPEG', optimize=True, quality=COMPRESSION_QUALITY)
        elif img_format == 'PNG':
            # PNG is lossless, optimize=True attempts to find better pixel compression blocks
            image.save(buffer, format='PNG', optimize=True)
        else:
            # Fallback for other formats
            image.save(buffer, format=img_format)
            
        buffer.seek(0)
        
        # 5. Define new key pointing to the 'compressed/' folder
        compressed_key = f"{TARGET_PREFIX}{filename}"
        
        # 6. Upload compressed image back to the S3 bucket
        s3_client.put_object(
            Bucket=bucket_name,
            Key=compressed_key,
            Body=buffer,
            ContentType=response.get('ContentType', 'image/jpeg')
        )
        
        print(f"Successfully compressed and uploaded to: {compressed_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully processed {filename}')
        }
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise e