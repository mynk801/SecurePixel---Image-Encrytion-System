import numpy as np
import warnings

def generate_henon_sequence(size, x0, y0, a=1.4, b=0.3):
    """Generates a Henon map sequence and returns a deterministic permutation array."""
    x = np.zeros(size, dtype=np.float64)
    y = np.zeros(size, dtype=np.float64)
    x[0], y[0] = x0, y0
    
    # Generate the chaotic sequence with overflow protection
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i in range(1, size):
            nx = 1 - a * x[i-1]**2 + y[i-1]
            ny = b * x[i-1]
            
            if abs(nx) > 1000: nx = nx % 1000
            if abs(ny) > 1000: ny = ny % 1000
                
            x[i] = nx
            y[i] = ny
        
    return np.argsort(x)

def encrypt_image(image_array, x0, y0):
    """Scrambles the image pixels using the Henon map."""
    shape = image_array.shape
    flat_img = image_array.reshape(-1, shape[2])
    
    permutation = generate_henon_sequence(flat_img.shape[0], x0, y0)
    
    encrypted_flat = np.zeros_like(flat_img)
    encrypted_flat[permutation] = flat_img
    
    return encrypted_flat.reshape(shape)

def decrypt_image(encrypted_array, x0, y0):
    """Reverses the scramble to restore the image."""
    shape = encrypted_array.shape
    flat_encrypted = encrypted_array.reshape(-1, shape[2])
    
    # Generate the EXACT same sequence used during encryption
    permutation = generate_henon_sequence(flat_encrypted.shape[0], x0, y0)
    
    # THE FIX: Map the pixels directly back to their original positions
    decrypted_flat = flat_encrypted[permutation]
    
    return decrypted_flat.reshape(shape)