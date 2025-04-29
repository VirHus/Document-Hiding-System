import wave
import os
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from xor_cipher import KEY, xor_decrypt

def extract_document_from_audio(stego_audio, output_folder):
    """Extracts and decrypts a document from a stego audio file."""
    start_time = time.time()
    try:
        # Open the stego audio and read its frames
        with wave.open(stego_audio, "rb") as audio:
            params = audio.getparams()
            frames = bytearray(audio.readframes(audio.getnframes()))
            stego_amplitudes = np.frombuffer(frames, dtype=np.int16)

        # Extract the encrypted data
        extracted_data = bytearray()
        for i in range(0, len(frames), 8):
            byte = 0
            for j in range(8):
                byte |= (frames[i + j] & 1) << j
            extracted_data.append(byte)

        # Decrypt the data
        decrypted_data = xor_decrypt(extracted_data, KEY)

        # Separate file extension
        separator = b"|||"
        if separator in decrypted_data:
            extension_bytes, document_data = decrypted_data.split(separator, 1)
            file_extension = extension_bytes.decode(errors="ignore").strip()
        else:
            return "Error: No file extension found.", None, None, None

        # Generate output paths
        timestamp = str(int(time.time()))
        extracted_filename = f"extracted_document_{timestamp}{file_extension}"
        extracted_doc_path = os.path.join(output_folder, extracted_filename)
        histogram_path = os.path.join(output_folder, f"decode_histogram_{timestamp}.png")

        # Save extracted document
        with open(extracted_doc_path, "wb") as f:
            f.write(document_data)

        # Generate histogram
        plt.figure(figsize=(12, 6))
        plt.hist(stego_amplitudes, bins=100, color='purple', alpha=0.7)
        plt.title('Stego Audio Amplitude Distribution')
        plt.xlabel('Amplitude')
        plt.ylabel('Frequency')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.savefig(histogram_path, dpi=150)
        plt.close()

        elapsed_time = time.time() - start_time

        return (
            f"Success: Document extracted in {elapsed_time:.2f} seconds",
            extracted_doc_path,
            histogram_path,
            elapsed_time
        )

    except Exception as e:
        return f"Error: {e}", None, None, None