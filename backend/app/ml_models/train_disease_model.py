import json
import random
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image


# ============================================================
# PLANT DISEASE DETECTION MODEL
# MobileNetV3-Small + Transfer Learning
# ============================================================


# ============================================================
# PATH CONFIGURATION
# ============================================================

# train_disease_model.py
#       ↓ parents[0] = ml_models
#       ↓ parents[1] = app
#       ↓ parents[2] = backend
BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = (
    BASE_DIR
    / "dataset"
    / "PlantVillage"
    / "raw"
    / "color"
)

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
# TRAINING CONFIGURATION
# ============================================================

IMAGE_SIZE = 224

BATCH_SIZE = 32

# Maximum images used from each disease class.
# This keeps training practical on CPU.
MAX_IMAGES_PER_CLASS = 300

EPOCHS = 5

LEARNING_RATE = 0.001

VALIDATION_SPLIT = 0.20

RANDOM_SEED = 42

NUM_WORKERS = 0

DEVICE = torch.device("cpu")


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(RANDOM_SEED)

torch.manual_seed(RANDOM_SEED)


# ============================================================
# DATASET CLASS
# ============================================================

class PlantDiseaseDataset(Dataset):

    def __init__(self, samples, transform=None):

        self.samples = samples

        self.transform = transform

    def __len__(self):

        return len(self.samples)

    def __getitem__(self, index):

        image_path, label = self.samples[index]

        try:

            image = Image.open(
                image_path
            ).convert("RGB")

        except Exception as error:

            print(
                f"\nWarning: Could not read image:"
                f"\n{image_path}"
                f"\nError: {error}"
            )

            # Try the next image
            new_index = (
                index + 1
            ) % len(self.samples)

            image_path, label = (
                self.samples[new_index]
            )

            image = Image.open(
                image_path
            ).convert("RGB")

        if self.transform:

            image = self.transform(image)

        return image, label


# ============================================================
# IMAGE TRANSFORMS
# ============================================================

train_transform = transforms.Compose([

    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),

    transforms.RandomHorizontalFlip(
        p=0.5
    ),

    transforms.RandomRotation(
        10
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
    ),
])


validation_transform = transforms.Compose([

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
    ),
])


# ============================================================
# COLLECT DATASET
# ============================================================

def collect_samples():

    print("\nChecking dataset...")

    print(
        f"Dataset path:\n{DATASET_DIR}"
    )

    if not DATASET_DIR.exists():

        raise FileNotFoundError(
            "\nDataset directory not found:\n"
            f"{DATASET_DIR}\n\n"
            "Expected structure:\n"
            "backend/dataset/PlantVillage/raw/color/"
        )

    class_names = sorted([

        folder.name

        for folder in DATASET_DIR.iterdir()

        if folder.is_dir()

    ])

    if not class_names:

        raise RuntimeError(
            f"No disease classes found in:\n"
            f"{DATASET_DIR}"
        )

    print(
        f"\nClasses found: "
        f"{len(class_names)}"
    )

    samples_by_class = {}

    total_available = 0

    total_used = 0


    # --------------------------------------------------------
    # COLLECT EACH CLASS
    # --------------------------------------------------------

    for class_index, class_name in enumerate(
        class_names
    ):

        class_dir = (
            DATASET_DIR
            / class_name
        )

        image_files = []


        # Search supported image types
        for pattern in [
            "*.jpg",
            "*.JPG",
            "*.jpeg",
            "*.JPEG",
            "*.png",
            "*.PNG"
        ]:

            image_files.extend(
                class_dir.glob(pattern)
            )


        image_files = sorted(
            image_files
        )

        available_count = len(
            image_files
        )

        total_available += (
            available_count
        )


        # Deterministic shuffle
        random_generator = random.Random(
            RANDOM_SEED + class_index
        )

        random_generator.shuffle(
            image_files
        )


        # Limit number of images
        selected_images = (
            image_files[
                :MAX_IMAGES_PER_CLASS
            ]
        )

        used_count = len(
            selected_images
        )

        total_used += used_count


        samples_by_class[
            class_index
        ] = [

            (
                str(image_path),
                class_index
            )

            for image_path
            in selected_images

        ]


        print(
            f"{class_name}: "
            f"{available_count} available "
            f"-> {used_count} used"
        )


    print(
        "\nTotal available images: "
        f"{total_available}"
    )

    print(
        "Total images selected: "
        f"{total_used}"
    )

    return (
        class_names,
        samples_by_class
    )


# ============================================================
# STRATIFIED TRAIN / VALIDATION SPLIT
# ============================================================

def create_split(
    samples_by_class
):

    train_samples = []

    validation_samples = []


    for class_index, samples in (
        samples_by_class.items()
    ):

        # Copy so original list is not modified
        samples = list(samples)


        # Shuffle each class independently
        random_generator = random.Random(
            RANDOM_SEED + class_index
        )

        random_generator.shuffle(
            samples
        )


        validation_count = max(
            1,
            int(
                len(samples)
                * VALIDATION_SPLIT
            )
        )


        validation_part = (
            samples[
                :validation_count
            ]
        )

        train_part = (
            samples[
                validation_count:
            ]
        )


        train_samples.extend(
            train_part
        )

        validation_samples.extend(
            validation_part
        )


    # Shuffle final datasets
    random.Random(
        RANDOM_SEED
    ).shuffle(
        train_samples
    )

    random.Random(
        RANDOM_SEED
    ).shuffle(
        validation_samples
    )


    return (
        train_samples,
        validation_samples
    )


# ============================================================
# CREATE MOBILENETV3-SMALL
# ============================================================

def create_model(
    num_classes
):

    print(
        "\nLoading MobileNetV3-Small..."
    )

    print(
        "Using pretrained ImageNet weights."
    )


    # The weights are already cached after
    # the previous training attempt.
    weights = (
        models.MobileNet_V3_Small_Weights.DEFAULT
    )


    model = (
        models.mobilenet_v3_small(
            weights=weights
        )
    )


    # --------------------------------------------------------
    # FREEZE FEATURE EXTRACTOR
    # --------------------------------------------------------

    for parameter in (
        model.features.parameters()
    ):

        parameter.requires_grad = False


    # --------------------------------------------------------
    # REPLACE FINAL CLASSIFIER
    # --------------------------------------------------------

    input_features = (
        model.classifier[-1]
        .in_features
    )


    model.classifier[-1] = (
        nn.Linear(
            input_features,
            num_classes
        )
    )


    model = model.to(
        DEVICE
    )


    return model


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(
    model,
    train_loader,
    validation_loader,
    criterion,
    optimizer
):

    best_validation_accuracy = 0.0

    best_state = None


    # ========================================================
    # EPOCH LOOP
    # ========================================================

    for epoch in range(
        1,
        EPOCHS + 1
    ):

        print(
            "\n"
            + "=" * 60
        )

        print(
            f"Epoch {epoch}/{EPOCHS}"
        )

        print(
            "=" * 60
        )


        # ====================================================
        # TRAINING
        # ====================================================

        model.train()


        training_loss = 0.0

        training_correct = 0

        training_total = 0


        for batch_index, (
            images,
            labels
        ) in enumerate(
            train_loader
        ):

            images = images.to(
                DEVICE
            )

            labels = labels.to(
                DEVICE
            )


            # Clear gradients
            optimizer.zero_grad()


            # Forward pass
            outputs = model(
                images
            )


            # Calculate loss
            loss = criterion(
                outputs,
                labels
            )


            # Backpropagation
            loss.backward()


            # Update classifier
            optimizer.step()


            # ------------------------------------------------
            # Statistics
            # ------------------------------------------------

            training_loss += (
                loss.item()
                * images.size(0)
            )


            predictions = (
                outputs.argmax(
                    dim=1
                )
            )


            training_correct += (
                (
                    predictions
                    == labels
                )
                .sum()
                .item()
            )


            training_total += (
                labels.size(0)
            )


            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if (
                (batch_index + 1)
                % 25
                == 0
            ):

                print(
                    f"Batch "
                    f"{batch_index + 1}/"
                    f"{len(train_loader)}"
                )


        train_loss = (
            training_loss
            / training_total
        )


        train_accuracy = (
            training_correct
            / training_total
        ) * 100


        # ====================================================
        # VALIDATION
        # ====================================================

        model.eval()


        validation_loss = 0.0

        validation_correct = 0

        validation_total = 0


        with torch.no_grad():

            for (
                images,
                labels
            ) in validation_loader:

                images = images.to(
                    DEVICE
                )

                labels = labels.to(
                    DEVICE
                )


                outputs = model(
                    images
                )


                loss = criterion(
                    outputs,
                    labels
                )


                validation_loss += (
                    loss.item()
                    * images.size(0)
                )


                predictions = (
                    outputs.argmax(
                        dim=1
                    )
                )


                validation_correct += (
                    (
                        predictions
                        == labels
                    )
                    .sum()
                    .item()
                )


                validation_total += (
                    labels.size(0)
                )


        validation_loss = (
            validation_loss
            / validation_total
        )


        validation_accuracy = (
            validation_correct
            / validation_total
        ) * 100


        # ====================================================
        # DISPLAY RESULTS
        # ====================================================

        print("\nResults:")

        print(
            f"Train Loss: "
            f"{train_loss:.4f}"
        )

        print(
            f"Train Accuracy: "
            f"{train_accuracy:.2f}%"
        )

        print(
            f"Validation Loss: "
            f"{validation_loss:.4f}"
        )

        print(
            f"Validation Accuracy: "
            f"{validation_accuracy:.2f}%"
        )


        # ====================================================
        # SAVE BEST STATE
        # ====================================================

        if (
            validation_accuracy
            > best_validation_accuracy
        ):

            best_validation_accuracy = (
                validation_accuracy
            )


            best_state = {

                key: value.cpu().clone()

                for key, value
                in model.state_dict().items()

            }


            print(
                "\n*** New best model ***"
            )


    # ========================================================
    # RESTORE BEST MODEL
    # ========================================================

    if best_state is not None:

        model.load_state_dict(
            best_state
        )


    return (
        best_validation_accuracy
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "PLANT DISEASE MODEL TRAINING"
    )

    print(
        "=" * 60
    )


    print(
        f"Device: {DEVICE}"
    )

    print(
        f"Image size: {IMAGE_SIZE}"
    )

    print(
        f"Batch size: {BATCH_SIZE}"
    )

    print(
        f"Maximum images/class: "
        f"{MAX_IMAGES_PER_CLASS}"
    )

    print(
        f"Epochs: {EPOCHS}"
    )


    # ========================================================
    # COLLECT DATA
    # ========================================================

    (
        class_names,
        samples_by_class
    ) = collect_samples()


    # ========================================================
    # SPLIT DATA
    # ========================================================

    (
        train_samples,
        validation_samples
    ) = create_split(
        samples_by_class
    )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "DATASET SUMMARY"
    )

    print(
        "=" * 60
    )


    print(
        f"Classes: "
        f"{len(class_names)}"
    )

    print(
        f"Training images: "
        f"{len(train_samples)}"
    )

    print(
        f"Validation images: "
        f"{len(validation_samples)}"
    )


    print(
        f"Total used: "
        f"{len(train_samples) + len(validation_samples)}"
    )


    # ========================================================
    # CREATE DATASETS
    # ========================================================

    train_dataset = (
        PlantDiseaseDataset(
            train_samples,
            transform=train_transform
        )
    )


    validation_dataset = (
        PlantDiseaseDataset(
            validation_samples,
            transform=validation_transform
        )
    )


    # ========================================================
    # DATA LOADERS
    # ========================================================

    train_loader = DataLoader(

        train_dataset,

        batch_size=BATCH_SIZE,

        shuffle=True,

        num_workers=NUM_WORKERS,

        pin_memory=False

    )


    validation_loader = DataLoader(

        validation_dataset,

        batch_size=BATCH_SIZE,

        shuffle=False,

        num_workers=NUM_WORKERS,

        pin_memory=False

    )


    # ========================================================
    # CREATE MODEL
    # ========================================================

    model = create_model(
        len(class_names)
    )


    trainable_parameters = sum(

        parameter.numel()

        for parameter
        in model.parameters()

        if parameter.requires_grad

    )


    total_parameters = sum(

        parameter.numel()

        for parameter
        in model.parameters()

    )


    print(
        f"\nTotal parameters: "
        f"{total_parameters:,}"
    )

    print(
        f"Trainable parameters: "
        f"{trainable_parameters:,}"
    )


    # ========================================================
    # LOSS
    # ========================================================

    criterion = (
        nn.CrossEntropyLoss()
    )


    # ========================================================
    # OPTIMIZER
    # ========================================================

    optimizer = torch.optim.Adam(

        filter(
            lambda parameter:
            parameter.requires_grad,

            model.parameters()
        ),

        lr=LEARNING_RATE

    )


    # ========================================================
    # TRAIN
    # ========================================================

    best_accuracy = train_model(

        model,

        train_loader,

        validation_loader,

        criterion,

        optimizer

    )


    # ========================================================
    # CREATE MODEL DIRECTORY
    # ========================================================

    MODEL_DIR.mkdir(

        parents=True,

        exist_ok=True

    )


    # ========================================================
    # SAVE MODEL
    # ========================================================

    print(
        "\nSaving model..."
    )


    torch.save(

        model.state_dict(),

        MODEL_PATH

    )


    # ========================================================
    # SAVE METADATA
    # ========================================================

    metadata = {

        "model":
            "MobileNetV3-Small",

        "framework":
            "PyTorch",

        "num_classes":
            len(class_names),

        "classes":
            class_names,

        "image_size":
            IMAGE_SIZE,

        "dataset_images_used":
            (
                len(train_samples)
                + len(validation_samples)
            ),

        "training_images":
            len(train_samples),

        "validation_images":
            len(validation_samples),

        "max_images_per_class":
            MAX_IMAGES_PER_CLASS,

        "validation_accuracy":
            round(
                best_accuracy,
                2
            ),

        "epochs":
            EPOCHS,

        "batch_size":
            BATCH_SIZE,

        "learning_rate":
            LEARNING_RATE,

        "device":
            "cpu",

        "architecture":
            "MobileNetV3-Small",

        "pretrained":
            True

    }


    with open(

        METADATA_PATH,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            metadata,

            file,

            indent=2,

            ensure_ascii=False

        )


    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "TRAINING COMPLETE"
    )

    print(
        "=" * 60
    )


    print(
        f"Best validation accuracy: "
        f"{best_accuracy:.2f}%"
    )


    print(
        "\nModel saved:"
    )

    print(
        MODEL_PATH
    )


    print(
        "\nMetadata saved:"
    )

    print(
        METADATA_PATH
    )


    print(
        "\nModel classes:"
    )


    for index, class_name in enumerate(
        class_names
    ):

        print(
            f"{index}: {class_name}"
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()