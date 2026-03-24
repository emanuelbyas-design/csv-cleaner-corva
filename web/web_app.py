#!/usr/bin/env python3
import os
import sys
import tempfile
import shutil
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify, send_file, render_template

from detector import detect_provider
from cleaners import NOVCleaner, RigcloudCleaner, PasonCleaner
from cleaners.base import BaseCleaner

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB limit

CLEANER_MAP: dict[str, type[BaseCleaner]] = {
    "NOV": NOVCleaner,
    "Rigcloud": RigcloudCleaner,
    "Pason": PasonCleaner,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():
    """Accept a CSV upload, detect the provider, and return the result."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    tmp_dir = tempfile.mkdtemp()
    try:
        filepath = os.path.join(tmp_dir, file.filename)
        file.save(filepath)
        provider = detect_provider(filepath)
        return jsonify({"provider": provider or "Unknown", "filename": file.filename})
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.route("/clean", methods=["POST"])
def clean():
    """Accept a CSV upload + provider choice, clean it, return the cleaned file."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    provider = request.form.get("provider", "").strip()

    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    tmp_dir = tempfile.mkdtemp()
    try:
        filepath = os.path.join(tmp_dir, file.filename)
        file.save(filepath)

        if not provider or provider == "Auto-detect":
            provider = detect_provider(filepath) or ""

        if provider not in CLEANER_MAP:
            return jsonify({"error": f"Unknown provider: {provider}"}), 400

        cleaner_cls = CLEANER_MAP[provider]
        cleaner = cleaner_cls(filepath)
        result = cleaner.clean()

        base, ext = os.path.splitext(file.filename)

        if len(result.output_paths) == 1:
            return send_file(
                result.output_paths[0],
                as_attachment=True,
                download_name=f"{base}_Corva_Formatted{ext}",
                mimetype="text/csv",
            )

        zip_path = os.path.join(tmp_dir, f"{base}_Corva_Formatted.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in result.output_paths:
                zf.write(p, os.path.basename(p))

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{base}_Corva_Formatted.zip",
            mimetype="application/zip",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
