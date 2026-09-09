import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { predictPlantDisease } from "../services/api";
import "./PlantDisease.css";

// =========================================================
// PLANT DISEASE DETECTION
// =========================================================

const TEXT = {
    en: {
        title: "Plant Disease Detection",
        subtitle:
            "Upload a plant leaf image or use your camera to identify possible diseases and get treatment guidance.",

        backDashboard: "← Back to Dashboard",

        uploadTitle: "Upload Plant Leaf Image",
        uploadDescription:
            "Choose a clear image of a plant leaf or capture one using your camera.",

        chooseImage: "Choose Image",
        changeImage: "Change Image",
        removeImage: "Remove Image",

        useCamera: "Use Camera",
        closeCamera: "Close Camera",
        capturePhoto: "Capture Photo",
        retakePhoto: "Retake Photo",
        usePhoto: "Use Photo",

        cameraStarting: "Starting camera...",
        cameraPermission:
            "Please allow camera permission in your browser.",
        cameraNotSupported:
            "Camera is not supported by this browser or device.",
        cameraReady:
            "Position the leaf inside the frame",
        cameraDescription:
            "Take a photo directly using your camera.",

        capturedPhoto: "Captured Photo",

        supported:
            "Supported formats: JPG, JPEG, PNG • Maximum size: 5 MB",

        predict: "Detect Disease",
        detecting: "Analyzing Image...",

        resultTitle: "Disease Detection Result",

        crop: "Crop",
        disease: "Detected Disease",
        confidence: "Confidence",
        treatment: "Treatment",
        prevention: "Prevention",

        modelInformation: "Model Information",
        model: "Model",
        accuracy: "Validation Accuracy",
        datasetImages: "Images Used",
        classes: "Disease Classes",

        uploadFirst:
            "Please upload or capture a plant leaf image first.",

        error:
            "Unable to analyze the image. Please try again.",

        capturedTooLarge:
            "Captured image is larger than 5 MB.",

        cameraNotReady:
            "Camera is not ready. Please wait a moment and try again.",

        healthy: "Healthy",

        diseaseDetected: "Disease Detected",

        noResult:
            "Upload or capture an image and click Detect Disease to see the result.",

        noCamera:
            "No camera was found. Please check your camera connection.",

        cameraBusy:
            "The camera is being used by another application.",
    },

    kn: {
        title: "ಸಸ್ಯ ರೋಗ ಪತ್ತೆ",

        subtitle:
            "ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕ್ಯಾಮೆರಾ ಬಳಸಿ ಚಿತ್ರ ತೆಗೆದು ರೋಗವನ್ನು ಗುರುತಿಸಿ ಮತ್ತು ಚಿಕಿತ್ಸೆಯ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯಿರಿ.",

        backDashboard: "← ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ",

        uploadTitle: "ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",

        uploadDescription:
            "ಸ್ಪಷ್ಟವಾದ ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಕ್ಯಾಮೆರಾ ಬಳಸಿ ಚಿತ್ರ ತೆಗೆಯಿರಿ.",

        chooseImage: "ಚಿತ್ರ ಆಯ್ಕೆಮಾಡಿ",
        changeImage: "ಚಿತ್ರ ಬದಲಾಯಿಸಿ",
        removeImage: "ಚಿತ್ರ ತೆಗೆದುಹಾಕಿ",

        useCamera: "ಕ್ಯಾಮೆರಾ ಬಳಸಿ",
        closeCamera: "ಕ್ಯಾಮೆರಾ ಮುಚ್ಚಿ",
        capturePhoto: "ಚಿತ್ರ ತೆಗೆಯಿರಿ",
        retakePhoto: "ಮತ್ತೆ ಚಿತ್ರ ತೆಗೆಯಿರಿ",
        usePhoto: "ಚಿತ್ರ ಬಳಸಿ",

        cameraStarting: "ಕ್ಯಾಮೆರಾ ಪ್ರಾರಂಭಿಸಲಾಗುತ್ತಿದೆ...",

        cameraPermission:
            "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಕ್ಯಾಮೆರಾ ಅನುಮತಿಯನ್ನು ನೀಡಿ.",

        cameraNotSupported:
            "ಈ ಬ್ರೌಸರ್ ಅಥವಾ ಸಾಧನದಲ್ಲಿ ಕ್ಯಾಮೆರಾ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ.",

        cameraReady:
            "ಎಲೆಯನ್ನು ಚೌಕಟ್ಟಿನ ಒಳಗೆ ಇರಿಸಿ",

        cameraDescription:
            "ಕ್ಯಾಮೆರಾ ಬಳಸಿ ನೇರವಾಗಿ ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ತೆಗೆಯಿರಿ.",

        capturedPhoto: "ತೆಗೆದ ಚಿತ್ರ",

        supported:
            "ಬೆಂಬಲಿತ ಫಾರ್ಮ್ಯಾಟ್‌ಗಳು: JPG, JPEG, PNG • ಗರಿಷ್ಠ ಗಾತ್ರ: 5 MB",

        predict: "ರೋಗ ಪತ್ತೆ ಮಾಡಿ",
        detecting: "ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",

        resultTitle: "ರೋಗ ಪತ್ತೆ ಫಲಿತಾಂಶ",

        crop: "ಬೆಳೆ",
        disease: "ಪತ್ತೆಯಾದ ರೋಗ",
        confidence: "ವಿಶ್ವಾಸಾರ್ಹತೆ",
        treatment: "ಚಿಕಿತ್ಸೆ",
        prevention: "ತಡೆಗಟ್ಟುವಿಕೆ",

        modelInformation: "ಮಾದರಿ ಮಾಹಿತಿ",
        model: "ಮಾದರಿ",
        accuracy: "ಮೌಲ್ಯಮಾಪನ ನಿಖರತೆ",
        datasetImages: "ಬಳಸಿದ ಚಿತ್ರಗಳು",
        classes: "ರೋಗ ವರ್ಗಗಳು",

        uploadFirst:
            "ಮೊದಲು ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕ್ಯಾಮೆರಾದಿಂದ ಚಿತ್ರ ತೆಗೆಯಿರಿ.",

        error:
            "ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",

        capturedTooLarge:
            "ತೆಗೆದ ಚಿತ್ರವು 5 MB ಗಿಂತ ದೊಡ್ಡದಾಗಿದೆ.",

        cameraNotReady:
            "ಕ್ಯಾಮೆರಾ ಇನ್ನೂ ಸಿದ್ಧವಾಗಿಲ್ಲ. ಸ್ವಲ್ಪ ಸಮಯ ಕಾಯ್ದು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",

        healthy: "ಆರೋಗ್ಯಕರ",

        diseaseDetected: "ರೋಗ ಪತ್ತೆಯಾಗಿದೆ",

        noResult:
            "ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕ್ಯಾಮೆರಾದಿಂದ ಚಿತ್ರ ತೆಗೆದು ಫಲಿತಾಂಶವನ್ನು ನೋಡಲು ರೋಗ ಪತ್ತೆ ಬಟನ್ ಒತ್ತಿರಿ.",

        noCamera:
            "ಕ್ಯಾಮೆರಾ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಕ್ಯಾಮೆರಾ ಸಂಪರ್ಕವನ್ನು ಪರಿಶೀಲಿಸಿ.",

        cameraBusy:
            "ಕ್ಯಾಮೆರಾವನ್ನು ಮತ್ತೊಂದು ಅಪ್ಲಿಕೇಶನ್ ಬಳಸುತ್ತಿದೆ.",
    },
};

// =========================================================
// CROP TRANSLATION
// =========================================================

const KANNADA_CROP_NAMES = {
    Apple: "ಆಪಲ್",
    Blueberry: "ಬ್ಲೂಬೆರ್ರಿ",
    Cherry: "ಚೆರ್ರಿ",
    Corn: "ಜೋಳ",
    Grape: "ದ್ರಾಕ್ಷಿ",
    Orange: "ಕಿತ್ತಳೆ",
    Peach: "ಪೀಚ್",
    Pepper: "ಮೆಣಸಿನಕಾಯಿ",
    Potato: "ಆಲೂಗಡ್ಡೆ",
    Raspberry: "ರಾಸ್ಪ್ಬೆರಿ",
    Soybean: "ಸೋಯಾಬೀನ್",
    Squash: "ಸ್ಕ್ವಾಷ್",
    Strawberry: "ಸ್ಟ್ರಾಬೆರಿ",
    Tomato: "ಟೊಮೆಟೊ",
};

// =========================================================
// DISEASE NAME TRANSLATION
// =========================================================

const KANNADA_DISEASE_NAMES = {
    "Apple Scab": "ಆಪಲ್ ಸ್ಕ್ಯಾಬ್",
    "Apple Black Rot": "ಆಪಲ್ ಬ್ಲ್ಯಾಕ್ ರಾಟ್",
    "Apple Cedar Apple Rust": "ಆಪಲ್ ಸೀಡರ್ ಆಪಲ್ ರಸ್ಟ್",
    "Healthy Apple": "ಆರೋಗ್ಯಕರ ಆಪಲ್",

    "Healthy Blueberry": "ಆರೋಗ್ಯಕರ ಬ್ಲೂಬೆರ್ರಿ",

    "Cherry Powdery Mildew": "ಚೆರ್ರಿ ಪೌಡರಿ ಮಿಲ್ಡ್ಯೂ",
    "Healthy Cherry": "ಆರೋಗ್ಯಕರ ಚೆರ್ರಿ",

    "Corn Cercospora Leaf Spot Gray Leaf Spot":
        "ಜೋಳದ ಸೆರ್ಕೋಸ್ಪೋರಾ ಎಲೆ ಕಲೆ",

    "Corn Common Rust": "ಜೋಳದ ಕಾಮನ್ ರಸ್ಟ್",

    "Corn Northern Leaf Blight":
        "ಜೋಳದ ನಾರ್ದರ್ನ್ ಲೀಫ್ ಬ್ಲೈಟ್",

    "Healthy Corn": "ಆರೋಗ್ಯಕರ ಜೋಳ",

    "Grape Black Rot": "ದ್ರಾಕ್ಷಿಯ ಬ್ಲ್ಯಾಕ್ ರಾಟ್",

    "Grape Esca Black Measles":
        "ದ್ರಾಕ್ಷಿಯ ಎಸ್ಕಾ",

    "Grape Leaf Blight Isariopsis Leaf Spot":
        "ದ್ರಾಕ್ಷಿಯ ಲೀಫ್ ಬ್ಲೈಟ್",

    "Healthy Grape": "ಆರೋಗ್ಯಕರ ದ್ರಾಕ್ಷಿ",

    "Orange Huanglongbing Citrus Greening":
        "ಕಿತ್ತಳೆಯ ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್",

    "Peach Bacterial Spot":
        "ಪೀಚ್ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸ್ಪಾಟ್",

    "Healthy Peach":
        "ಆರೋಗ್ಯಕರ ಪೀಚ್",

    "Bell Pepper Bacterial Spot":
        "ಬೆಲ್ ಪೆಪ್ಪರ್ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸ್ಪಾಟ್",

    "Healthy Bell Pepper":
        "ಆರೋಗ್ಯಕರ ಬೆಲ್ ಪೆಪ್ಪರ್",

    "Potato Early Blight":
        "ಆಲೂಗಡ್ಡೆಯ ಆರಂಭಿಕ ಬ್ಲೈಟ್",

    "Potato Late Blight":
        "ಆಲೂಗಡ್ಡೆಯ ತಡವಾದ ಬ್ಲೈಟ್",

    "Healthy Potato":
        "ಆರೋಗ್ಯಕರ ಆಲೂಗಡ್ಡೆ",

    "Healthy Raspberry":
        "ಆರೋಗ್ಯಕರ ರಾಸ್ಪ್ಬೆರಿ",

    "Healthy Soybean":
        "ಆರೋಗ್ಯಕರ ಸೋಯಾಬೀನ್",

    "Squash Powdery Mildew":
        "ಸ್ಕ್ವಾಷ್ ಪೌಡರಿ ಮಿಲ್ಡ್ಯೂ",

    "Strawberry Leaf Scorch":
        "ಸ್ಟ್ರಾಬೆರಿ ಲೀಫ್ ಸ್ಕಾರ್ಚ",

    "Healthy Strawberry":
        "ಆರೋಗ್ಯಕರ ಸ್ಟ್ರಾಬೆರಿ",

    "Tomato Bacterial Spot":
        "ಟೊಮೆಟೊ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸ್ಪಾಟ್",

    "Tomato Early Blight":
        "ಟೊಮೆಟೊ ಆರಂಭಿಕ ಬ್ಲೈಟ್",

    "Tomato Late Blight":
        "ಟೊಮೆಟೊ ತಡವಾದ ಬ್ಲೈಟ್",

    "Tomato Leaf Mold":
        "ಟೊಮೆಟೊ ಲೀಫ್ ಮೋಲ್ಡ್",

    "Tomato Septoria Leaf Spot":
        "ಟೊಮೆಟೊ ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಕಲೆ",

    "Tomato Spider Mites":
        "ಟೊಮೆಟೊ ಸ್ಪೈಡರ್ ಮೈಟ್ಸ್",

    "Tomato Target Spot":
        "ಟೊಮೆಟೊ ಟಾರ್ಗೆಟ್ ಸ್ಪಾಟ್",

    "Tomato Yellow Leaf Curl Virus":
        "ಟೊಮೆಟೊ ಯೆಲ್ಲೋ ಲೀಫ್ ಕರ್ಳ್ ವೈರಸ್",

    "Tomato Mosaic Virus":
        "ಟೊಮೆಟೊ ಮೊಸಾಯಿಕ್ ವೈರಸ್",

    "Healthy Tomato":
        "ಆರೋಗ್ಯಕರ ಟೊಮೆಟೊ",
};

// =========================================================
// TREATMENT / PREVENTION TRANSLATION
// =========================================================

const KANNADA_GUIDANCE = {
    "Apple Scab": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳು ಮತ್ತು ಹಣ್ಣುಗಳನ್ನು ತೆಗೆದುಹಾಕಿ. ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ತೋಟದಲ್ಲಿ ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ ಮತ್ತು ಬಿದ್ದ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ.",
    },

    "Apple Black Rot": {
        treatment:
            "ಸೋಂಕಿತ ಭಾಗಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಸತ್ತ ಕೊಂಬೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಮರದ ಸುತ್ತಲಿನ ಪ್ರದೇಶವನ್ನು ಸ್ವಚ್ಛವಾಗಿಡಿ.",
    },

    "Apple Cedar Apple Rust": {
        treatment:
            "ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ ಮತ್ತು ಸೋಂಕಿತ ಭಾಗಗಳನ್ನು ತೆಗೆದುಹಾಕಿ.",
        prevention:
            "ಸೋಂಕಿಗೆ ಒಳಗಾದ ಸಸ್ಯ ಭಾಗಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Healthy Apple": {
        treatment:
            "ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ಪ್ರಸ್ತುತ ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ನಿಯಮಿತವಾಗಿ ಸಸ್ಯವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಸರಿಯಾದ ನೀರು ಹಾಗೂ ಪೋಷಕಾಂಶಗಳನ್ನು ಒದಗಿಸಿ.",
    },

    "Healthy Blueberry": {
        treatment:
            "ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ಪ್ರಸ್ತುತ ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸಸ್ಯಕ್ಕೆ ಸರಿಯಾದ ನೀರು, ಪೋಷಕಾಂಶ ಮತ್ತು ಗಾಳಿಯ ಹರಿವು ಒದಗಿಸಿ.",
    },

    "Cherry Powdery Mildew": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಗಾಳಿಯ ಹರಿವು ಹೆಚ್ಚಿಸಿ ಮತ್ತು ಎಲೆಗಳ ಮೇಲೆ ಹೆಚ್ಚಿನ ತೇವಾಂಶ ಉಳಿಯದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
    },

    "Healthy Cherry": {
        treatment:
            "ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ನಿಯಮಿತವಾಗಿ ಸಸ್ಯವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Corn Cercospora Leaf Spot Gray Leaf Spot": {
        treatment:
            "ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ ಮತ್ತು ಸೋಂಕಿತ ಸಸ್ಯ ಅವಶೇಷಗಳನ್ನು ತೆಗೆದುಹಾಕಿ.",
        prevention:
            "ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಹೊಲದಲ್ಲಿ ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Corn Common Rust": {
        treatment:
            "ತೀವ್ರ ಸೋಂಕಿನ ಸಂದರ್ಭದಲ್ಲಿ ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ರೋಗ ನಿರೋಧಕ ಜೋಳದ ತಳಿಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ಉತ್ತಮ ಹೊಲ ನಿರ್ವಹಣೆ ಮಾಡಿ.",
    },

    "Corn Northern Leaf Blight": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಸೋಂಕಿತ ಅವಶೇಷಗಳನ್ನು ಹೊಲದಿಂದ ತೆಗೆದುಹಾಕಿ.",
    },

    "Healthy Corn": {
        treatment:
            "ಜೋಳದ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸರಿಯಾದ ನೀರಾವರಿ, ಪೋಷಕಾಂಶ ಮತ್ತು ಹೊಲ ನಿರ್ವಹಣೆ ಮುಂದುವರಿಸಿ.",
    },

    "Grape Black Rot": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳು ಮತ್ತು ಹಣ್ಣುಗಳನ್ನು ತೆಗೆದುಹಾಕಿ. ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ದ್ರಾಕ್ಷಿ ತೋಟದಲ್ಲಿ ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಮತ್ತು ಸ್ವಚ್ಛತೆ ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Grape Esca Black Measles": {
        treatment:
            "ತೀವ್ರವಾಗಿ ಸೋಂಕಿತ ಕೊಂಬೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ನಿರ್ವಹಣಾ ಕ್ರಮಗಳನ್ನು ಅನುಸರಿಸಿ.",
        prevention:
            "ಸೋಂಕಿತ ಕೊಂಬೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಕತ್ತರಿಸುವ ಉಪಕರಣಗಳನ್ನು ಸ್ವಚ್ಛವಾಗಿಡಿ.",
    },

    "Grape Leaf Blight Isariopsis Leaf Spot": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಗಾಳಿಯ ಹರಿವು ಸುಧಾರಿಸಿ ಮತ್ತು ಎಲೆಗಳ ಮೇಲೆ ನೀರು ಹೆಚ್ಚು ಕಾಲ ಉಳಿಯದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
    },

    "Healthy Grape": {
        treatment:
            "ದ್ರಾಕ್ಷಿ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸರಿಯಾದ ನೀರು, ಪೋಷಕಾಂಶ ಮತ್ತು ಕತ್ತರಿಸುವ ಕ್ರಮಗಳನ್ನು ಅನುಸರಿಸಿ.",
    },

    "Orange Huanglongbing Citrus Greening": {
        treatment:
            "ಸೋಂಕಿತ ಸಸ್ಯಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ರೋಗ ಹರಡುವ ಕೀಟಗಳನ್ನು ನಿಯಂತ್ರಿಸಿ.",
        prevention:
            "ರೋಗಮುಕ್ತ ನೆಡುವ ವಸ್ತು ಬಳಸಿ ಮತ್ತು ವಾಹಕ ಕೀಟಗಳ ನಿಯಂತ್ರಣ ಮಾಡಿ.",
    },

    "Peach Bacterial Spot": {
        treatment:
            "ಸೋಂಕಿತ ಭಾಗಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಶಿಫಾರಸು ಮಾಡಿದ ಬ್ಯಾಕ್ಟೀರಿಯಾ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಅನುಸರಿಸಿ.",
        prevention:
            "ಎಲೆಗಳ ಮೇಲೆ ನೀರು ಚಿಮ್ಮುವುದನ್ನು ಕಡಿಮೆ ಮಾಡಿ ಮತ್ತು ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Healthy Peach": {
        treatment:
            "ಪೀಚ್ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ನಿಯಮಿತವಾಗಿ ಸಸ್ಯವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಸರಿಯಾದ ನೀರಾವರಿ ಒದಗಿಸಿ.",
    },

    "Bell Pepper Bacterial Spot": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಬ್ಯಾಕ್ಟೀರಿಯಾ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಅನುಸರಿಸಿ.",
        prevention:
            "ರೋಗಮುಕ್ತ ಬೀಜಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ಎಲೆಗಳ ಮೇಲೆ ನೀರು ಚಿಮ್ಮುವುದನ್ನು ತಪ್ಪಿಸಿ.",
    },

    "Healthy Bell Pepper": {
        treatment:
            "ಬೆಲ್ ಪೆಪ್ಪರ್ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸರಿಯಾದ ನೀರು ಮತ್ತು ಪೋಷಕಾಂಶಗಳನ್ನು ನೀಡಿ ಮತ್ತು ಸಸ್ಯವನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.",
    },

    "Potato Early Blight": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಸಸ್ಯಗಳ ನಡುವೆ ಉತ್ತಮ ಅಂತರ ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Potato Late Blight": {
        treatment:
            "ತೀವ್ರ ಸೋಂಕಿತ ಭಾಗಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ತಕ್ಷಣ ಬಳಸಿ.",
        prevention:
            "ಅತಿಯಾದ ತೇವಾಂಶ ತಪ್ಪಿಸಿ ಮತ್ತು ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬಳಸುವುದು ಉತ್ತಮ.",
    },

    "Healthy Potato": {
        treatment:
            "ಆಲೂಗಡ್ಡೆ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸರಿಯಾದ ನೀರಾವರಿ ಮತ್ತು ಉತ್ತಮ ಹೊಲ ಸ್ವಚ್ಛತೆ ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Healthy Raspberry": {
        treatment:
            "ರಾಸ್ಪ್ಬೆರಿ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸರಿಯಾದ ನೀರು, ಪೋಷಕಾಂಶ ಮತ್ತು ಗಾಳಿಯ ಹರಿವು ಒದಗಿಸಿ.",
    },

    "Healthy Soybean": {
        treatment:
            "ಸೋಯಾಬೀನ್ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸರಿಯಾದ ನೀರಾವರಿ, ಪೋಷಕಾಂಶ ಮತ್ತು ಕೀಟ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಅನುಸರಿಸಿ.",
    },

    "Squash Powdery Mildew": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಸಸ್ಯಗಳ ನಡುವೆ ಸಾಕಷ್ಟು ಅಂತರವಿಟ್ಟು ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Strawberry Leaf Scorch": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸಸ್ಯಕ್ಕೆ ಸೂಕ್ತ ಆರೈಕೆ ನೀಡಿ.",
        prevention:
            "ಸರಿಯಾದ ನೀರಾವರಿ ಮತ್ತು ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Healthy Strawberry": {
        treatment:
            "ಸ್ಟ್ರಾಬೆರಿ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸರಿಯಾದ ನೀರು ಮತ್ತು ಪೋಷಕಾಂಶಗಳನ್ನು ನೀಡಿ ಹಾಗೂ ಸಸ್ಯವನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.",
    },

    "Tomato Bacterial Spot": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಬ್ಯಾಕ್ಟೀರಿಯಾ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಅನುಸರಿಸಿ.",
        prevention:
            "ರೋಗಮುಕ್ತ ಬೀಜಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ಎಲೆಗಳ ಮೇಲೆ ನೀರು ಚಿಮ್ಮುವುದನ್ನು ತಪ್ಪಿಸಿ.",
    },

    "Tomato Early Blight": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಸಸ್ಯಗಳ ನಡುವೆ ಉತ್ತಮ ಅಂತರ ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Tomato Late Blight": {
        treatment:
            "ಸೋಂಕಿತ ಭಾಗಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಎಲೆಗಳ ಮೇಲೆ ನೀರು ಉಳಿಯದಂತೆ ನೋಡಿಕೊಳ್ಳಿ ಮತ್ತು ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Tomato Leaf Mold": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ತೇವಾಂಶವನ್ನು ನಿಯಂತ್ರಿಸಿ ಮತ್ತು ಉತ್ತಮ ಗಾಳಿಯ ಹರಿವು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
    },

    "Tomato Septoria Leaf Spot": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಸಸ್ಯದ ಸುತ್ತಲಿನ ಅವಶೇಷಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಎಲೆಗಳ ಮೇಲೆ ನೀರು ಚಿಮ್ಮುವುದನ್ನು ತಪ್ಪಿಸಿ.",
    },

    "Tomato Spider Mites": {
        treatment:
            "ಸೋಂಕಿತ ಸಸ್ಯವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಅಗತ್ಯವಿದ್ದರೆ ಸೂಕ್ತ ಕೀಟನಾಶಕ ಅಥವಾ ಮೈಟ್ ನಿಯಂತ್ರಣ ಕ್ರಮ ಬಳಸಿ.",
        prevention:
            "ಸಸ್ಯಕ್ಕೆ ಸೂಕ್ತ ತೇವಾಂಶ ಒದಗಿಸಿ ಮತ್ತು ನಿಯಮಿತವಾಗಿ ಕೀಟಗಳಿಗಾಗಿ ಪರಿಶೀಲಿಸಿ.",
    },

    "Tomato Target Spot": {
        treatment:
            "ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಬಳಸಿ.",
        prevention:
            "ಸಸ್ಯಗಳ ನಡುವೆ ಉತ್ತಮ ಅಂತರ ಕಾಪಾಡಿಕೊಳ್ಳಿ ಮತ್ತು ಎಲೆಗಳ ಮೇಲೆ ನೀರು ಉಳಿಯದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
    },

    "Tomato Yellow Leaf Curl Virus": {
        treatment:
            "ವೈರಸ್ ಸೋಂಕಿತ ಸಸ್ಯಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಬಿಳಿ ನೊಣಗಳ ನಿಯಂತ್ರಣ ಮಾಡಿ.",
        prevention:
            "ರೋಗಮುಕ್ತ ಸಸಿಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ವೈರಸ್ ಹರಡುವ ಕೀಟಗಳನ್ನು ನಿಯಂತ್ರಿಸಿ.",
    },

    "Tomato Mosaic Virus": {
        treatment:
            "ತೀವ್ರವಾಗಿ ಸೋಂಕಿತ ಸಸ್ಯಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಸೋಂಕಿತ ಸಸ್ಯಗಳನ್ನು ಮುಟ್ಟಿದ ನಂತರ ಕೈಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ.",
        prevention:
            "ರೋಗಮುಕ್ತ ಬೀಜಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ಉಪಕರಣಗಳನ್ನು ನಿಯಮಿತವಾಗಿ ಸ್ವಚ್ಛಗೊಳಿಸಿ.",
    },

    "Healthy Tomato": {
        treatment:
            "ಟೊಮೆಟೊ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ. ವಿಶೇಷ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        prevention:
            "ಸರಿಯಾದ ನೀರಾವರಿ, ಪೋಷಕಾಂಶ ಮತ್ತು ಕೀಟ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಮುಂದುವರಿಸಿ.",
    },
};

// =========================================================
// FORMAT DISEASE NAME
// =========================================================

const formatDiseaseName = (name) => {
    if (!name) {
        return "";
    }

    return name
        .replace(/_/g, " ")
        .replace(/\s+/g, " ")
        .trim();
};

// =========================================================
// WAIT FOR VIDEO ELEMENT
// =========================================================

const waitForVideoElement = (videoRef, timeout = 10000) => {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();

        const check = () => {
            if (videoRef.current) {
                resolve(videoRef.current);
                return;
            }

            if (Date.now() - startTime >= timeout) {
                reject(
                    new Error(
                        "Video element did not become available."
                    )
                );
                return;
            }

            requestAnimationFrame(check);
        };

        check();
    });
};

// =========================================================
// WAIT FOR VIDEO TO ACTUALLY BECOME READY
// =========================================================

const waitForVideoReady = (video, timeout = 10000) => {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();

        const check = () => {
            if (
                video.readyState >= 2 &&
                video.videoWidth > 0 &&
                video.videoHeight > 0
            ) {
                resolve();
                return;
            }

            if (Date.now() - startTime >= timeout) {
                reject(
                    new Error(
                        "Camera video did not become ready."
                    )
                );
                return;
            }

            setTimeout(check, 100);
        };

        check();
    });
};

// =========================================================
// COMPONENT
// =========================================================

const PlantDisease = () => {
    const [language, setLanguage] = useState("en");

    const [selectedImage, setSelectedImage] = useState(null);
    const [previewUrl, setPreviewUrl] = useState("");

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // Camera state
    const [cameraOpen, setCameraOpen] = useState(false);
    const [cameraLoading, setCameraLoading] = useState(false);
    const [cameraReady, setCameraReady] = useState(false);
    const [capturedPhoto, setCapturedPhoto] = useState(null);

    const fileInputRef = useRef(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null);

    // Used to cancel an old camera request
    const cameraRequestRef = useRef(0);

    const t = TEXT[language];

    // =====================================================
    // STOP CAMERA
    // =====================================================

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current
                .getTracks()
                .forEach((track) => {
                    track.stop();
                });

            streamRef.current = null;
        }

        if (videoRef.current) {
            videoRef.current.pause();
            videoRef.current.srcObject = null;
        }

        setCameraReady(false);
        setCameraLoading(false);
    };

    // =====================================================
    // CLEAN CAMERA WHEN PAGE CLOSES
    // =====================================================

    useEffect(() => {
        return () => {
            cameraRequestRef.current += 1;

            if (streamRef.current) {
                streamRef.current
                    .getTracks()
                    .forEach((track) => {
                        track.stop();
                    });

                streamRef.current = null;
            }

            if (videoRef.current) {
                videoRef.current.pause();
                videoRef.current.srcObject = null;
            }
        };
    }, []);

    // =====================================================
    // CLEAN PREVIEW URL
    // =====================================================

    useEffect(() => {
        return () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        };
    }, [previewUrl]);

    // =====================================================
    // OPEN CAMERA
    // =====================================================

    const handleOpenCamera = () => {
        const requestId =
            cameraRequestRef.current + 1;

        cameraRequestRef.current = requestId;

        setError("");
        setResult(null);
        setCapturedPhoto(null);
        setCameraReady(false);
        setCameraLoading(true);
        setCameraOpen(true);
    };

    // =====================================================
    // START CAMERA
    // =====================================================

    useEffect(() => {
        if (!cameraOpen || capturedPhoto) {
            return;
        }

        const requestId =
            cameraRequestRef.current;

        let cancelled = false;
        let currentStream = null;

        const startCamera = async () => {
            try {
                setCameraLoading(true);
                setCameraReady(false);

                if (!navigator.mediaDevices?.getUserMedia) {
                    throw new Error(
                        t.cameraNotSupported
                    );
                }

                /*
                 * IMPORTANT:
                 * The video element is now rendered even
                 * while cameraLoading is true.
                 */
                const video =
                    await waitForVideoElement(
                        videoRef
                    );

                if (
                    cancelled ||
                    requestId !==
                        cameraRequestRef.current
                ) {
                    return;
                }

                console.log(
                    "VIDEO ELEMENT FOUND"
                );

                let stream;

                try {
                    stream =
                        await navigator.mediaDevices.getUserMedia(
                            {
                                video: {
                                    facingMode: {
                                        ideal: "environment",
                                    },
                                    width: {
                                        ideal: 1280,
                                    },
                                    height: {
                                        ideal: 720,
                                    },
                                },
                                audio: false,
                            }
                        );
                } catch (firstError) {
                    console.warn(
                        "Preferred camera constraints failed:",
                        firstError
                    );

                    if (
                        firstError?.name ===
                            "NotAllowedError" ||
                        firstError?.name ===
                            "SecurityError"
                    ) {
                        throw firstError;
                    }

                    // Fallback for desktop cameras
                    stream =
                        await navigator.mediaDevices.getUserMedia(
                            {
                                video: true,
                                audio: false,
                            }
                        );
                }

                currentStream = stream;

                if (
                    cancelled ||
                    requestId !==
                        cameraRequestRef.current
                ) {
                    stream
                        .getTracks()
                        .forEach((track) =>
                            track.stop()
                        );

                    return;
                }

                streamRef.current = stream;

                // Attach stream to video
                video.srcObject = stream;
                video.muted = true;
                video.autoplay = true;
                video.playsInline = true;

                video.setAttribute(
                    "autoplay",
                    ""
                );

                video.setAttribute(
                    "playsinline",
                    ""
                );

                video.setAttribute(
                    "muted",
                    ""
                );

                console.log(
                    "CAMERA STREAM ATTACHED"
                );

                // Wait for metadata
                await new Promise(
                    (resolve, reject) => {
                        const timeout =
                            setTimeout(() => {
                                cleanup();

                                reject(
                                    new Error(
                                        t.cameraNotReady
                                    )
                                );
                            }, 10000);

                        const cleanup = () => {
                            clearTimeout(
                                timeout
                            );

                            video.removeEventListener(
                                "loadedmetadata",
                                handleMetadata
                            );
                        };

                        const handleMetadata =
                            () => {
                                cleanup();
                                resolve();
                            };

                        if (
                            video.readyState >=
                                1 &&
                            video.videoWidth >
                                0
                        ) {
                            cleanup();
                            resolve();
                        } else {
                            video.addEventListener(
                                "loadedmetadata",
                                handleMetadata
                            );
                        }
                    }
                );

                if (
                    cancelled ||
                    requestId !==
                        cameraRequestRef.current
                ) {
                    return;
                }

                await video.play();

                if (
                    cancelled ||
                    requestId !==
                        cameraRequestRef.current
                ) {
                    return;
                }

                console.log(
                    "VIDEO PLAY STARTED"
                );

                // Wait for actual dimensions/frame
                await waitForVideoReady(
                    video
                );

                if (
                    cancelled ||
                    requestId !==
                        cameraRequestRef.current
                ) {
                    return;
                }

                console.log(
                    "CAMERA FULLY READY:",
                    {
                        readyState:
                            video.readyState,
                        videoWidth:
                            video.videoWidth,
                        videoHeight:
                            video.videoHeight,
                        trackState:
                            stream
                                .getVideoTracks()[0]
                                ?.readyState,
                    }
                );

                setCameraReady(true);
                setCameraLoading(false);
            } catch (cameraError) {
                console.error(
                    "CAMERA ERROR:",
                    cameraError
                );

                if (
                    cancelled ||
                    requestId !==
                        cameraRequestRef.current
                ) {
                    if (currentStream) {
                        currentStream
                            .getTracks()
                            .forEach((track) =>
                                track.stop()
                            );
                    }

                    return;
                }

                if (currentStream) {
                    currentStream
                        .getTracks()
                        .forEach((track) =>
                            track.stop()
                        );
                }

                streamRef.current = null;

                setCameraReady(false);
                setCameraLoading(false);
                setCameraOpen(false);

                if (
                    cameraError?.name ===
                    "NotAllowedError"
                ) {
                    setError(
                        t.cameraPermission
                    );
                } else if (
                    cameraError?.name ===
                    "NotFoundError"
                ) {
                    setError(t.noCamera);
                } else if (
                    cameraError?.name ===
                    "NotReadableError"
                ) {
                    setError(t.cameraBusy);
                } else if (
                    cameraError?.name ===
                    "SecurityError"
                ) {
                    setError(
                        t.cameraPermission
                    );
                } else {
                    setError(
                        cameraError?.message ||
                            t.cameraNotSupported
                    );
                }
            }
        };

        startCamera();

        return () => {
            cancelled = true;

            if (currentStream) {
                currentStream
                    .getTracks()
                    .forEach((track) =>
                        track.stop()
                    );
            }
        };
    }, [cameraOpen, capturedPhoto]);

    // =====================================================
    // CLOSE CAMERA
    // =====================================================

    const handleCloseCamera = () => {
        cameraRequestRef.current += 1;

        stopCamera();

        setCameraOpen(false);
        setCapturedPhoto(null);
    };

    // =====================================================
    // CAPTURE PHOTO
    // =====================================================

    const handleCapturePhoto = () => {
        const video = videoRef.current;
        const canvas = canvasRef.current;

        if (
            !cameraReady ||
            !video ||
            !canvas
        ) {
            setError(t.cameraNotReady);
            return;
        }

        if (
            video.readyState < 2 ||
            video.videoWidth <= 0 ||
            video.videoHeight <= 0
        ) {
            setError(t.cameraNotReady);
            return;
        }

        const width = video.videoWidth;
        const height = video.videoHeight;

        canvas.width = width;
        canvas.height = height;

        const context =
            canvas.getContext("2d");

        if (!context) {
            setError(t.error);
            return;
        }

        context.drawImage(
            video,
            0,
            0,
            width,
            height
        );

        const dataUrl =
            canvas.toDataURL(
                "image/jpeg",
                0.9
            );

        if (
            !dataUrl ||
            dataUrl === "data:,"
        ) {
            setError(t.cameraNotReady);
            return;
        }

        console.log(
            "PHOTO CAPTURED:",
            {
                width,
                height,
            }
        );

        setCapturedPhoto(dataUrl);
        setError("");

        stopCamera();
    };

    // =====================================================
    // CONVERT CAPTURED PHOTO TO FILE
    // =====================================================

    const dataUrlToFile = (
        dataUrl,
        filename
    ) => {
        const parts =
            dataUrl.split(",");

        const mime =
            parts[0].match(
                /:(.*?);/
            )?.[1] ||
            "image/jpeg";

        const binary =
            atob(parts[1]);

        const array =
            new Uint8Array(
                binary.length
            );

        for (
            let i = 0;
            i < binary.length;
            i++
        ) {
            array[i] =
                binary.charCodeAt(i);
        }

        return new File(
            [array],
            filename,
            {
                type: mime,
            }
        );
    };

    // =====================================================
    // USE CAPTURED PHOTO
    // =====================================================

    const handleUseCapturedPhoto = () => {
        if (!capturedPhoto) {
            return;
        }

        const file =
            dataUrlToFile(
                capturedPhoto,
                `plant-leaf-${Date.now()}.jpg`
            );

        if (
            file.size >
            5 * 1024 * 1024
        ) {
            setError(
                t.capturedTooLarge
            );
            return;
        }

        if (previewUrl) {
            URL.revokeObjectURL(
                previewUrl
            );
        }

        const url =
            URL.createObjectURL(
                file
            );

        setSelectedImage(file);
        setPreviewUrl(url);
        setResult(null);
        setError("");
        setCapturedPhoto(null);
        setCameraOpen(false);
        setCameraReady(false);
    };

    // =====================================================
    // RETAKE PHOTO
    // =====================================================

    const handleRetakePhoto = () => {
        cameraRequestRef.current += 1;

        stopCamera();

        setCapturedPhoto(null);
        setError("");
        setCameraReady(false);
        setCameraLoading(true);
        setCameraOpen(true);
    };

    // =====================================================
    // IMAGE SELECTION
    // =====================================================

    const handleImageChange = (
        event
    ) => {
        const file =
            event.target.files?.[0];

        if (!file) {
            return;
        }

        setError("");
        setResult(null);

        if (
            !file.type ||
            !file.type.startsWith(
                "image/"
            )
        ) {
            setError(
                language === "kn"
                    ? "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ."
                    : "Please select a valid image file."
            );

            return;
        }

        const maxSize =
            5 * 1024 * 1024;

        if (file.size > maxSize) {
            setError(
                language === "kn"
                    ? "ಚಿತ್ರದ ಗಾತ್ರವು 5 MB ಗಿಂತ ಕಡಿಮೆ ಇರಬೇಕು."
                    : "Image size must be less than 5 MB."
            );

            return;
        }

        if (previewUrl) {
            URL.revokeObjectURL(
                previewUrl
            );
        }

        const url =
            URL.createObjectURL(
                file
            );

        setSelectedImage(file);
        setPreviewUrl(url);
    };

    // =====================================================
    // REMOVE IMAGE
    // =====================================================

    const handleRemoveImage = () => {
        cameraRequestRef.current += 1;

        if (previewUrl) {
            URL.revokeObjectURL(
                previewUrl
            );
        }

        stopCamera();

        setSelectedImage(null);
        setPreviewUrl("");
        setCapturedPhoto(null);
        setResult(null);
        setError("");
        setCameraOpen(false);
        setCameraReady(false);

        if (fileInputRef.current) {
            fileInputRef.current.value =
                "";
        }
    };

    // =====================================================
    // PREDICT DISEASE
    // =====================================================

    const handlePrediction =
        async () => {
            if (!selectedImage) {
                setError(
                    t.uploadFirst
                );
                return;
            }

            setLoading(true);
            setError("");
            setResult(null);

            try {
                const data =
                    await predictPlantDisease(
                        selectedImage
                    );

                if (!data?.success) {
                    throw new Error(
                        "Disease prediction failed."
                    );
                }

                setResult(data);
            } catch (
                predictionError
            ) {
                console.error(
                    "Plant Disease Prediction Error:",
                    predictionError
                );

                const backendMessage =
                    predictionError
                        ?.response
                        ?.data
                        ?.detail;

                setError(
                    backendMessage ||
                        predictionError?.message ||
                        t.error
                );
            } finally {
                setLoading(false);
            }
        };

    // =====================================================
    // GET DISPLAY DISEASE NAME
    // =====================================================

    const getDiseaseName = () => {
        if (!result?.disease) {
            return "";
        }

        const formatted =
            formatDiseaseName(
                result.disease
            );

        if (language === "kn") {
            return (
                KANNADA_DISEASE_NAMES[
                    formatted
                ] ||
                formatted
            );
        }

        return formatted;
    };

    // =====================================================
    // GET DISPLAY CROP NAME
    // =====================================================

    const getCropName = () => {
        if (!result?.crop) {
            return "";
        }

        const crop =
            formatDiseaseName(
                result.crop
            );

        if (language === "kn") {
            return (
                KANNADA_CROP_NAMES[
                    crop
                ] ||
                crop
            );
        }

        return crop;
    };

    // =====================================================
    // GET TREATMENT
    // =====================================================

    const getTreatment = () => {
        if (!result?.treatment) {
            return "";
        }

        if (language === "kn") {
            const disease =
                formatDiseaseName(
                    result.disease
                );

            if (
                KANNADA_GUIDANCE[
                    disease
                ]?.treatment
            ) {
                return (
                    KANNADA_GUIDANCE[
                        disease
                    ].treatment
                );
            }
        }

        return result.treatment;
    };

    // =====================================================
    // GET PREVENTION
    // =====================================================

    const getPrevention = () => {
        if (!result?.prevention) {
            return "";
        }

        if (language === "kn") {
            const disease =
                formatDiseaseName(
                    result.disease
                );

            if (
                KANNADA_GUIDANCE[
                    disease
                ]?.prevention
            ) {
                return (
                    KANNADA_GUIDANCE[
                        disease
                    ].prevention
                );
            }
        }

        return result.prevention;
    };

    // =====================================================
    // HEALTH STATUS
    // =====================================================

    const isHealthy =
        result &&
        result.disease &&
        result.disease
            .toLowerCase()
            .includes("healthy");

    // =====================================================
    // RENDER
    // =====================================================

    return (
        <div
            className="plant-disease-page"
            lang={
                language === "kn"
                    ? "kn"
                    : "en"
            }
        >
            {/* HEADER */}

            <header className="disease-header">
                <div className="disease-header-left">
                    <Link
                        to="/dashboard"
                        className="disease-back-button"
                    >
                        {t.backDashboard}
                    </Link>
                </div>

                <div className="disease-language-buttons">
                    <button
                        type="button"
                        className={
                            language === "en"
                                ? "language-btn active"
                                : "language-btn"
                        }
                        onClick={() =>
                            setLanguage("en")
                        }
                    >
                        English
                    </button>

                    <button
                        type="button"
                        className={
                            language === "kn"
                                ? "language-btn active"
                                : "language-btn"
                        }
                        onClick={() =>
                            setLanguage("kn")
                        }
                    >
                        ಕನ್ನಡ
                    </button>
                </div>
            </header>

            {/* MAIN */}

            <main className="disease-main">
                <section className="disease-hero">
                    <div className="disease-hero-icon">
                        🌿
                    </div>

                    <div>
                        <h1>
                            {t.title}
                        </h1>

                        <p>
                            {t.subtitle}
                        </p>
                    </div>
                </section>

                <div className="disease-grid">
                    {/* UPLOAD / CAMERA CARD */}

                    <section className="disease-card upload-card">
                        <div className="card-title-row">
                            <div className="card-icon">
                                📷
                            </div>

                            <div>
                                <h2>
                                    {t.uploadTitle}
                                </h2>

                                <p>
                                    {t.uploadDescription}
                                </p>
                            </div>
                        </div>

                        {/* CAMERA */}

                        {cameraOpen && (
                            <div className="camera-container">
                                <div className="camera-header">
                                    <strong>
                                        📷{" "}
                                        {t.useCamera}
                                    </strong>

                                    <button
                                        type="button"
                                        className="camera-secondary-btn"
                                        onClick={
                                            handleCloseCamera
                                        }
                                    >
                                        ✕{" "}
                                        {
                                            t.closeCamera
                                        }
                                    </button>
                                </div>

                                {/*
                                 * IMPORTANT FIX:
                                 * Video is ALWAYS mounted while camera is open.
                                 * Loading is now an overlay instead of replacing
                                 * the video element.
                                 */}

                                {!capturedPhoto && (
                                    <div className="camera-preview-wrapper">
                                        <video
                                            ref={
                                                videoRef
                                            }
                                            className="camera-video"
                                            autoPlay
                                            playsInline
                                            muted
                                        />

                                        <div className="camera-guide">
                                            <span>
                                                {
                                                    t.cameraReady
                                                }
                                            </span>
                                        </div>

                                        {cameraLoading && (
                                            <div className="camera-loading">
                                                <span className="spinner"></span>

                                                <p>
                                                    {
                                                        t.cameraStarting
                                                    }
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {capturedPhoto && (
                                    <div className="camera-preview-wrapper">
                                        <img
                                            src={
                                                capturedPhoto
                                            }
                                            alt={
                                                t.capturedPhoto
                                            }
                                            className="camera-captured-image"
                                        />
                                    </div>
                                )}

                                <div className="camera-actions">
                                    {!capturedPhoto ? (
                                        <button
                                            type="button"
                                            className="capture-btn"
                                            onClick={
                                                handleCapturePhoto
                                            }
                                            disabled={
                                                cameraLoading ||
                                                !cameraReady
                                            }
                                        >
                                            📸{" "}
                                            {
                                                t.capturePhoto
                                            }
                                        </button>
                                    ) : (
                                        <>
                                            <button
                                                type="button"
                                                className="secondary-btn"
                                                onClick={
                                                    handleRetakePhoto
                                                }
                                            >
                                                🔄{" "}
                                                {
                                                    t.retakePhoto
                                                }
                                            </button>

                                            <button
                                                type="button"
                                                className="predict-btn"
                                                onClick={
                                                    handleUseCapturedPhoto
                                                }
                                            >
                                                ✅{" "}
                                                {
                                                    t.usePhoto
                                                }
                                            </button>
                                        </>
                                    )}
                                </div>

                                <canvas
                                    ref={
                                        canvasRef
                                    }
                                    hidden
                                />
                            </div>
                        )}

                        {/* IMAGE PREVIEW */}

                        {!cameraOpen &&
                            previewUrl && (
                                <div className="image-preview-container">
                                    <img
                                        src={
                                            previewUrl
                                        }
                                        alt={
                                            language ===
                                            "kn"
                                                ? "ಆಯ್ಕೆಮಾಡಿದ ಸಸ್ಯದ ಎಲೆ"
                                                : "Selected plant leaf"
                                        }
                                        className="plant-preview-image"
                                    />

                                    <div className="image-actions">
                                        <button
                                            type="button"
                                            className="secondary-btn"
                                            onClick={() =>
                                                fileInputRef.current?.click()
                                            }
                                        >
                                            🔄{" "}
                                            {
                                                t.changeImage
                                            }
                                        </button>

                                        <button
                                            type="button"
                                            className="remove-btn"
                                            onClick={
                                                handleRemoveImage
                                            }
                                        >
                                            🗑️{" "}
                                            {
                                                t.removeImage
                                            }
                                        </button>
                                    </div>
                                </div>
                            )}

                        {/* UPLOAD / CAMERA OPTIONS */}

                        {!cameraOpen &&
                            !previewUrl && (
                                <div className="disease-input-options">
                                    <button
                                        type="button"
                                        className="upload-zone"
                                        onClick={() =>
                                            fileInputRef.current?.click()
                                        }
                                    >
                                        <div className="upload-icon">
                                            🌱
                                        </div>

                                        <strong>
                                            {
                                                t.chooseImage
                                            }
                                        </strong>

                                        <span>
                                            {
                                                t.supported
                                            }
                                        </span>
                                    </button>

                                    <button
                                        type="button"
                                        className="camera-zone"
                                        onClick={
                                            handleOpenCamera
                                        }
                                    >
                                        <div className="upload-icon">
                                            📸
                                        </div>

                                        <strong>
                                            {
                                                t.useCamera
                                            }
                                        </strong>

                                        <span>
                                            {
                                                t.cameraDescription
                                            }
                                        </span>
                                    </button>
                                </div>
                            )}

                        {/* CAMERA BUTTON WITH SELECTED IMAGE */}

                        {!cameraOpen &&
                            previewUrl && (
                                <button
                                    type="button"
                                    className="camera-secondary-btn"
                                    onClick={
                                        handleOpenCamera
                                    }
                                >
                                    📸{" "}
                                    {
                                        t.useCamera
                                    }
                                </button>
                            )}

                        <input
                            ref={
                                fileInputRef
                            }
                            type="file"
                            accept="image/png,image/jpeg,image/jpg"
                            onChange={
                                handleImageChange
                            }
                            hidden
                        />

                        {/* PREDICT BUTTON */}

                        <button
                            type="button"
                            className="predict-btn"
                            disabled={
                                !selectedImage ||
                                loading ||
                                cameraOpen
                            }
                            onClick={
                                handlePrediction
                            }
                        >
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    {
                                        t.detecting
                                    }
                                </>
                            ) : (
                                <>
                                    🔍{" "}
                                    {
                                        t.predict
                                    }
                                </>
                            )}
                        </button>

                        {/* ERROR */}

                        {error && (
                            <div className="disease-error">
                                ⚠️ {error}
                            </div>
                        )}
                    </section>

                    {/* RESULT CARD */}

                    <section className="disease-card result-card">
                        <div className="card-title-row">
                            <div className="card-icon">
                                🧪
                            </div>

                            <div>
                                <h2>
                                    {
                                        t.resultTitle
                                    }
                                </h2>

                                <p>
                                    {result
                                        ? isHealthy
                                            ? t.healthy
                                            : t.diseaseDetected
                                        : t.noResult}
                                </p>
                            </div>
                        </div>

                        {result ? (
                            <div className="result-content">
                                {/* MAIN RESULT */}

                                <div
                                    className={
                                        isHealthy
                                            ? "status-box healthy"
                                            : "status-box disease"
                                    }
                                >
                                    <div className="status-icon">
                                        {isHealthy
                                            ? "🌿"
                                            : "🦠"}
                                    </div>

                                    <div>
                                        <span>
                                            {
                                                t.disease
                                            }
                                        </span>

                                        <strong>
                                            {
                                                getDiseaseName()
                                            }
                                        </strong>
                                    </div>
                                </div>

                                {/* BASIC INFORMATION */}

                                <div className="result-info-grid">
                                    <div className="info-box">
                                        <span>
                                            🌱{" "}
                                            {
                                                t.crop
                                            }
                                        </span>

                                        <strong>
                                            {
                                                getCropName()
                                            }
                                        </strong>
                                    </div>

                                    <div className="info-box">
                                        <span>
                                            📊{" "}
                                            {
                                                t.confidence
                                            }
                                        </span>

                                        <strong>
                                            {Number(
                                                result.confidence
                                            ).toFixed(
                                                2
                                            )}
                                            %
                                        </strong>
                                    </div>
                                </div>

                                {/* CONFIDENCE BAR */}

                                <div className="confidence-section">
                                    <div className="confidence-header">
                                        <span>
                                            {
                                                t.confidence
                                            }
                                        </span>

                                        <strong>
                                            {Number(
                                                result.confidence
                                            ).toFixed(
                                                2
                                            )}
                                            %
                                        </strong>
                                    </div>

                                    <div className="confidence-bar">
                                        <div
                                            className="confidence-fill"
                                            style={{
                                                width: `${Math.min(
                                                    Math.max(
                                                        Number(
                                                            result.confidence
                                                        ) ||
                                                            0,
                                                        0
                                                    ),
                                                    100
                                                )}%`,
                                            }}
                                        />
                                    </div>
                                </div>

                                {/* TREATMENT */}

                                <div className="guidance-box treatment-box">
                                    <div className="guidance-icon">
                                        💊
                                    </div>

                                    <div>
                                        <h3>
                                            {
                                                t.treatment
                                            }
                                        </h3>

                                        <p>
                                            {
                                                getTreatment()
                                            }
                                        </p>
                                    </div>
                                </div>

                                {/* PREVENTION */}

                                <div className="guidance-box prevention-box">
                                    <div className="guidance-icon">
                                        🛡️
                                    </div>

                                    <div>
                                        <h3>
                                            {
                                                t.prevention
                                            }
                                        </h3>

                                        <p>
                                            {
                                                getPrevention()
                                            }
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="empty-result">
                                <div className="empty-result-icon">
                                    🌱
                                </div>

                                <p>
                                    {
                                        t.noResult
                                    }
                                </p>
                            </div>
                        )}
                    </section>
                </div>

                {/* MODEL INFORMATION */}

                <section className="disease-card model-card">
                    <div className="card-title-row">
                        <div className="card-icon">
                            🤖
                        </div>

                        <div>
                            <h2>
                                {
                                    t.modelInformation
                                }
                            </h2>

                            <p>
                                MobileNetV3-Small
                            </p>
                        </div>
                    </div>

                    <div className="model-info-grid">
                        <div className="model-info-box">
                            <span>
                                🤖{" "}
                                {t.model}
                            </span>

                            <strong>
                                {result?.model ||
                                    "MobileNetV3-Small"}
                            </strong>
                        </div>

                        <div className="model-info-box">
                            <span>
                                📈{" "}
                                {
                                    t.accuracy
                                }
                            </span>

                            <strong>
                                {result?.model_accuracy
                                    ? `${Number(
                                          result.model_accuracy
                                      ).toFixed(
                                          2
                                      )}%`
                                    : "92.37%"}
                            </strong>
                        </div>

                        <div className="model-info-box">
                            <span>
                                🖼️{" "}
                                {
                                    t.datasetImages
                                }
                            </span>

                            <strong>
                                {result?.dataset_images_used ||
                                    "5,700"}
                            </strong>
                        </div>

                        <div className="model-info-box">
                            <span>
                                🔢{" "}
                                {t.classes}
                            </span>

                            <strong>
                                {result?.total_classes ||
                                    "38"}
                            </strong>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
};

export default PlantDisease;