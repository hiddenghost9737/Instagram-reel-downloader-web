import os
import torch
from flask import Flask, render_template, request, jsonify
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from diffusers import StableDiffusionPipeline
import numpy as np

# --- Load Models and Setup ---
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v-1-4-original")
pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# --- Helper Functions ---
def load_image(image_path: str):
    """Loads an image for conditioning (e.g., sketch, depth map)."""
    return Image.open(image_path)

def refine_to_high_resolution(image: Image) -> Image:
    """Progressively refines an image to high resolution."""
    for _ in range(5):  # 5 refinement steps for high-resolution generation
        image = pipe(prompt, init_image=image, num_inference_steps=50, guidance_scale=12.0).images[0]
    return image

def apply_attention(image: Image, attention_maps) -> Image:
    """Applies attention mechanisms to the generated image."""
    return image  # Placeholder, can be customized

def gan_refinement(image: Image) -> Image:
    """Uses a GAN for further image refinement if needed."""
    return image  # Placeholder, can be customized

# --- Flask Routes ---
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_advanced_image():
    """Generates an advanced image based on the prompt and control image."""
    prompt = request.form.get("prompt")
    control_image = request.files["control_image"]

    # Save the control image temporarily
    control_image_path = os.path.join("static", control_image.filename)
    control_image.save(control_image_path)

    # Step 1: Generate an initial image using Stable Diffusion
    initial_image = pipe(prompt).images[0]

    # Step 2: Load the control image (e.g., sketch, depth map)
    control_image = load_image(control_image_path)
    width, height = control_image.size

    # Step 3: Generate refined image using multi-scale refinement
    refined_image = refine_to_high_resolution(initial_image)

    # Step 4: Apply CLIP to ensure the image matches the prompt
    input_text = clip_processor(text=prompt, return_tensors="pt", padding=True)
    generated_image_tensor = torch.tensor(np.array(refined_image)).unsqueeze(0).float()

    # Get CLIP embeddings and compare with generated image embeddings
    clip_embeddings = clip_model.get_text_features(**input_text)
    similarity_score = torch.cosine_similarity(clip_embeddings, generated_image_tensor)

    if similarity_score < 0.8:
        refined_image = pipe(prompt, init_image=refined_image, num_inference_steps=50, guidance_scale=15.0).images[0]

    # Step 5: Apply attention mechanisms for targeted focus
    refined_image = apply_attention(refined_image, attention_maps=None)

    # Step 6: Optionally apply GAN-based refinement
    refined_image = gan_refinement(refined_image)

    # Save and return the generated image
    output_path = os.path.join("static", "generated_image.png")
    refined_image.save(output_path)

    return jsonify({"message": "Image generated successfully", "image_path": output_path})

if __name__ == '__main__':
    app.run(debug=True)
