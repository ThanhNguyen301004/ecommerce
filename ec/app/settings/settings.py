import os

CAMERA = {
    'index': 0,  
    'width': 480,
    'height': 640
}

FACE_DETECTION = {
    'scale_factor': 1.3,
    'min_neighbors': 5,
    'min_size': (30, 30)
}

TRAINING = {
    'samples_needed': 100
}

PATHS = {
    'image_dir': 'images',
    'cascade_file': 'haarcascade_frontalface_default.xml',
    'names_file': 'names.json',
    'trainer_file': 'modle.pkl',
    'facenet_model': 'path/to/facenet_keras.h5',
    'embeddings_dir': 'embeddings'
}

