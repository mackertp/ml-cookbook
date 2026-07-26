"""
Flask application to teach genomics core concepts and to perform gene sequence analysis.

This application has hit a point, where it would benefit greatly from being refactored into a framework 
like Django - with a robust database and better scalablility.

@author: Preston Mackert
"""

# ------------------------------------------------------------------------------------- #
# libraries
# ------------------------------------------------------------------------------------- #

from __future__ import annotations
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from .analysis import (
    analyze_pair,
    list_presets,
    list_research_areas,
    load_preset_reference,
    load_preset_sample,
    parse_sequence_text,
)
# set application directory
APP_DIR = Path(__file__).resolve().parent

# ------------------------------------------------------------------------------------- #
# create the flask application that will be called in launch.py
# ------------------------------------------------------------------------------------- #

def create_app() -> Flask:
    app = Flask(
        # initial flask application definition
        __name__,
        # frontend design system connection
        template_folder=str(APP_DIR / "templates"),
        static_folder=str(APP_DIR / "static"),
        static_url_path="/static",
    )

    # index route
    @app.get("/")
    def index():
        return render_template(
            "index.html",
            presets=list_presets(),
            research_areas=list_research_areas(),
        )

    # sequencing process / animation route
    @app.get("/sequencing")
    def sequencing():
        return render_template("sequencing.html")

    # API routes
    @app.get("/api/presets")
    def presets():
        return jsonify(list_presets())

    @app.get("/api/research-areas")
    def research_areas():
        return jsonify(list_research_areas())

    @app.post("/api/analyze")
    def analyze():
        try:
            preset_id = (request.form.get("preset_id") or "").strip() or None
            use_demo_sample = request.form.get("use_demo_sample") == "true"

            if preset_id:
                ref_header, ref_seq, preset_id = load_preset_reference(preset_id)
            elif "reference_file" in request.files and request.files["reference_file"].filename:
                raw = request.files["reference_file"].read().decode("utf-8", errors="replace")
                ref_header, ref_seq = parse_sequence_text(raw)
            elif request.form.get("reference_text", "").strip():
                ref_header, ref_seq = parse_sequence_text(request.form["reference_text"])
            else:
                return jsonify({"error": "Provide a reference preset, file, or pasted sequence."}), 400

            if use_demo_sample and preset_id:
                sample_header, sample_seq = load_preset_sample(preset_id)
            elif "sample_file" in request.files and request.files["sample_file"].filename:
                raw = request.files["sample_file"].read().decode("utf-8", errors="replace")
                sample_header, sample_seq = parse_sequence_text(raw)
            elif request.form.get("sample_text", "").strip():
                sample_header, sample_seq = parse_sequence_text(request.form["sample_text"])
            else:
                return jsonify({"error": "Upload or paste a sample sequence (or use the demo sample)."}), 400

            result = analyze_pair(ref_header, ref_seq, sample_header, sample_seq, preset_id)
            return jsonify(result)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:  # noqa: BLE001 — surface unexpected errors to the UI
            return jsonify({"error": f"Analysis failed: {exc}"}), 500

    return app

# ------------------------------------------------------------------------------------- #
# call the app and run when server is invoked from launch.py
# ------------------------------------------------------------------------------------- #

app = create_app()
def main() -> None:
    app.run(debug=True, port=5050)
