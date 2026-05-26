import cv2
import numpy as np

def hide_image(base_image_path, encrypted_target_array):
    """Hides the target into the lowest 2 bits of the base image with a dynamic size header."""
    base_img = cv2.imread(base_image_path)
    
    if base_img is None:
        raise ValueError("Base image not found.")
        
    h_t, w_t, _ = encrypted_target_array.shape
    
    # 1. Prepare Header (16 bits for height, 16 bits for width = 32 bits total)
    # Using 2-bit LSB, 32 bits requires 16 chunks to store
    header_bits = (np.uint32(h_t) << 16) | np.uint32(w_t)
    header_chunks = np.zeros(16, dtype=np.uint8)
    for i in range(16):
        header_chunks[i] = (header_bits >> ((15 - i) * 2)) & 0x03
        
    # 2. Prepare Target Data
    target_flat = encrypted_target_array.flatten()
    chunks = np.zeros((len(target_flat), 4), dtype=np.uint8)
    chunks[:, 0] = (target_flat >> 6) & 0x03
    chunks[:, 1] = (target_flat >> 4) & 0x03
    chunks[:, 2] = (target_flat >> 2) & 0x03
    chunks[:, 3] = target_flat & 0x03
    target_chunks = chunks.flatten()
    
    # 3. Capacity Check
    base_flat = base_img.flatten()
    total_required = len(header_chunks) + len(target_chunks)
    
    if len(base_flat) < total_required:
        raise ValueError(f"Base image is too small. Needs to be at least {total_required // 3} pixels.")
        
    # 4. Embed Header and Data
    # Clear the bottom 2 bits and embed the header
    base_flat[0:16] = (base_flat[0:16] & 0xFC) | header_chunks
    # Clear the bottom 2 bits and embed the target data
    base_flat[16:16 + len(target_chunks)] = (base_flat[16:16 + len(target_chunks)] & 0xFC) | target_chunks
    
    # Reshape back to original base image dimensions
    stego_img = base_flat.reshape(base_img.shape)
    
    return stego_img

def extract_image(stego_image_path):
    """Reads the dynamic header and extracts the exact dimensions of the hidden target."""
    stego_img = cv2.imread(stego_image_path)
    
    if stego_img is None:
        raise ValueError("Stego image not found.")
        
    stego_flat = stego_img.flatten()
    
    # 1. Extract Header (First 16 chunks)
    header_chunks = stego_flat[0:16] & 0x03
    header_bits = np.uint32(0)
    for i in range(16):
        header_bits |= (np.uint32(header_chunks[i]) << ((15 - i) * 2))
        
    h_t = int(header_bits >> 16)
    w_t = int(header_bits & 0xFFFF)
    
    # 2. Calculate Data Bounds
    target_elements = h_t * w_t * 3
    total_chunks = target_elements * 4
    
    # Security / Corruption check
    if 16 + total_chunks > len(stego_flat):
        raise ValueError("Corrupted Stego Image: Header declares a size larger than the image capacity.")
        
    # 3. Extract Target Data
    target_chunks_flat = stego_flat[16:16 + total_chunks] & 0x03
    chunks = target_chunks_flat.reshape(-1, 4)
    
    target_flat = (chunks[:, 0] << 6) | (chunks[:, 1] << 4) | (chunks[:, 2] << 2) | chunks[:, 3]
    target_img = target_flat.reshape(h_t, w_t, 3)
    
    return target_img