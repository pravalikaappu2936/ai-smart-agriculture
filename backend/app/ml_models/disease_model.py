import json
from functools import lru_cache
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    BASE_DIR
    / "app"
    / "ml_models"
    / "saved_models"
)

MODEL_PATH = (
    MODEL_DIR
    / "plant_disease_model.pth"
)

METADATA_PATH = (
    MODEL_DIR
    / "plant_disease_metadata.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

IMAGE_SIZE = 224

DEVICE = torch.device("cpu")


# ============================================================
# IMAGE TRANSFORM
# ============================================================

IMAGE_TRANSFORM = transforms.Compose([
    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[
            0.485,
            0.456,
            0.406
        ],
        std=[
            0.229,
            0.224,
            0.225
        ]
    )
])


# ============================================================
# LOAD METADATA
# ============================================================

@lru_cache(maxsize=1)
def load_metadata():

    if not METADATA_PATH.exists():

        raise FileNotFoundError(
            f"Disease metadata not found:\n"
            f"{METADATA_PATH}"
        )

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(file)

    return metadata


# ============================================================
# CREATE MODEL
# ============================================================

def create_model(num_classes):

    model = models.mobilenet_v3_small(
        weights=None
    )

    input_features = (
        model.classifier[-1]
        .in_features
    )

    model.classifier[-1] = nn.Linear(
        input_features,
        num_classes
    )

    return model


# ============================================================
# LOAD MODEL LAZILY
# ============================================================

@lru_cache(maxsize=1)
def load_disease_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Disease model not found:\n"
            f"{MODEL_PATH}"
        )

    metadata = load_metadata()

    class_names = metadata["classes"]

    model = create_model(
        len(class_names)
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True
    )

    model.load_state_dict(
        checkpoint
    )

    model.to(DEVICE)

    model.eval()

    return model, class_names


# ============================================================
# FORMAT DISEASE NAME
# ============================================================

def format_disease_name(
    class_name
):

    parts = class_name.split(
        "___",
        1
    )

    if len(parts) != 2:

        return class_name

    crop = parts[0]

    disease = parts[1]

    crop = crop.replace(
        "_",
        " "
    )

    disease = disease.replace(
        "_",
        " "
    )

    disease = disease.replace(
        "  ",
        " "
    )

    return (
        crop,
        disease
    )


# ============================================================
# DISEASE INFORMATION
# ============================================================

DISEASE_INFO = {

    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab",
        "treatment": "Remove infected leaves and fruits. Apply an appropriate fungicide according to local agricultural recommendations.",
        "prevention": "Maintain good orchard sanitation, remove fallen leaves, and improve air circulation."
    },

    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot",
        "treatment": "Remove infected plant material and prune affected branches. Use recommended fungicide when necessary.",
        "prevention": "Remove dead wood and infected fruits and maintain proper orchard sanitation."
    },

    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "disease": "Cedar Apple Rust",
        "treatment": "Remove severely affected plant material and use an appropriate fungicide when recommended.",
        "prevention": "Maintain orchard sanitation and reduce nearby alternate hosts where practical."
    },

    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Continue regular monitoring, proper watering, nutrition, and orchard sanitation."
    },

    "Blueberry___healthy": {
        "crop": "Blueberry",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper irrigation, nutrition, air circulation, and regular monitoring."
    },

    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Powdery Mildew",
        "treatment": "Remove severely affected leaves and improve air circulation. Apply a recommended fungicide if required.",
        "prevention": "Avoid excessive humidity around foliage and maintain good canopy ventilation."
    },

    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Continue regular monitoring and maintain proper irrigation and orchard hygiene."
    },

    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn",
        "disease": "Cercospora Leaf Spot / Gray Leaf Spot",
        "treatment": "Remove heavily infected crop residue where appropriate and use recommended fungicide practices.",
        "prevention": "Use resistant varieties, crop rotation, and good field sanitation."
    },

    "Corn_(maize)___Common_rust_": {
        "crop": "Corn",
        "disease": "Common Rust",
        "treatment": "Monitor disease development and use a recommended fungicide when economically justified.",
        "prevention": "Use resistant varieties and maintain balanced crop nutrition."
    },

    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn",
        "disease": "Northern Leaf Blight",
        "treatment": "Use appropriate fungicide treatment when necessary and manage infected crop residue.",
        "prevention": "Use resistant hybrids, crop rotation, and field sanitation."
    },

    "Corn_(maize)___healthy": {
        "crop": "Corn",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper irrigation, nutrition, weed management, and regular crop monitoring."
    },

    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Black Rot",
        "treatment": "Remove infected berries and plant material and apply recommended fungicide treatment.",
        "prevention": "Maintain canopy airflow, remove infected material, and avoid prolonged leaf wetness."
    },

    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape",
        "disease": "Esca / Black Measles",
        "treatment": "Remove severely affected vines or infected wood where appropriate and consult local plant disease recommendations.",
        "prevention": "Use healthy planting material and maintain careful pruning and vineyard sanitation."
    },

    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape",
        "disease": "Leaf Blight",
        "treatment": "Remove infected foliage where practical and apply a recommended fungicide.",
        "prevention": "Improve canopy ventilation and reduce prolonged moisture on leaves."
    },

    "Grape___healthy": {
        "crop": "Grape",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper irrigation, nutrition, pruning, and vineyard sanitation."
    },

    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange",
        "disease": "Huanglongbing / Citrus Greening",
        "treatment": "There is no simple curative treatment for infected trees. Follow local citrus disease management recommendations and manage the insect vector.",
        "prevention": "Use certified planting material and monitor and control psyllid vectors."
    },

    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "disease": "Bacterial Spot",
        "treatment": "Remove severely affected plant material and follow locally recommended bacterial disease management practices.",
        "prevention": "Use resistant varieties where available and avoid unnecessary leaf wetness."
    },

    "Peach___healthy": {
        "crop": "Peach",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper irrigation, nutrition, pruning, and orchard sanitation."
    },

    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "disease": "Bacterial Spot",
        "treatment": "Remove severely infected plant material and follow recommended bacterial disease management practices.",
        "prevention": "Use disease-free seed, avoid overhead irrigation, and maintain field sanitation."
    },

    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain balanced nutrition, appropriate irrigation, and regular crop monitoring."
    },

    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "treatment": "Remove infected foliage and use an appropriate fungicide according to local recommendations.",
        "prevention": "Use crop rotation, proper irrigation, resistant varieties, and remove infected crop residue."
    },

    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "treatment": "Remove severely infected material and apply an appropriate fungicide promptly according to local recommendations.",
        "prevention": "Use disease-free seed, resistant varieties, good field sanitation, and avoid prolonged leaf wetness."
    },

    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper irrigation, nutrition, crop rotation, and regular monitoring."
    },

    "Raspberry___healthy": {
        "crop": "Raspberry",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain good airflow, appropriate irrigation, nutrition, and regular monitoring."
    },

    "Soybean___healthy": {
        "crop": "Soybean",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain balanced nutrition, proper irrigation, weed management, and crop monitoring."
    },

    "Squash___Powdery_mildew": {
        "crop": "Squash",
        "disease": "Powdery Mildew",
        "treatment": "Remove severely affected leaves and use an appropriate fungicide when recommended.",
        "prevention": "Improve air circulation, avoid excessive humidity, and maintain adequate plant spacing."
    },

    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "disease": "Leaf Scorch",
        "treatment": "Remove severely affected leaves and follow recommended disease management practices.",
        "prevention": "Maintain field sanitation, proper irrigation, and good airflow."
    },

    "Strawberry___healthy": {
        "crop": "Strawberry",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper irrigation, nutrition, spacing, and regular crop monitoring."
    },

    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "treatment": "Remove infected plant material and follow locally recommended bacterial disease management practices.",
        "prevention": "Use disease-free seed, avoid overhead irrigation, and maintain good field sanitation."
    },

    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "treatment": "Remove affected leaves and use an appropriate fungicide according to local recommendations.",
        "prevention": "Use crop rotation, proper spacing, mulching, and avoid prolonged leaf wetness."
    },

    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "treatment": "Remove infected plant material and apply an appropriate fungicide promptly according to local recommendations.",
        "prevention": "Use disease-free planting material, improve airflow, and reduce prolonged leaf moisture."
    },

    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Leaf Mold",
        "treatment": "Remove affected leaves and improve ventilation. Apply recommended fungicide when necessary.",
        "prevention": "Reduce humidity, improve greenhouse ventilation, and avoid prolonged leaf wetness."
    },

    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot",
        "treatment": "Remove affected leaves and apply an appropriate fungicide when recommended.",
        "prevention": "Use crop rotation, remove infected residue, and avoid overhead watering."
    },

    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Spider Mites",
        "treatment": "Use appropriate integrated pest management measures and locally recommended miticides when necessary.",
        "prevention": "Monitor the undersides of leaves, reduce plant stress, and encourage beneficial predators."
    },

    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Target Spot",
        "treatment": "Remove infected leaves and use a recommended fungicide when required.",
        "prevention": "Maintain good airflow, proper plant spacing, and field sanitation."
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus",
        "treatment": "Remove severely infected plants and manage whitefly vectors according to local recommendations.",
        "prevention": "Use resistant varieties, healthy seedlings, insect monitoring, and whitefly management."
    },

    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus",
        "treatment": "Remove infected plants and sanitize tools and hands to reduce mechanical transmission.",
        "prevention": "Use certified disease-free seed and maintain strict sanitation."
    },

    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy",
        "treatment": "No disease treatment is required.",
        "prevention": "Continue regular monitoring and maintain proper irrigation, nutrition, spacing, and sanitation."
    }
}


# ============================================================
# PREDICTION
# ============================================================

def predict_disease(
    image
):

    # Load model only when prediction is requested
    model, class_names = (
        load_disease_model()
    )


    # --------------------------------------------------------
    # Prepare image
    # --------------------------------------------------------

    if not isinstance(
        image,
        Image.Image
    ):

        image = Image.open(
            image
        )


    image = image.convert(
        "RGB"
    )


    tensor = IMAGE_TRANSFORM(
        image
    )


    tensor = tensor.unsqueeze(
        0
    )


    tensor = tensor.to(
        DEVICE
    )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(
            tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, prediction = (
            torch.max(
                probabilities,
                dim=1
            )
        )


    class_index = (
        prediction.item()
    )

    confidence_value = (
        confidence.item()
        * 100
    )


    class_name = (
        class_names[
            class_index
        ]
    )


    # --------------------------------------------------------
    # Disease information
    # --------------------------------------------------------

    info = DISEASE_INFO.get(
        class_name
    )


    if info is None:

        crop_disease = (
            format_disease_name(
                class_name
            )
        )

        if isinstance(
            crop_disease,
            tuple
        ):

            crop_name, disease_name = (
                crop_disease
            )

        else:

            crop_name = "Unknown"

            disease_name = (
                crop_disease
            )

        info = {

            "crop": crop_name,

            "disease": disease_name,

            "treatment":
                "Consult a local agricultural expert for appropriate treatment.",

            "prevention":
                "Maintain crop hygiene and regularly monitor the plant."

        }


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "success": True,

        "crop": info["crop"],

        "disease": info["disease"],

        "confidence": round(
            confidence_value,
            2
        ),

        "class_index":
            class_index,

        "treatment":
            info["treatment"],

        "prevention":
            info["prevention"],

        "model":
            "MobileNetV3-Small",

        "model_accuracy":
            load_metadata().get(
                "validation_accuracy"
            ),

        "dataset_images_used":
            load_metadata().get(
                "dataset_images_used"
            ),

        "total_classes":
            len(class_names)

    }