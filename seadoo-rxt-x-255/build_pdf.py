#!/usr/bin/env python3
"""Render the Arman supercharger walkthrough HTML into a phone-friendly PDF.

Usage:  python3 build_pdf.py
Requires: weasyprint  (pip install weasyprint)
"""
import os
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "arman-supercharger-walkthrough.html")
OUT = os.path.join(HERE, "Arman-Supercharger-Walkthrough.pdf")


def main():
    HTML(filename=SRC).write_pdf(OUT)
    size_kb = os.path.getsize(OUT) / 1024
    print(f"Built {OUT}  ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
