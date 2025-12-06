import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils

def generate_proof():
    print("--- Generating Submission Proof ---")

    # 1. Get the Commit Hash
    commit_hash = input("Enter your Git Commit Hash (40 chars): ").strip()
    if len(commit_hash) != 40:
        print("❌ Error: Commit hash must be exactly 40 characters.")
        return

    # 2. Load Student Private Key (To SIGN the hash)
    try:
        with open("student_private.pem", "rb") as f:
            student_private_key = serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        print("❌ Error: student_private.pem not found.")
        return

    # 3. Load Instructor Public Key (To ENCRYPT the signature)
    try:
        with open("instructor_public.pem", "rb") as f:
            instructor_public_key = serialization.load_pem_public_key(f.read())
    except FileNotFoundError:
        print("❌ Error: instructor_public.pem not found. Please download it from your course resources.")
        return

    try:
        # 4. Sign the Commit Hash (RSA-PSS)
        # CRITICAL: We sign the ASCII bytes of the hash string
        message_bytes = commit_hash.encode('utf-8')
        
        signature = student_private_key.sign(
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("✅ Signature generated (RSA-PSS).")

        # 5. Encrypt the Signature (RSA-OAEP)
        encrypted_signature = instructor_public_key.encrypt(
            signature,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("✅ Signature encrypted with Instructor Key.")

        # 6. Encode to Base64 (Single Line)
        final_proof = base64.b64encode(encrypted_signature).decode('utf-8')

        print("\n" + "="*60)
        print("SUBMISSION DATA")
        print("="*60)
        print(f"Commit Hash:         {commit_hash}")
        print("-" * 20)
        print(f"Encrypted Signature: {final_proof}")
        print("="*60)
        
        # Save to file for easy copying
        with open("submission_proof.txt", "w") as f:
            f.write(final_proof)
        print("\nSaved encrypted signature to 'submission_proof.txt'")

    except Exception as e:
        print(f"❌ Error during crypto operations: {e}")

if __name__ == "__main__":
    generate_proof()