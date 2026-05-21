#!/usr/bin/env python3
"""
Interior Vibing — Gemini API Bridge

Models:
  Analysis:   gemini-2.5-flash (vision + text)
  Generation: gemini-3-pro-image-preview (Nano Banana Pro — reasoning-enhanced image gen)

Setup:
  pip install google-genai Pillow
  Put your API key in .env file or: export GEMINI_API_KEY=your_key_here
  Get a key at: https://aistudio.google.com/apikey

Usage:
  python render.py analyze --image room.jpg
  python render.py render --image room.jpg --prompt "detailed design prompt"
  python render.py edit --image room.jpg --prompt "change the bedding to white linen"
"""

import argparse
import os
import sys
import shutil
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────

OUTPUT_DIR = ".stilo-output"
ANALYSIS_MODEL = "gemini-2.5-flash"              # Fast, great at vision understanding
IMAGE_MODEL = "gemini-3-pro-image-preview"        # Nano Banana Pro — best image generation

# ─── Setup ───────────────────────────────────────────────────────────

def ensure_deps():
    """Check dependencies."""
    missing = []
    try:
        from google import genai
    except ImportError:
        missing.append("google-genai")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        sys.exit(1)


def ensure_api_key():
    """Check for Gemini API key. Looks in: 1) .env file  2) environment variable."""
    key = None

    for env_path in [
        Path(__file__).parent.parent / ".env",
        Path.cwd() / ".env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("GEMINI_API_KEY=") and not line.endswith("paste_your_key_here"):
                    key = line.split("=", 1)[1].strip()
                    break
        if key:
            break

    if not key:
        key = os.environ.get("GEMINI_API_KEY")

    if not key:
        print("❌ GEMINI_API_KEY not found.")
        print("")
        print("   Option 1: Edit the .env file in the skill folder")
        print("             Replace 'paste_your_key_here' with your key")
        print("")
        print("   Option 2: Set environment variable")
        print("             export GEMINI_API_KEY=your_key_here")
        print("")
        print("   Get a key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    return key


def ensure_output_dir():
    """Create .stilo-output/ if it doesn't exist."""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    return OUTPUT_DIR


def copy_before_image(image_path: str) -> str:
    """Copy the uploaded image to .stilo-output/before.*"""
    src = Path(image_path)
    if not src.exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)

    dst = Path(OUTPUT_DIR) / f"before{src.suffix}"
    shutil.copy2(src, dst)
    print(f"📷 Before image: {dst}")
    return str(dst)


# ─── Commands ────────────────────────────────────────────────────────

def cmd_analyze(args):
    """
    Analyze a room photo using gemini-2.5-flash.
    Saves analysis to .stilo-output/analysis.txt
    """
    from google import genai
    from PIL import Image

    ensure_output_dir()
    before_path = copy_before_image(args.image)

    client = genai.Client(api_key=ensure_api_key())
    image = Image.open(before_path)

    system = """You are a professional interior designer and architectural assessor.
You analyze rooms with the precision of an architect and the eye of a photographer.
Every observation must be SPECIFIC to THIS room — never generic.

Instead of "hardwood floors" say "medium-warm white oak, ~5-inch planks, satin finish, 
good condition with minor wear paths near entry."

Analyze the photo and provide a structured assessment:

1. ROOM TYPE & SIZE — Type, estimated L×W×ceiling height (use furniture as scale)
2. FLOOR — Material, color tone, plank/tile size, condition (1-5 with reasoning)
3. WALLS — Color (approximate hex), finish, condition, features (molding, texture)
4. NATURAL LIGHT — Window count, estimated orientation (from shadows), quality
5. ARTIFICIAL LIGHT — Fixture types, adequacy, layers
6. FIXED ELEMENTS — Everything that can't easily change (counters, cabinets, tile, built-ins)
7. EXISTING FURNITURE — Each item: style, color, condition, keep/replace/remove recommendation
8. ARCHITECTURAL STYLE — Era, style name, quality tier
9. SPATIAL FLOW — Entry points, primary sightline, focal wall, dead zones, best photo angle
10. BEST ASSET — The single best design feature of this room
11. BIGGEST PROBLEM — The single biggest design issue to address
12. MISSING ESSENTIALS — What the room clearly needs but doesn't have

FORMAT: Clean readable sections with headers. Not JSON."""

    print("🔍 Analyzing room with gemini-2.5-flash...")

    response = client.models.generate_content(
        model=ANALYSIS_MODEL,
        contents=[
            "Analyze this room in full detail for interior design purposes.",
            image,
        ],
        config={
            "system_instruction": system,
            "temperature": 0.3,
        }
    )

    analysis = response.text

    analysis_path = Path(OUTPUT_DIR) / "analysis.txt"
    analysis_path.write_text(analysis)
    print(f"📋 Analysis saved: {analysis_path}")
    print(f"\n{'='*60}\n")
    print(analysis)

    return analysis


def cmd_render(args):
    """
    Generate a redesigned room rendering using gemini-3-pro-image-preview (Nano Banana Pro).
    Saves to .stilo-output/after.png
    """
    from google import genai
    from google.genai import types
    from PIL import Image

    ensure_output_dir()
    before_path = copy_before_image(args.image)
    image = Image.open(before_path)

    client = genai.Client(api_key=ensure_api_key())

    # Build prompt
    parts = [f"""Redesign this room. Keep the existing architecture, windows, and 
fixed elements (floors, counters, built-ins) intact. Transform the furnishings, 
decor, and styling.

DESIGN BRIEF:
{args.prompt}"""]

    if args.purpose:
        parts.append(f"\nPURPOSE: This redesign is for {args.purpose}.")
    if args.style:
        parts.append(f"\nSTYLE DIRECTION: {args.style}.")

    parts.append("""
OUTPUT: A photorealistic interior photograph. Professional real estate photography 
quality. Natural lighting with warm color temperature. Magazine editorial standard.
Camera angle from the doorway at 4-foot height showing full room depth.
The image must look like a REAL photograph, not an AI rendering.""")

    full_prompt = "\n".join(parts)

    # Determine output path and aspect ratio
    output_path = args.output or str(Path(OUTPUT_DIR) / "after.png")
    aspect_ratio = args.aspect_ratio or "4:3"
    resolution = args.resolution or "2K"

    print(f"🎨 Generating rendering with gemini-3-pro-image-preview...")
    print(f"   Resolution: {resolution}, Aspect ratio: {aspect_ratio}")
    print(f"   Prompt: {full_prompt[:150]}...")

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[full_prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                ),
            )
        )
    except Exception as e:
        print(f"⚠️  First attempt error: {e}")
        print("   Retrying with minimal config...")
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[full_prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            )
        )

    # Extract image and text using the official SDK pattern
    image_saved = False
    model_notes = []

    for part in response.parts:
        if part.text is not None:
            model_notes.append(part.text)
        elif part.inline_data is not None:
            # Save using inline_data bytes directly
            import base64
            img_data = part.inline_data.data
            if isinstance(img_data, str):
                img_data = base64.b64decode(img_data)
            Path(output_path).write_bytes(img_data)
            # Get dimensions via PIL
            try:
                pil_img = Image.open(output_path)
                print(f"✅ Rendering saved: {output_path} ({pil_img.size[0]}×{pil_img.size[1]})")
            except Exception:
                print(f"✅ Rendering saved: {output_path}")
            image_saved = True

    if model_notes:
        notes_text = "\n".join(model_notes)
        notes_path = Path(OUTPUT_DIR) / "render_notes.txt"
        notes_path.write_text(notes_text)
        print(f"📝 Model notes: {notes_path}")

    if not image_saved:
        print("⚠️  No image generated. Possible reasons:")
        print("   - Prompt triggered safety filters")
        print("   - Model chose text-only response")
        print("   - Try rephrasing or simplifying the prompt")
        if model_notes:
            print(f"   Model said: {model_notes[0][:200]}")

    return output_path if image_saved else None


def cmd_edit(args):
    """
    Edit specific areas of a room photo using gemini-3-pro-image-preview.
    Saves to .stilo-output/after.png
    """
    from google import genai
    from google.genai import types
    from PIL import Image

    ensure_output_dir()
    before_path = copy_before_image(args.image)
    image = Image.open(before_path)

    client = genai.Client(api_key=ensure_api_key())

    prompt = f"""Edit this room photograph with these specific changes ONLY.
Keep everything else exactly as-is.

CHANGES:
{args.prompt}

The result must look like a real photograph — same lighting, perspective, architecture.
Professional interior photography quality. Only modify what was described."""

    output_path = args.output or str(Path(OUTPUT_DIR) / "after.png")
    aspect_ratio = args.aspect_ratio or "4:3"
    resolution = args.resolution or "2K"

    print(f"✏️  Editing room with gemini-3-pro-image-preview...")

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                ),
            )
        )
    except Exception as e:
        print(f"⚠️  First attempt error: {e}")
        print("   Retrying with minimal config...")
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            )
        )

    image_saved = False
    for part in response.parts:
        if part.text is not None:
            print(f"📝 Note: {part.text[:200]}")
        elif part.inline_data is not None:
            import base64
            img_data = part.inline_data.data
            if isinstance(img_data, str):
                img_data = base64.b64decode(img_data)
            Path(output_path).write_bytes(img_data)
            try:
                pil_img = Image.open(output_path)
                print(f"✅ Edit saved: {output_path} ({pil_img.size[0]}×{pil_img.size[1]})")
            except Exception:
                print(f"✅ Edit saved: {output_path}")
            image_saved = True

    if not image_saved:
        print("⚠️  No image generated. Try rephrasing the edit request.")

    return output_path if image_saved else None


# ─── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Interior Vibing — Gemini-powered room analysis and redesign",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models:
  analyze → gemini-2.5-flash (fast vision understanding)
  render  → gemini-3-pro-image-preview (Nano Banana Pro, best image gen)
  edit    → gemini-3-pro-image-preview

Examples:
  python render.py analyze --image room.jpg
  python render.py render --image room.jpg --prompt "Warm Scandinavian bedroom with white linen bedding, oak nightstands, brass lamps, large abstract art above headboard" --resolution 2K
  python render.py render --image room.jpg --prompt "..." --purpose "airbnb listing" --style "warm scandinavian" --aspect-ratio 4:3
  python render.py edit --image room.jpg --prompt "Replace dated brass fixtures with matte black, add white towels"

All outputs saved to .stilo-output/ in the current directory.
"""
    )
    sub = parser.add_subparsers(dest="command")

    # Analyze
    p1 = sub.add_parser("analyze", help="Analyze a room photo (gemini-2.5-flash)")
    p1.add_argument("--image", required=True, help="Path to room photo")

    # Render
    p2 = sub.add_parser("render", help="Generate redesigned room (gemini-3-pro-image-preview)")
    p2.add_argument("--image", required=True, help="Path to original room photo")
    p2.add_argument("--prompt", required=True, help="Detailed design prompt (80+ words)")
    p2.add_argument("--output", help=f"Output path (default: {OUTPUT_DIR}/after.png)")
    p2.add_argument("--style", help="Style direction, e.g. 'warm scandinavian'")
    p2.add_argument("--purpose", help="Design purpose, e.g. 'airbnb listing'")
    p2.add_argument("--aspect-ratio", default="4:3",
                     help="Image aspect ratio: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 (default: 4:3)")
    p2.add_argument("--resolution", default="2K",
                     help="Output resolution: 1K, 2K, 4K (default: 2K)")

    # Edit
    p3 = sub.add_parser("edit", help="Edit specific areas (gemini-3-pro-image-preview)")
    p3.add_argument("--image", required=True, help="Path to room photo")
    p3.add_argument("--prompt", required=True, help="What to change")
    p3.add_argument("--output", help=f"Output path (default: {OUTPUT_DIR}/after.png)")
    p3.add_argument("--aspect-ratio", default="4:3", help="Aspect ratio (default: 4:3)")
    p3.add_argument("--resolution", default="2K", help="Resolution: 1K, 2K, 4K (default: 2K)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    ensure_deps()

    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "render":
        cmd_render(args)
    elif args.command == "edit":
        cmd_edit(args)


if __name__ == "__main__":
    main()
